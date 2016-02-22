# Introduction
## Pandoras Box
#### Terminology
* **ID**s and **index**es are used to identify various items. The key difference is that during runtime **ID**s are usually fixed and **index**es may change their meaning 

#### Pandoras Box Machines
There is always one Pandoras Box software running as the **master** and optionally you can have as many **clients** connected to it as you want. If you have multiple **masters** in one network the assignment of **clients** to **masters** is controlled by the **domain** id. It is also important when remote controlling Pandoras Box from either Widget Designer or a custom application. Technically, each Pandoras Box on the network is called a **node**. Once it is added to the project, or, once a new *offline* or *empty* server is added (using the Device Types Tab) a **site** is created. You can assign any **node** (the machine on the network) to any **site** as long as the license matches.

#### Content
Videos, Images, Live Inputs are all referred to as **resources**. Once you add them to your project, a new **asset** is created. This **asset** contains information about the file that is being referenced.