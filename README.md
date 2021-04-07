# pyspectrum

Python client for the DX Spectrum API

## Installation

The client it not yet available on PyPI and so must be installed directly from
GitHub:

```text
pip install git+https//github.com/johnrdowson/py-spectrum
```

## Quick Start

```python
from pyspectrum import SpectrumClient

# Create a client instance. With no parameters, it will use the environment
# variables listed below
spectrum = SpectrumClient()

# Alternatively, create instance with parameters:
spectrum = SpectrumClient(
    base_url='https://oneclick:8443',
    username='admin',
    password='P@55w0rd'
)

# Fetch the complete list of devices
all_devices = spectrum.fetch_all_devices()
```

## Environment Variabes

The following environment variables can be used so that you do no need to 
provide them in your program:

- `SPECTRUM_URL` - Spectrum OneClick server URL
- `SPECTRUM_USERNAME` - Login username
- `SPECTRUM_PASSWORD` - Login password
