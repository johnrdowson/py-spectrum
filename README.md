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

## Attributes

The Spectrum API refers to attributes using their ID, which is in hex format
(e.g. `model_handle` is `0x129fa`). The client is contains a number of attribute
name to ID mappings which make requesting attributes, applying filters, and
parsing the response much more readable.

For example, the attribute `sys_location` can be request by either the name or
the ID (`0x1102e`):

```python
# By ID (can be string or integer)
resp = spectrum.fetch_all_devices(attrs=[0x1102e])

# By name
resp = spectrum.fetch_all_devices(attrs=["sys_location"])
```

The response data will be (by default) populated with the named attribute name:

```json
{
    "model_handle": "0x10a3b11",
    "model_name": "LAB_RTR",
    "model_type_name": "Rtr_Cisco",
    "sys_location": "Rack 1A, Network Lab, Head Office, London",
},
```

To disable the response parser resolving attribute IDS to name, use the
parameter `resolve_attrs=False`.

The base attributes which are requested by default are:

- `model_handle`
- `model_name`
- `model_type_name`

A list of attributes that support using the name can be viewed on the
`attributes.py` file, or programmatically as follows:

```python
from pyspectrum.attributes import SpectrumModelAttributes
list(SpectrumModelAttributes)
```

## Filters

To do.