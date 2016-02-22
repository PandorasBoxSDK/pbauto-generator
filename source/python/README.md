## Requirements
* Python (tested on 3, 2 should work as well)
* coolux Pandoras Box

## Installation
The code is currently distributed as a single file. There might be a pip package in the future.

## Usage
The PBAuto class expects a connector in the constructor. Currently there is only the TCP connector.

```python
import pbauto

# Use Tcp Connector
ip = "127.0.0.1"
domain = 0

connector = Tcp(ip, domain) # domain is optional
pb = pbauto.PBAuto(connector)

# ... or use the convenience function
pb = pbauto.PBAuto.connect_tcp(ip, domain)
```

You can then proceed to use all api functions.

```python
pb.getSelectedDeviceCount()
# returns {'selectedDevicesCount': 2, 'ok': True, 'code': 81}
```