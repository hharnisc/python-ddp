import sys
import ejson
import time
import socket

from ws4py.exc import WebSocketException
from ws4py.client.threadedclient import WebSocketClient
from pyee import EventEmitter

DDP_VERSIONS = ["1", "pre2", "pre1"]

class DDPSocket(WebSocketClient, EventEmitter):
    """DDPSocket"""
    def __init__(self, url, debug=False):
        self.debug = debug
        # by default socket connections don't timeout. this causes issues
        # where reconnects can get stuck
        # TODO: make this configurable?
        socket.setdefaulttimeout(10)
        WebSocketClient.__init__(self, url)
        EventEmitter.__init__(self)

    def opened(self):
        """Set the connect flag to true and send the connect message to
        the server."""
        self.emit('opened')

    def closed(self, code, reason=None):
        """Called when the connection is closed"""
        self.emit('closed', code, reason)

    def send(self, msg_dict):
        """Send a message through the websocket client and wait for the
        answer if the message being sent contains an id attribute."""
        message = ejson.dumps(msg_dict)
        super(DDPSocket, self).send(message)
        self._debug_log('<<<{}'.format(message))

    def received_message(self, data):
        self._debug_log('>>>{}'.format(data))
        self.emit('received_message', data)

    def _debug_log(self, msg):
        """Debug log messages if debug=True"""
        if not self.debug:
            return
        sys.stderr.write('{}\n'.format(msg))

    def once(self):
        # check for self.sock existence
        # https://github.com/hharnisc/python-meteor/issues/5
        if self.sock:
            return super(DDPSocket, self).once()
        return False


class DDPClient(EventEmitter):
    """An event driven ddp client"""
    def __init__(self, url, auto_reconnect=True, auto_reconnect_timeout=0.5, debug=False):
        EventEmitter.__init__(self)
        self.ddpsocket = None
        self._ddp_version_index = 0
        self._retry_new_version = False
        self._is_closing = False
        self._is_reconnecting = False
        self.url = url
        self.auto_reconnect = auto_reconnect
        self.auto_reconnect_timeout = auto_reconnect_timeout
        self.debug = debug
        self._session = None
        self._uniq_id = 0
        self._callbacks = {}
        self._init_socket()

    def _init_socket(self):
        """Initialize the ddp socket"""
        # destroy the connection if it already exists
        if self.ddpsocket:
            self.ddpsocket.remove_all_listeners('received_message')
            self.ddpsocket.remove_all_listeners('closed')
            self.ddpsocket.remove_all_listeners('opened')
            self.ddpsocket.close_connection()
            self.ddpsocket = None

        # create a ddp socket and subscribe to events
        self.ddpsocket = DDPSocket(self.url, self.debug)
        self.ddpsocket.on('received_message', self.received_message)
        self.ddpsocket.on('closed', self.closed)
        self.ddpsocket.on('opened', self.opened)

    def _recover_network_failure(self):
        """Recover from a network failure"""
        if self.auto_reconnect and not self._is_closing:
            connected = False
            while not connected:
                log_msg = "* ATTEMPTING RECONNECT"
                if self._retry_new_version:
                    log_msg = "* RETRYING DIFFERENT DDP VERSION"
                self.ddpsocket._debug_log(log_msg)
                time.sleep(self.auto_reconnect_timeout)
                self._init_socket()
                try:
                    self.connect()
                    connected = True
                    if self._retry_new_version:
                        self._retry_new_version = False
                    else:
                        self._is_reconnecting = True
                except (socket.error, WebSocketException):
                    pass

    def _next_id(self):
        """Get the next id that will be sent to the server"""
        self._uniq_id += 1
        return str(self._uniq_id)

    def connect(self):
        if self.ddpsocket:
            self.ddpsocket.connect()

    def close(self):
        self._is_closing = True
        self.ddpsocket.close_connection()

    def opened(self):
        """Send the connect message to the server."""
        # give up if there are no more ddp versions to try
        if self._ddp_version_index == len(DDP_VERSIONS):
            self.ddpsocket._debug_log('* DDP VERSION MISMATCH')
            self.emit('version_mismatch', DDP_VERSIONS)
            return

        # use server recommended version if we support it
        if self._retry_new_version in DDP_VERSIONS:
            self._ddp_version_index = [i for i, x in enumerate(DDP_VERSIONS)
                                       if x == self._retry_new_version][0]

        connect_msg = {
            "msg": "connect",
            "version": DDP_VERSIONS[self._ddp_version_index],
            "support": DDP_VERSIONS
        }

        # if we've already got a session token then reconnect
        if self._session:
            connect_msg["session"] = self._session

        self.send(connect_msg)

    def closed(self, code, reason=None):
        """Called when the connection is closed"""
        self.emit('socket_closed', code, reason)
        self._recover_network_failure()

    def send(self, msg_dict):
        """Send a message through the websocket client and wait for the
        answer if the message being sent contains an id attribute."""
        self.ddpsocket.send(msg_dict)

    def received_message(self, data):
        """Incomming messages"""
        data = ejson.loads(str(data))
        if not data.get('msg'):
            return

        elif data['msg'] == 'failed':
            self._ddp_version_index += 1
            self._retry_new_version = data.get('version', True)
            self.emit('failed', data)

        elif data['msg'] == 'connected':
            self._session = data.get('session')
            if self._is_reconnecting:
                self.ddpsocket._debug_log("* RECONNECTED")
                self.emit('reconnected')
                self._is_reconnecting = False
            else:
                self.ddpsocket._debug_log("* CONNECTED")
                self.emit('connected')
                self._retry_new_version = False

        # method result
        elif data['msg'] == 'result':
            # call the optional callback
            callback = self._callbacks.get(data['id'])
            if callback:
                callback(data.get('error'), data.get('result'))
                self._callbacks.pop(data['id'])

        # missing subscription
        elif data['msg'] == 'nosub':
            callback = self._callbacks.get(data['id'])
            if callback:
                callback(data.get('error'), data['id'])
                self._callbacks.pop(data['id'])

        # document added to collection
        elif data['msg'] == 'added':
            self.emit('added', data['collection'],
                      data['id'], data.get('fields', {}))

        # document changed in collection
        elif data['msg'] == 'changed':
            self.emit('changed', data['collection'], data['id'],
                       data.get('fields', {}), data.get('cleared', {}))

        # document removed from collection
        elif data['msg'] == 'removed':
            self.emit('removed', data['collection'], data['id'])

        # subcription ready
        elif data['msg'] == 'ready':
            for sub_id in data.get('subs', []):
                callback = self._callbacks.get(sub_id)
                if callback:
                    callback(data.get('error'), sub_id)
                    self._callbacks.pop(sub_id)

        elif data['msg'] == 'ping':
            msg = {'msg': 'pong'}
            id = data.get('id')
            if id is not None:
                msg['id'] = id
            self.ddpsocket.send(msg)

        else:
            pass

    def call(self, method, params, callback=None):
        """Call a method on the server

        Arguments:
        method - the remote server method
        params - an array of commands to send to the method

        Keyword Arguments:
        callback - a callback function containing the return data"""
        cur_id = self._next_id()
        if callback:
            self._callbacks[cur_id] = callback
        self.send({'msg': 'method', 'id': cur_id, 'method': method, 'params': params})

    def subscribe(self, name, params, callback=None):
        """Subcribe to add/change/remove events for a collection

        Arguments:
        name - the name of the publication to subscribe
        params - params to subscribe (parsed as ejson)

        Keyword Arguments:
        callback - a callback function that gets executed when the subscription has completed"""
        cur_id = self._next_id()
        if callback:
            self._callbacks[cur_id] = callback
        self.send({'msg': 'sub', 'id': cur_id, 'name': name, 'params': params})
        return cur_id

    def unsubscribe(self, sub_id):
        """Unsubscribe from a collection

        Arguments:
        sub_id - the id of the subsciption (returned by subcribe)"""
        self.send({'msg': 'unsub', 'id': sub_id})
