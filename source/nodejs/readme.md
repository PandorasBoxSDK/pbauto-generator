## Requirements
* node.js
* Pandora's Box Manager with web server enabled

## Installation
```
npm install pbauto-nodejs-http
```

## Usage
Create a new PBAuto instance by passing in IP and Port of the Pandoras Box Web Server Service.

```javascript
var PBAuto = require('pbauto-nodejs-http');

var connection = new PBAuto("2.0.0.1", 6214);
```

You can then proceed to use all api functions. You can provide an optional callback to retrieve the response values.

```javascript
connection.getSelectedDeviceCount( function(response){
	// response.http holds the HTTP status code
	// response.code holds the Automation Command code
	// both are considered for the convenience value response.ok
	if(response.ok) // check if request was successful
	{
		// response values are automatically parsed and put on the response object
		console.log(response);
	}
});
```
Response (Raw JSON)
```json
{
	http: 200,
	ok: true,
	code: 81,
	selectedDevicesCount: 2
}
```