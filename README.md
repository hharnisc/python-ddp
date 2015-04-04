# python-ddp

An event driven ddp client

**Installation**

```bash
$ pip install python-ddp
```

**Table of Contents**

- [History](#history)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Collaborators](#collaborators)

## History

**Latest Version** 0.1.5
- Handle DDP versions _1_, _pre2_ and _pre1_ (thanks [@ppettit](https://github.com/ppettit))
- Added [EJSON](http://docs.meteor.com/#/full/ejson) support (thanks [@tdamsma](https://github.com/tdamsma))

**Version** 0.1.4

- BUGFIX - fix reconnect order (thanks [@ppettit](https://github.com/ppettit))
- BUGFIX - fix breaking change <https://github.com/hharnisc/python-ddp/commit/5998839866fccfee8a456cb5cb2559a320f2203d> (thanks [@ppettit](https://github.com/ppettit))

**Version** 0.1.3

- BUGFIX - closed python meteor [issue #5](https://github.com/hharnisc/python-meteor/issues/5)

**Version** 0.1.2

- BUGFIX - auto reconnect can now handle WebSocketExceptions (thanks [@ppettit](https://github.com/ppettit))

**Version** 0.1.1

- Implemented auto reconnect (auto reconnect on by default) and reconnected event emitter

**Version** 0.1.0

- Initial implementation, add ability to call, subscribe and unsubscribe

## Quick Start

### General Commands

**Establish A Connection And Close It**

```python
from DDPClient import DDPClient

client = DDPClient('ws://127.0.0.1:3000/websocket')
client.connect()
client.close()
```

**Establish A Connection Without Auto Reconnect**

```python
from DDPClient import DDPClient
client = DDPClient('ws://127.0.0.1:3000/websocket', auto_reconnect=False)
client.connect()
```

**Establish A Connection And With Reconnect Different Frequency**

```python
from DDPClient import DDPClient
# try to reconnect every second
client = DDPClient('ws://127.0.0.1:3000/websocket', auto_reconnect=True, auto_reconnect_timeout=1)
client.connect()
```

**Call A Remote Function**

```python
from DDPClient import DDPClient

def callback_function(data):
    print data

client = DDPClient('ws://127.0.0.1:3000/websocket')
client.connect()
client.call('someFunction', [1,2,3], callback_function)
```

**Subscribe and Unsubscribe**

```python
from DDPClient import DDPClient

def subscription_callback(data):
    print data

client = DDPClient('ws://127.0.0.1:3000/websocket')
client.connect()
sub_id = client.subscribe('posts', subscription_callback)
client.unsubscribe(sub_id)
```

## Usage

### Class Init

####DDPClient(url, auto_reconnect=True, auto_reconnect_timeout=0.5, debug=False)

**Arguments**

_url_ - to connect to ddp server

**Keyword Arguments**

_auto_reconnect_ - automatic reconnect (default: True)  
_auto_reconnect_timeout_ - reconnect every X seconds (default: 0.5)  
_debug_ - print out lots of debug info (default: False)  
     
### Functions

####call(self, method, params, callback=None)

Call a method on the server

**Arguments**

_method_ - the remote server method  
_params_ - an array of commands to send to the method  

**Keyword Arguments**

_callback_ - a callback function containing the return data

####subscribe(self, name, params, callback=None)

Subcribe to add/change/remove events for a collection

**Arguments**

_name_ - the name of the publication to subscribe  
_params_ - params to subscribe (parsed as json)  

**Keyword Arguments**

_callback_ - a callback function that gets executed when the subscription has completed  


####unsubscribe(self, sub_id)

Unsubscribe from a collection

**Arguments**

_sub_id_ - the id of the subsciption (returned by subcribe)  

### Events and Callback Arguments

When creating an instance of `DDPClient` it is capable of emitting a few events with arguments. The documentation below assumes that you've instanciated a client with the following code:

```python
from DDPClient import DDPClient
client = DDPClient('ws://127.0.0.1:3000/websocket')
```

#### connected

Register the event to a callback function

```python
def connected(self):
    print '* CONNECTED'

client.on('connected', connected)
```

The connected event callback takes no arguments

#### socket_closed

Register the event to a callback function

```python
def closed(self, code, reason):
    print '* CONNECTION CLOSED {} {}'.format(code, reason)

client.on('socket_closed', closed)
```

`socket_closed` callback takes the following arguments

_code_ - the error code  
_reason_ - the error message  

### reconnected

```python
def reconnected(self):
    print '* RECONNECTED'

client.on('reconnected', reconnected)
```

`reconnected` call back takes no arguments

#### failed

Register the event to a callback function

```python
def failed(collection, data):
    print '* FAILED - data: {}'.format(str(data))

client.on('failed', failed)
```

`failed` callback takes the following arguments

_data_ - the error data  

#### version_mismatch

Register the event to a callback function

This event is fired if the server and client can not agree on a DDP version to use and is a fatal error

```python
def version_mismatch(versions):
    print '* VERSION MISMATCH - versions: {}'.format(str(versions))

client.on('version_mismatch', version_mismatch)
```

`version_mismatch` callback takes the following arguments

_versions_ - the DDP versions attempted

#### added

Register the event to a callback function

```python
def added(collection, id, fields):
    print '* ADDED {} {}'.format(collection, id)
    for key, value in fields.items():
        print '  - FIELD {} {}'.format(key, value)

client.on('added', added)
```

`added` callback takes the following arguments

_collection_ - the collection that has been modified  
_id_ - the collection item id
_fields_ - the fields for item

#### changed

Register the event to a callback function

```python
def changed(self, collection, id, fields, cleared):
    print '* CHANGED {} {}'.format(collection, id)
    for key, value in fields.items():
        print '  - FIELD {} {}'.format(key, value)
    for key, value in cleared.items():
        print '  - CLEARED {} {}'.format(key, value)

client.on('changed', changed)
```

`changed` callback takes the following arguments

_collection_ - the collection that has been modified  
_id_ - the collection item id
_fields_ - the fields for item  
_cleared_ - the fields for the item that have been removed

#### removed

Register the event to a callback function

```python
def removed(collection, id):
    print '* REMOVED {} {}'.format(collection, id)

client.on('removed', removed)
```

`removed` callback takes the following arguments

_collection_ - the collection that has been modified  
_id_ - the collection item id

####All of the callbacks

For reference

```python
client.on('connected', connected)
client.on('socket_closed', closed)
client.on('reconnected', reconnected)
client.on('failed', failed)
client.on('version_mismatch', version_mismatch)
client.on('added', added)
client.on('changed', changed)
client.on('removed', removed)
```

##Collaborators

- [@ppettit](https://github.com/ppettit)
- [@tdamsma](https://github.com/tdamsma)