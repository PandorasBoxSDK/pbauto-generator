# Abstract
The following document describes the data types, message formats and principles that are required to communicate with Pandoras Box.

## Data Types
Pandoras Box Automation uses data types derived from C++ data types. Everything is transmitted in **network byte order**

#### bool
A bool is represented with an 8-bit integer. A value of 1 is “true” and a value of 0 is “false”. No other values are permitted.

#### byte
8-bit unsigned integer

#### short
16-bit unsigned integer (Endianess = network byte order = Big Endian)

#### int
32-bit signed integer (Endianess = network byte order = Big Endian)

#### int64 (rarely used)
64-bit signed integer (Endianess = network byte order = Big Endian)

#### double
IEEE 754 - double floating point (64-bit)

#### string narrow
The string data types are used to transmit text. 

They are compound data types that consist of:
1. The text character count
2. The text data (so the text itself)

The character count is transmitted in an short (as defined above). The text data encoding depends on the string type (narrow or wide).

See right column for details.   The text data encoding used in the narrow version is ASCII. Each character is encoded in one byte.

The underlying C++ type is char (8-bit)

#### string wide
The text data encoding used in the wide version is UCS-2.  Each character is encoded in one short (as defined above). It is mostly compatible with UTF-16-BE (over 95%).

The underlying C++ type is wchar_t (which is a 16-bit character in Pandoras Box)

#### byte buffer
Byte buffers are used to transmit binary data, such as image data or vectors. They are basically an array of bytes.

The byte buffer is a compound data type that contains:
1. The length of the data encoded in a integer (as defined above)
2. The data bytes each encoded as bytes

#### int buffer
Int buffers are used to transmit multiple integers.

The int buffer is a compound data type that contains:
1. The length of the data encoded in a integer (as defined above)
2. The data bytes each encoded as integers

#### enumerations (optional)
Pandoras Automation also uses enumerations that contain constants for frequently used values. These types are not part of the protocol since they are transmitted using the base data types defined above. They are only used as a convenience for the developers.

## Message Structure
#### TCP/UDP
All TCP and UDP Pandoras Automation packets consist of a **header** + **data**. The **header** is used in both directions (PB->client, App->client).
#### HTTP
HTTP does not require any headers since they are provided by the HTTP protocol.

### Header (17 bytes)
#### Identifier (4 bytes)
A constant value that denotes the beginning of a Pandoras Box Automation Message.
**0x50 0x42 0x41 0x55** (or ‘**PBAU**’ ASCII encoded)

#### Version (1 byte)
The protocol version, constant value of **0x01**

#### Domain (integer)
The Domain ID Pandoras Box operates on, defaults to **0x00**

#### Message Length (short)
The message/data length (excluding header)

#### Connection ID (integer)
##### Protocol:TCP
The Connection ID has no use. Defaults to **0x00**
##### Protocol:UDP
During the handshake Pandoras Box provides a connection ID. Use this when sending commands.


#### Protocol (byte)
The protocol identifier.
##### Protocol:TCP
For TCP use **0x00**.
##### Protocol:UDP
Handshake Init (App->PB) **0x01**
Handshake Response (PB-App) **0x02**
UDP Command **0x03**

#### Checksum (byte)
To calculate the checksum take the sum of all bytes from the header excluding the PBAU-Identifier. Divide by 255. The remainder of the division is the checksum value (modulo 255)

### Message Structure
#### Header (17 bytes)
The message header as described before.

#### Command code (short)
The message code. When sending a command this identifies the requested action. Pandoras Box will (almost always) respond with the same code.

**Note:** A code is not used during **UDP handshake** initialization.

**Note:** Implementations should not check responses for the exact code, but rather for a positive value to determine success. Negative codes signalize failure.

**Note:** When using HTTP, check for equal or larger than 0. Older Pandoras Box versions may return 0 on success.

#### Data
The message body. This contains all the arguments or return values.

## Protocol specific information
### TCP
Connections can be established to any Pandoras Box running in Master mode. The TCP port used is **6211**. After successfully connecting Pandoras Box is ready to receive commands.

### UDP
UDP connections require a handshake. Remember that UDP is stateless and does not guarantee delivery of packets. Clients may have to resend the handshake initializer.

#### Step 1 (Client)
The client sends a handshake request to port UDP 6212. The connection id can be any value. The protocol id is **0x01**. Do not send a code. The data is an interger of an open UDP port number on the client used by Pandoras Box for responses.

#### Step 2 (Pandoras Box)
Pandoras Box will acknowledge by returning a header that includes the protocol id **0x02**. A connection id for the established connection is also provided by Pandoras Box. Store the connection id and use it for subsequent requests. Once the handshake is complete clients may send commands.

#### Step 3 (Client)
Send any of the available commands. Make sure you include the connection id from **Step 2** and use protocol id 0x03. Pandoras Box will respond to the port provided in **Step 1**.

### HTTP
The Pandoras Box Automation protocol is based on binary data. To transmit binary data via HTTP use the Base64 encoding and decoding. The HTTP request method used is **PBAUTO**. Data should be put in the body (similar to a POST request)



