# pyspectrum

Python client for the DX Spectrum API

## Installation

The client it not yet available on PyPI and so must be installed directly from
GitHub:

```text
pip install git+https://github.com/johnrdowson/py-spectrum
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

# Specify attributes to retrieve. These can be using the hex code or using the
# attribute name (See attributes.py file for a list of named attributes
# supported)
attrs = ["network_address", "serial_number", 0x1102E]

# Fetch the complete list of devices
resp = spectrum.get_devices()

# Process the data or optinally dump the result to a CSV
spectrum.to_csv(resp.result, "inventory.csv", order_by="model_name") 
```

The Spectrum API allows a filter to be provided in the payload XML. The
`pyspectrum` client is able to parse a string expression and translate it to a
dictionary object which will finally be rendered to XML using a `Jinja`
template. 

```python
from pyspectrum import SpectrumClient
spectrum = SpectrumClient()

# Simple expression

resp = spectrum.get_models(filters="device_type ~ Juniper")

# Supports grouping multiple filters

group_expr = """
and (
    model_type_name = Rtr_Cisco,
    condition <= 2
)
"""

resp = spectrum.get_models(filters=group_expr)
```

## Environment Variabes

The following environment variables can be used so that you do no need to 
provide them in your program:

- `SPECTRUM_URL` - Spectrum OneClick server URL
- `SPECTRUM_USERNAME` - Login username
- `SPECTRUM_PASSWORD` - Login password

## Attributes

The Spectrum API refers to attributes using their ID, which is in hex format
(e.g. `model_handle` is `0x129fa`). The client contains a number of attribute
name to ID mappings which make requesting attributes, applying filters, and
parsing the response much more readable.

For example, the attribute `sys_location` can be request by either the name or
the ID (`0x1102e`):

```python
# By ID (can be string or integer)
resp = spectrum.get_devices(attrs=[0x1102e])

# By name
resp = spectrum.get_devices(attrs=["sys_location"])
```

The response data in `resp.result` will be (by default) populated with the
attribute name:

```json
{
    "model_handle": "0x10a3b11",
    "model_name": "LAB_RTR",
    "model_type_name": "Rtr_Cisco",
    "sys_location": "Rack 1A, Network Lab, Head Office, London",
},
```

To disable the response parser resolving attribute IDs to name, use the
parameter `resolve_attrs=False` in the method call.

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
