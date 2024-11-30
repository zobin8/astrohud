# AstroHud

Tool for creating and charting astral data.

Project is still in development. The CLI tool and image rendering are generally complete. A web API is planned for future development.

| Feature | Status |
|---------|--------|
| Basic ephemeris | ✔️ |
| Tropical/Sideareal Splitting | ✔️ |
| IAU Splitting | ✔️ |
| Planetarium (3D) Splitting | ✔️ |
| Wheel Chart Rendering | ✔️ |
| Star Chart Rendering |  |
| Web API |  |
| Web Frontend |  |
| Date Search |  |

Astro symbols used in this project: https://suberic.net/~dmm/astro

## Install

1. Clone this repo and its submodules.
2. Download the ephemeris file for Eris to `submodules/swisseph/ephe/ast136/s136199.se1`.
3. Install all PIP requirements from `requirements.txt`
4. Run `python3 -m astrohud --help` to verify installation
