# Abstract
This document contains information on the SDK Architecture.

## SDK Architecture
The SDK implementations of all languages follow a pattern. You don't have to follow it, but it has proved itself to be a good way to structure things.
There are three different concerns that have to be covered. They are usually built using three classes. **PBAuto**, **Connector** & **Buffer**. The advantage of doing so is that the **Connector** and **Buffer** classes have to be implemented once and then the **PBAuto** class can utilize them to communicate with Pandoras Box. **PBAuto** classes are generated using a database and can be quickly updated when new commands are available.

#### PBAuto
The **PBAuto** class is the main class that uses the **Connector** and **Buffer** classes to communicate with Pandoras Box. It offers the functionality to the client application and takes care of constructing messages and parsing the responses.

#### Connector
The **Connector** class knows how to send and receive data from/to Pandoras Box. It is also capable of constructing the header required by the protocol.

#### Buffer
The **Buffer** class is backed by a byte data store. It can take the native data types and cast them to the types required by Pandoras Box.

#### Workflow
The **client application** calls a function on the **PBAuto** class. It in turn constructs the package using the **Buffer** class. The **Buffer** contents are then sent to **PB** using the **Connector** class. Data returned from the **Connector** is then put into another **Buffer** instance. Finally, the **PBAuto** parses the response and returns to the client application.
