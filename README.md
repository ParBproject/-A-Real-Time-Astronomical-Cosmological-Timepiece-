# Cosmic Clock

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](requirements.txt)
[![Streamlit](https://img.shields.io/badge/Streamlit-Interactive_App-FF4B4B?logo=streamlit&logoColor=white)](app.py)
[![Astronomy](https://img.shields.io/badge/Astronomy-Skyfield_%7C_Astropy-5b5bd6)](src/astronomy.py)

A real-time astronomical and cosmological timepiece that connects the sky above the user with the 13.8-billion-year history of the universe.

## Product Experience

Cosmic Clock presents time at two scales:

1. **Immediate sky:** current positions of the Sun, Moon, planets, and bright stars for a selected location.
2. **Cosmic scale:** the history of the universe compressed into an interactive calendar and timeline.

## Application Preview

### Live Cosmic Dashboard

![Cosmic Clock home page](assets/screenshots/01_home.png)

### Real-Time Sky Map

![Real-time all-sky map](assets/screenshots/02_sky_clock.png)

### Cosmic Timeline

![Interactive cosmological timeline](assets/screenshots/03_cosmic_timeline.png)

### Personal Scale

![Personal place in cosmic history](assets/screenshots/04_personal_scale.png)

## Features

- Stereographic all-sky projection for a selected observer location
- Sun, Moon, and planet position calculations
- Moon phase, illumination, and rise/set context
- Bright-star catalogue with altitude, azimuth, magnitude, and constellation
- Sidereal and local solar time
- Date/time override for historical or future sky views
- 43-event cosmological timeline with category filters
- Cosmic Calendar scaling from the Big Bang to the present
- Personalized comparison between a human lifetime and cosmic time

## Technical Architecture

| Layer | Implementation |
|---|---|
| Astronomy | Skyfield, Astropy, JPL DE421 ephemeris |
| Timeline | Custom cosmic-scaling and event logic |
| Visualization | Plotly |
| Application | Multi-page Streamlit |
| Data | JSON catalogues for events and bright stars |

## Run Locally

~~~bash
git clone https://github.com/ParBproject/-A-Real-Time-Astronomical-Cosmological-Timepiece-.git
cd ./-A-Real-Time-Astronomical-Cosmological-Timepiece-

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
~~~

On first launch, Skyfield may download the DE421 ephemeris file and cache it locally.

## Repository Structure

~~~text
.
├── app.py
├── pages/
│   ├── 1_Sky_Clock.py
│   ├── 2_Cosmic_Timeline.py
│   └── 3_About.py
├── src/
│   ├── astronomy.py
│   ├── timeline.py
│   ├── visuals.py
│   └── utils.py
├── assets/
│   ├── events.json
│   └── constellations.json
└── requirements.txt
~~~

## Skills Demonstrated

Scientific Python, astronomical coordinate calculations, external scientific datasets, interactive visualization, multi-page application design, data modelling, numerical scaling, and accessible science communication.

## Accuracy Note

The primary calculations use established astronomy libraries and the DE421 ephemeris. The application includes a simplified fallback mode when ephemeris resources are unavailable; fallback results are suitable for visualization rather than precision observing.
