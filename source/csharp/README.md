## Requirements
* .Net 4.0 (may work with 2/3)

## Installation
The code is currently distributed as a single file. Either copy the code right into your project files or add **PandorasBox.cs** to your project

## Usage
The PBAuto class expects a connector in the constructor. Currently there is only the TCP connector.

```csharp
ip = "127.0.0.1"
domain = 0

connector = Tcp(ip, domain)
pb = PBAuto(connector)

// alternatively use the convenience function
pb = PBAuto.ConnectTcp(ip, domain)
```

You can then proceed to use all api functions. All functions return a struct that contains the members **ok**, **code** and **error**.

Use **ok** to check if the request was successful. **error** will return the error id if something went wrong.

If there are values to be returned then the struct will contain them as members as well.

```csharp
pb.GetSelectedDeviceCount()
// returns a GetSelectedDeviceCountResult
// .selectedDevicesCount = 2
// .ok = true
// .code = 81
// .error = undefined (because ok is true)
```