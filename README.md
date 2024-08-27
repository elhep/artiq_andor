# Andor (Oxford Instruments) iXion Ultra 897

## Requirements

- Windows host (tested on W11)
- Andor SDK2 installed (tested with 2.104.30065.0)
- Python 3.8 (required due to SDK numpy 1.19 requirement)

## Installation

1. You can easily install Python 3.8 with [pyenv-win](https://github.com/pyenv-win/pyenv-win).
2. Create virtual environment with Python 3.8
3. Install pyAndorSDK2 in venv by navigating to SDK installation location and than `python\pyandorsdk2` and executing `python -m pip install .`.
4. Install sipyco: `python -m pip install git+https://github.com/m-labs/sipyco`.

