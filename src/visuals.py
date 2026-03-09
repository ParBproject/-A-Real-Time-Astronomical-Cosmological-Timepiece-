"""
visuals.py — Plotly figure generators for Cosmic Clock.

All visual generation is centralized here for clean separation of concerns.
Design philosophy: dark, cosmic aesthetic with careful use of color and glow effects.
"""

import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional
import json
import os


# ─── Color palette ────────────────────────────────────────────────────────────

COSMIC_BG = "#03030f"
PANEL_BG  = "#07071a"
GRID_COLOR = "#1a1a3e"
TEXT_COLOR = "#c8d4e8"
ACCENT1 = "#4FC3F7"   # ice blue
ACCENT2 = "#CE93D8"   # soft violet
ACCENT3 = "#81C784"   # sage green
ACCENT4 = "#FFD54F"   # warm gold


# ─── Sky Map (stereographic projection) ──────────────────────────────────────

def build_sky_map(
    planets: list[dict],
    stars: list[dict],
    sun: dict,
    moon: dict,
    sky_state: dict,
    lat: float = 45.0,
    show_planets: bool = True,
    show_stars: bool = True,
    show_labels: bool = True,
) -> go.Figure:
    """
    Build a full-sky stereographic projection centered on the zenith.
    Alt=90° → center, Alt=0° → edge, Az=0° (N) → top.
    """

    def altaz_to_xy(alt, az):
        """Stereographic: radius = cos(alt), angle = az from N clockwise."""
        r = np.cos(np.radians(max(0, alt)))
        az_rad = np.radians(az)
        x = r * np.sin(az_rad)
        y = r * np.cos(az_rad)
        return x, y

    fig = go.Figure()

    # ── Background sky gradient circles ──────────────────────────────────────
    # Draw concentric altitude rings
    theta = np.linspace(0, 2 * np.pi, 200)
    for alt_ring in [0, 30, 60, 90]:
        r = np.cos(np.radians(alt_ring))
        x_ring = r * np.cos(theta)
        y_ring = r * np.sin(theta)
        fig.add_trace(go.Scatter(
            x=x_ring, y=y_ring,
            mode="lines",
            line=dict(color=GRID_COLOR, width=0.5 if alt_ring != 0 else 1.5),
            hoverinfo="skip",
            showlegend=False,
        ))
        if alt_ring < 90 and show_labels:
            fig.add_annotation(
                x=0, y=r + 0.02,
                text=f"{alt_ring}°",
                showarrow=False,
                font=dict(color="#2a2a5e", size=9),
            )

    # Cardinal direction markers
    for az_mark, label in [(0, "N"), (90, "E"), (180, "S"), (270, "W")]:
        x, y = altaz_to_xy(0, az_mark)
        fig.add_annotation(
            x=x * 1.08, y=y * 1.08,
            text=label,
            showarrow=False,
            font=dict(color=ACCENT1, size=13, family="monospace"),
        )

    # Azimuth spokes every 45°
    for az_spoke in range(0, 360, 45):
        x0, y0 = altaz_to_xy(0, az_spoke)
        fig.add_trace(go.Scatter(
            x=[0, x0], y=[0, y0],
            mode="lines",
            line=dict(color=GRID_COLOR, width=0.4, dash="dot"),
            hoverinfo="skip",
            showlegend=False,
        ))

    # ── Bright stars ──────────────────────────────────────────────────────────
    if show_stars and stars:
        star_x, star_y, star_text, star_sizes, star_colors = [], [], [], [], []
        for star in stars:
            if star.get("above_horizon", False):
                x, y = altaz_to_xy(star["alt"], star["az"])
                star_x.append(x)
                star_y.append(y)
                star_text.append(
                    f"<b>{star['name']}</b><br>"
                    f"Alt: {star['alt']:.1f}°  Az: {star['az']:.1f}°<br>"
                    f"Mag: {star['mag']:.2f}  ({star['constellation']})"
                )
                # Size inversely proportional to magnitude
                sz = max(3, 10 - star["mag"] * 3)
                star_sizes.append(sz)
                star_colors.append(star.get("color", "#FFFFFF"))

        if star_x:
            fig.add_trace(go.Scatter(
                x=star_x, y=star_y,
                mode="markers",
                marker=dict(
                    size=star_sizes,
                    color=star_colors,
                    opacity=sky_state["star_opacity"],
                    line=dict(width=0),
                ),
                text=star_text,
                hovertemplate="%{text}<extra></extra>",
                name="Stars",
                showlegend=False,
            ))

    # ── Sun ───────────────────────────────────────────────────────────────────
    sun_x, sun_y = altaz_to_xy(sun["alt"], sun["az"])
    if sun["above_horizon"]:
        fig.add_trace(go.Scatter(
            x=[sun_x], y=[sun_y],
            mode="markers+text",
            marker=dict(size=24, color="#FFD700", symbol="circle",
                        line=dict(color="#FFF176", width=2)),
            text=["☀"],
            textfont=dict(size=18),
            textposition="middle center",
            hovertemplate=(
                f"<b>Sun</b><br>"
                f"Alt: {sun['alt']:.1f}°  Az: {sun['az']:.1f}°<br>"
                f"RA: {sun['ra']:.2f}h  Dec: {sun['dec']:.1f}°<extra></extra>"
            ),
            name="Sun",
            showlegend=False,
        ))
    else:
        # Show below horizon indicator
        fig.add_annotation(
            x=0, y=-0.92,
            text="☀ Sun below horizon",
            showarrow=False,
            font=dict(color="#FFD700", size=11),
        )

    # ── Moon ──────────────────────────────────────────────────────────────────
    moon_x, moon_y = altaz_to_xy(moon["alt"], moon["az"])
    moon_icon = _moon_icon(moon["phase"])

    if moon["above_horizon"]:
        fig.add_trace(go.Scatter(
            x=[moon_x], y=[moon_y],
            mode="markers+text",
            marker=dict(size=20, color="#E8E8D0", symbol="circle",
                        line=dict(color="#C0C0B0", width=1)),
            text=[moon_icon],
            textfont=dict(size=16),
            textposition="middle center",
            hovertemplate=(
                f"<b>Moon</b> {moon['phase_name']}<br>"
                f"Illumination: {moon['illumination']:.0f}%<br>"
                f"Alt: {moon['alt']:.1f}°  Az: {moon['az']:.1f}°<extra></extra>"
            ),
            name="Moon",
            showlegend=False,
        ))

    # ── Planets ───────────────────────────────────────────────────────────────
    if show_planets and planets:
        for p in planets:
            if not p.get("visible", False):
                continue
            px_, py = altaz_to_xy(p["alt"], p["az"])
            fig.add_trace(go.Scatter(
                x=[px_], y=[py],
                mode="markers+text",
                marker=dict(
                    size=p["size"],
                    color=p["color"],
                    symbol="circle",
                    line=dict(color="white", width=0.5),
                    opacity=0.9,
                ),
                text=[p["symbol"]],
                textfont=dict(size=10, color="white"),
                textposition="top center",
                hovertemplate=(
                    f"<b>{p['name']}</b> {p['symbol']}<br>"
                    f"Alt: {p['alt']:.1f}°  Az: {p['az']:.1f}°<br>"
                    f"Distance: {p['distance_au']:.2f} AU<extra></extra>"
                ),
                name=p["name"],
                showlegend=False,
            ))
            if show_labels:
                fig.add_annotation(
                    x=px_, y=py + 0.04,
                    text=p["name"],
                    showarrow=False,
                    font=dict(color=p["color"], size=9),
                )

    # ── Outer horizon circle ──────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=np.cos(theta), y=np.sin(theta),
        mode="lines",
        line=dict(color=ACCENT1, width=2),
        fill="toself",
        fillcolor=f"rgba(0,0,15,{0.4 * (1 - sky_state['star_opacity'])})",
        hoverinfo="skip",
        showlegend=False,
    ))

    fig.update_layout(
        plot_bgcolor=COSMIC_BG,
        paper_bgcolor=COSMIC_BG,
        xaxis=dict(
            range=[-1.15, 1.15], visible=False,
            scaleanchor="y", scaleratio=1,
        ),
        yaxis=dict(range=[-1.15, 1.15], visible=False),
        margin=dict(l=10, r=10, t=10, b=10),
        height=520,
        hoverlabel=dict(bgcolor=PANEL_BG, font_color=TEXT_COLOR, bordercolor=ACCENT1),
    )

    return fig


def _moon_icon(phase: float) -> str:
    icons = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
    return icons[int((phase * 8) % 8)]


# ─── Cosmic Timeline ──────────────────────────────────────────────────────────

def build_cosmic_timeline(
    events: list[dict],
    scale_name: str = "Cosmic Year",
    zoom_range: Optional[tuple] = None,
    highlight_categories: Optional[list] = None,
    user_birth_year: Optional[int] = None,
) -> go.Figure:
    """
    Build an interactive horizontal timeline Plotly figure.
    x-axis: fraction of universe history (0=Big Bang, 1=now).
    """
    from src.timeline import age_to_scale, CATEGORY_COLORS, compute_personal_stats

    # Filter events by category
    if highlight_categories:
        filtered = [e for e in events if e.get("category") in highlight_categories]
    else:
        filtered = events

    fig = go.Figure()

    # ── Main timeline bar ─────────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 0],
        mode="lines",
        line=dict(
            color="rgba(79,195,247,0.25)",
            width=6,
        ),
        hoverinfo="skip",
        showlegend=False,
    ))

    # ── Gradient bars for cosmic eras ─────────────────────────────────────────
    eras = [
        (0.0,  0.032,  "rgba(255,107,53,0.08)",  "Cosmic Dawn"),
        (0.032, 0.27,  "rgba(255,215,0,0.05)",   "First Galaxies"),
        (0.27,  0.667, "rgba(100,181,246,0.05)",  "Galaxy Evolution"),
        (0.667, 0.967, "rgba(102,187,106,0.07)",  "Earth & Life"),
        (0.967, 1.0,   "rgba(255,255,255,0.06)",  "Human Era"),
    ]
    for x0, x1, color, label in eras:
        fig.add_vrect(x0=x0, x1=x1, fillcolor=color, line_width=0)

    # ── Events ────────────────────────────────────────────────────────────────
    # Stagger events vertically to avoid overlap
    y_positions = {}
    sorted_events = sorted(filtered, key=lambda e: e.get("pct_from_start", 0))
    used_positions = {}

    for ev in sorted_events:
        pos = age_to_scale(ev["age_years"], scale_name)
        x = pos["fraction"]
        cat = ev.get("category", "cosmological")

        # Stagger
        bucket = int(x * 30)
        y_level = used_positions.get(bucket, 0)
        used_positions[bucket] = (y_level + 1) % 4
        y = 0.15 + y_level * 0.22

        color = CATEGORY_COLORS.get(cat, "#aaaaaa")

        fig.add_trace(go.Scatter(
            x=[x, x], y=[0, y],
            mode="lines",
            line=dict(color=f"rgba{_hex_to_rgba(color, 0.4)}", width=1, dash="dot"),
            hoverinfo="skip",
            showlegend=False,
        ))

        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode="markers+text",
            marker=dict(size=16, color=PANEL_BG,
                        line=dict(color=color, width=2)),
            text=[ev.get("icon", "●")],
            textfont=dict(size=12),
            textposition="middle center",
            hovertemplate=(
                f"<b>{ev['name']}</b><br>"
                f"{ev.get('description', '')}<br><br>"
                f"<i>{_years_label(ev['age_years'])}</i><br>"
                f"Cosmic date: {age_to_scale(ev['age_years'], scale_name)['display']}"
                f"<extra></extra>"
            ),
            name=ev["name"],
            showlegend=False,
        ))

    # ── "You Are Here" marker ─────────────────────────────────────────────────
    fig.add_vline(x=1.0, line_color="rgba(255,255,255,0.8)", line_width=2,
                  line_dash="dash")
    fig.add_annotation(
        x=1.0, y=1.05,
        text="⬆ NOW",
        showarrow=False,
        font=dict(color="white", size=11, family="monospace"),
        xanchor="center",
    )

    # ── Personal marker ───────────────────────────────────────────────────────
    if user_birth_year:
        stats = compute_personal_stats(user_birth_year)
        birth_pos = age_to_scale(stats["age_years"], scale_name)
        fig.add_vline(
            x=birth_pos["fraction"],
            line_color="rgba(206,147,216,0.7)",
            line_width=1.5,
            line_dash="dot",
        )
        fig.add_annotation(
            x=birth_pos["fraction"],
            y=-0.25,
            text=f"🎂 Born {user_birth_year}",
            showarrow=False,
            font=dict(color=ACCENT2, size=9),
            xanchor="center",
        )

    # ── X-axis tick labels ────────────────────────────────────────────────────
    tick_vals = np.linspace(0, 1, 14)
    tick_texts = []
    for v in tick_vals:
        years_ago = (1 - v) * 13.8e9
        if years_ago > 1e9:
            tick_texts.append(f"{years_ago/1e9:.1f}B")
        elif years_ago > 1e6:
            tick_texts.append(f"{years_ago/1e6:.0f}M")
        elif years_ago > 1e3:
            tick_texts.append(f"{years_ago/1e3:.0f}K")
        elif years_ago < 1:
            tick_texts.append("Now")
        else:
            tick_texts.append(f"{years_ago:.0f}")

    # Apply zoom range
    x_range = zoom_range if zoom_range else [0, 1.02]

    fig.update_layout(
        plot_bgcolor=COSMIC_BG,
        paper_bgcolor=COSMIC_BG,
        xaxis=dict(
            range=x_range,
            tickvals=tick_vals.tolist(),
            ticktext=tick_texts,
            tickfont=dict(color=TEXT_COLOR, size=9, family="monospace"),
            gridcolor=GRID_COLOR,
            zeroline=False,
            title=dict(text="Universe History (years ago)", font=dict(color=TEXT_COLOR, size=11)),
        ),
        yaxis=dict(
            range=[-0.4, 1.3],
            visible=False,
        ),
        margin=dict(l=10, r=10, t=20, b=60),
        height=380,
        hoverlabel=dict(bgcolor=PANEL_BG, font_color=TEXT_COLOR, bordercolor=ACCENT1),
        dragmode="pan",
    )

    return fig


def _hex_to_rgba(hex_color: str, alpha: float) -> tuple:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r, g, b, alpha)


def _years_label(years: float) -> str:
    if years == 0:
        return "Present moment"
    elif years < 1e3:
        return f"{years:,.0f} years ago"
    elif years < 1e6:
        return f"{years/1e3:,.1f} thousand years ago"
    elif years < 1e9:
        return f"{years/1e6:,.0f} million years ago"
    else:
        return f"{years/1e9:.3f} billion years ago"


# ─── Cosmic Calendar wheel ────────────────────────────────────────────────────

def build_cosmic_calendar_wheel(events: list[dict]) -> go.Figure:
    """
    Build a radial/polar chart showing the Cosmic Calendar as a clock face.
    Jan 1 = top, Dec 31 = almost back to top.
    """
    from src.timeline import age_to_cosmic_year, CATEGORY_COLORS

    fig = go.Figure()

    # Month dividers
    for month in range(12):
        angle = month / 12 * 360
        r_max = 1.0
        x = r_max * np.sin(np.radians(angle))
        y = r_max * np.cos(np.radians(angle))
        fig.add_trace(go.Scatter(
            x=[0, x], y=[0, y],
            mode="lines",
            line=dict(color=GRID_COLOR, width=1),
            hoverinfo="skip",
            showlegend=False,
        ))

    # Month labels
    month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    for i, name in enumerate(month_names):
        angle = (i + 0.5) / 12 * 360
        x = 1.15 * np.sin(np.radians(angle))
        y = 1.15 * np.cos(np.radians(angle))
        fig.add_annotation(x=x, y=y, text=name,
                           showarrow=False,
                           font=dict(color=TEXT_COLOR, size=9, family="monospace"))

    # Outer ring
    theta = np.linspace(0, 2 * np.pi, 500)
    fig.add_trace(go.Scatter(
        x=np.cos(theta), y=np.sin(theta),
        mode="lines",
        line=dict(color=f"rgba(79,195,247,0.3)", width=1.5),
        hoverinfo="skip", showlegend=False,
    ))

    # Events
    for ev in events:
        cal = age_to_cosmic_year(ev["age_years"])
        angle_deg = cal["fraction"] * 360
        r = 0.75
        x = r * np.sin(np.radians(angle_deg))
        y = r * np.cos(np.radians(angle_deg))

        cat = ev.get("category", "cosmological")
        color = CATEGORY_COLORS.get(cat, "#aaaaaa")

        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode="markers+text",
            marker=dict(size=14, color=PANEL_BG,
                        line=dict(color=color, width=2)),
            text=[ev.get("icon", "●")],
            textfont=dict(size=10),
            textposition="middle center",
            hovertemplate=(
                f"<b>{ev['name']}</b><br>"
                f"{ev.get('description', '')}<br>"
                f"Cosmic date: {cal['display']}<extra></extra>"
            ),
            showlegend=False,
        ))

    # "NOW" hand
    fig.add_trace(go.Scatter(
        x=[0, 0], y=[0, 0.98],
        mode="lines",
        line=dict(color="white", width=2),
        hoverinfo="skip", showlegend=False,
    ))
    fig.add_annotation(x=0, y=1.02, text="NOW ▼", showarrow=False,
                       font=dict(color="white", size=10, family="monospace"))

    fig.update_layout(
        plot_bgcolor=COSMIC_BG,
        paper_bgcolor=COSMIC_BG,
        xaxis=dict(range=[-1.3, 1.3], visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(range=[-1.3, 1.3], visible=False),
        margin=dict(l=10, r=10, t=10, b=10),
        height=480,
        hoverlabel=dict(bgcolor=PANEL_BG, font_color=TEXT_COLOR, bordercolor=ACCENT1),
    )
    return fig


# ─── Planet distance chart ────────────────────────────────────────────────────

def build_planet_visibility_chart(planets: list[dict]) -> go.Figure:
    """Horizontal bar chart showing which planets are visible tonight."""
    names = [p["name"] for p in planets]
    alts = [p["alt"] for p in planets]
    colors = [p["color"] if p["alt"] > 0 else "#333355" for p in planets]

    fig = go.Figure(go.Bar(
        x=alts,
        y=names,
        orientation="h",
        marker_color=colors,
        text=[f"{p['symbol']} {p['alt']:.1f}°" for p in planets],
        textposition="auto",
        hovertemplate="<b>%{y}</b><br>Altitude: %{x:.1f}°<extra></extra>",
    ))

    fig.add_vline(x=0, line_color=ACCENT1, line_width=1.5, line_dash="dash")
    fig.add_annotation(
        x=5, y=7.5, text="Horizon", showarrow=False,
        font=dict(color=ACCENT1, size=9),
    )

    fig.update_layout(
        plot_bgcolor=COSMIC_BG,
        paper_bgcolor=COSMIC_BG,
        xaxis=dict(
            title="Altitude (°)", range=[-90, 90],
            tickfont=dict(color=TEXT_COLOR, size=9),
            gridcolor=GRID_COLOR,
            zeroline=False,
        ),
        yaxis=dict(tickfont=dict(color=TEXT_COLOR, size=10), gridcolor=GRID_COLOR),
        margin=dict(l=80, r=20, t=20, b=40),
        height=280,
        font=dict(color=TEXT_COLOR),
    )
    return fig


# ─── Moon phase diagram ───────────────────────────────────────────────────────

def build_moon_phase_diagram(phase: float, illumination: float) -> go.Figure:
    """Simple moon phase visualization."""
    theta_full = np.linspace(0, 2 * np.pi, 200)
    x_full = np.cos(theta_full)
    y_full = np.sin(theta_full)

    fig = go.Figure()

    # Full moon circle (dark)
    fig.add_trace(go.Scatter(
        x=x_full, y=y_full,
        fill="toself",
        fillcolor="#1a1a2e",
        line=dict(color="#555577", width=1),
        hoverinfo="skip", showlegend=False,
    ))

    # Illuminated portion
    phase_angle = phase * 360
    # Draw lit portion based on phase
    if phase <= 0.5:
        # Waxing: right half lit, left half progressively
        stretch = np.cos(np.radians(phase_angle * 2 - 180))  # -1 to +1
        theta_half = np.linspace(-np.pi / 2, np.pi / 2, 100)
        x_right = np.cos(theta_half)
        y_right = np.sin(theta_half)
        x_left = stretch * np.abs(np.cos(theta_half))
        x_lit = np.concatenate([x_right, x_left[::-1]])
        y_lit = np.concatenate([y_right, y_right[::-1]])
    else:
        # Waning: left half lit, right progressively lost
        stretch = np.cos(np.radians((phase_angle - 180) * 2))
        theta_half = np.linspace(np.pi / 2, 3 * np.pi / 2, 100)
        x_left = np.cos(theta_half)
        y_left = np.sin(theta_half)
        x_right = stretch * np.abs(np.cos(theta_half))
        x_lit = np.concatenate([x_left, x_right[::-1]])
        y_lit = np.concatenate([y_left, y_left[::-1]])

    fig.add_trace(go.Scatter(
        x=x_lit, y=y_lit,
        fill="toself",
        fillcolor="#E8E8D0",
        line=dict(color="rgba(220,220,200,0.5)", width=0.5),
        hoverinfo="skip", showlegend=False,
    ))

    fig.update_layout(
        plot_bgcolor=COSMIC_BG,
        paper_bgcolor=COSMIC_BG,
        xaxis=dict(range=[-1.3, 1.3], visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(range=[-1.3, 1.3], visible=False),
        margin=dict(l=5, r=5, t=5, b=5),
        height=160,
        width=160,
    )
    return fig
