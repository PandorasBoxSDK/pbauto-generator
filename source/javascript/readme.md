## Usage
You can call the API on the PBAuto object.

```javascript
PBAuto.applyView(1);
```

If you need to retrieve values, you can add an optional callback as the last parameter.

```javascript
connection.getSelectedDeviceCount( function(response){
	// response.http holds the HTTP status code
	// response.code holds the Automation Command code
	// both are considered for the convenience value response.ok
	if(response.ok) // check if request was successful
	{
		// response values are automatically parsed and put on the response object
		console.log(response.selectedDevicesCount);
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