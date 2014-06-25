# python-ddp

An event driven ddp client

**Table of Contents**

- [History](#history)
- [Quick Start](#quick-start)
- [Usage](#usage)

## History

**Latest Version** 0.1.0

- Initial implementation, add ability to call, subscribe and unsubscribe

## Quick Start

### General Commands

**Establish a connection and Close It**

```python
from DDPClient import DDPClient

client = DDPClient('ws://127.0.0.1:3000/websocket')
client.connect()
client.close()
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

### Connection State Events

**Connected**

```python
from DDPClient import DDPClient

def connected(self):
    print '* CONNECTED'

client = DDPClient('ws://127.0.0.1:3000/websocket')
client.on('connected', connected)
client.connect()
```

**Socket Closed**

```python
from DDPClient import DDPClient

def closed(self, code, reason):
    print '* CONNECTION CLOSED {} {}'.format(code, reason)

client = DDPClient('ws://127.0.0.1:3000/websocket')
client.on('socket_closed', closed)
client.connect()
```

### Subscription Events

**Added To Collection**

```python
from DDPClient import DDPClient

def added(collection, id, fields):
    print '* ADDED {} {}'.format(collection, id)
    for key, value in fields.items():
        print '  - FIELD {} {}'.format(key, value)

client = DDPClient('ws://127.0.0.1:3000/websocket')
client.on('added', added)
client.connect()
sub_id = client.subscribe('posts')
```

**Collection Changed**

```python
from DDPClient import DDPClient

def changed(self, collection, id, fields, cleared):
    print '* CHANGED {} {}'.format(collection, id)
    for key, value in fields.items():
        print '  - FIELD {} {}'.format(key, value)
    for key, value in cleared.items():
        print '  - CLEARED {} {}'.format(key, value)

client = DDPClient('ws://127.0.0.1:3000/websocket')
client.on('changed', changed)
client.connect()
sub_id = client.subscribe('posts')
```

**Removed From Collection**

```python
from DDPClient import DDPClient

def removed(collection, id):
    print '* REMOVED {} {}'.format(collection, id)

client = DDPClient('ws://127.0.0.1:3000/websocket')
client.on('removed', removed)
client.connect()
sub_id = client.subscribe('posts')
```

### Other Events

**Failed**

```python
from DDPClient import DDPClient

def failed(collection, code, reason):
    print '* FAILED - data: {}'.format(str(data))

client = DDPClient('ws://127.0.0.1:3000/websocket')
client.connect()
client.on('failed', failed)
```

## Usage
     
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

`closed` callback takes the following arguments

_code_ - the error code  
_reason_ - the error message  

#### failed

Register the event to a callback function

```python
def failed(collection, code, reason):
    print '* FAILED - data: {}'.format(str(data))

client.on('failed', failed)
```

`failed` callback takes the following arguments

_code_ - the error code  
_reason_ - the error message  

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
client.on('failed', failed)
client.on('added', added)
client.on('changed', changed)
client.on('removed', removed)
```