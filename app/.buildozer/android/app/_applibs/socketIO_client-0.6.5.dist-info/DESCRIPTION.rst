.. image:: https://travis-ci.org/invisibleroads/socketIO-client.svg?branch=master
    :target: https://travis-ci.org/invisibleroads/socketIO-client


socketIO-client
===============
Here is a `socket.io <http://socket.io>`_ client library for Python.  You can use it to write test code for your socket.io server.

Please note that this version implements `socket.io protocol 1.x <https://github.com/automattic/socket.io-protocol>`_, which is not backwards compatible.  If you want to communicate using `socket.io protocol 0.9 <https://github.com/learnboost/socket.io-spec>`_ (which is compatible with `gevent-socketio <https://github.com/abourget/gevent-socketio>`_), please use `socketIO-client 0.5.6 <https://pypi.python.org/pypi/socketIO-client/0.5.6>`_.


Installation
------------
Install the package in an isolated environment. ::

    VIRTUAL_ENV=$HOME/.virtualenv

    # Prepare isolated environment
    virtualenv $VIRTUAL_ENV

    # Activate isolated environment
    source $VIRTUAL_ENV/bin/activate

    # Install package
    pip install -U socketIO-client


Usage
-----
Activate isolated environment. ::

    VIRTUAL_ENV=$HOME/.virtualenv
    source $VIRTUAL_ENV/bin/activate

Launch your socket.io server. ::

    # Get package folder
    PACKAGE_FOLDER=`python -c "import os, socketIO_client;\
        print(os.path.dirname(socketIO_client.__file__))"`
    # Start socket.io server
    DEBUG=* node $PACKAGE_FOLDER/tests/serve.js
    # Start proxy server in a separate terminal on the same machine
    DEBUG=* node $PACKAGE_FOLDER/tests/proxy.js

For debugging information, run these commands first. ::

    import logging
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.basicConfig(level=logging.DEBUG)

Emit. ::

    from socketIO_client import SocketIO, LoggingNamespace

    with SocketIO('localhost', 8000, LoggingNamespace) as socketIO:
        socketIO.emit('aaa')
        socketIO.wait(seconds=1)

Emit with callback. ::

    from socketIO_client import SocketIO, LoggingNamespace

    def on_bbb_response(*args):
        print('on_bbb_response', args)

    with SocketIO('localhost', 8000, LoggingNamespace) as socketIO:
        socketIO.emit('bbb', {'xxx': 'yyy'}, on_bbb_response)
        socketIO.wait_for_callbacks(seconds=1)

Define events. ::

    from socketIO_client import SocketIO, LoggingNamespace

    def on_aaa_response(*args):
        print('on_aaa_response', args)

    socketIO = SocketIO('localhost', 8000, LoggingNamespace)
    socketIO.on('aaa_response', on_aaa_response)
    socketIO.emit('aaa')
    socketIO.wait(seconds=1)

Define events in a namespace. ::

    from socketIO_client import SocketIO, BaseNamespace

    class Namespace(BaseNamespace):

        def on_aaa_response(self, *args):
            print('on_aaa_response', args)
            self.emit('bbb')

    socketIO = SocketIO('localhost', 8000, Namespace)
    socketIO.emit('aaa')
    socketIO.wait(seconds=1)

Define standard events. ::

    from socketIO_client import SocketIO, BaseNamespace

    class Namespace(BaseNamespace):

        def on_connect(self):
            print('[Connected]')

    socketIO = SocketIO('localhost', 8000, Namespace)
    socketIO.wait(seconds=1)

Define different namespaces on a single socket. ::

    from socketIO_client import SocketIO, BaseNamespace

    class ChatNamespace(BaseNamespace):

        def on_aaa_response(self, *args):
            print('on_aaa_response', args)

    class NewsNamespace(BaseNamespace):

        def on_aaa_response(self, *args):
            print('on_aaa_response', args)

    socketIO = SocketIO('localhost', 8000)
    chat_namespace = socketIO.define(ChatNamespace, '/chat')
    news_namespace = socketIO.define(NewsNamespace, '/news')

    chat_namespace.emit('aaa')
    news_namespace.emit('aaa')
    socketIO.wait(seconds=1)

Connect via SSL. ::

    from socketIO_client import SocketIO

    SocketIO('https://localhost', verify=False)

Specify params, headers, cookies, proxies thanks to the `requests <http://python-requests.org>`_ library. ::

    from socketIO_client import SocketIO
    from base64 import b64encode

    SocketIO(
        localhost', 8000,
        params={'q': 'qqq'},
        headers={'Authorization': 'Basic ' + b64encode('username:password')},
        cookies={'a': 'aaa'},
        proxies={'https': 'https://proxy.example.com:8080'})

Wait forever. ::

    from socketIO_client import SocketIO

    socketIO = SocketIO('localhost', 8000)
    socketIO.wait()


License
-------
This software is available under the MIT License.


Credits
-------
- `Guillermo Rauch <https://github.com/rauchg>`_ wrote the `socket.io specification <https://github.com/automattic/socket.io-protocol>`_.
- `Hiroki Ohtani <https://github.com/liris>`_ wrote `websocket-client <https://github.com/liris/websocket-client>`_.
- `rod <http://stackoverflow.com/users/370115/rod>`_ wrote a `prototype for a Python client to a socket.io server <http://stackoverflow.com/questions/6692908/formatting-messages-to-send-to-socket-io-node-js-server-from-python-client>`_.
- `Alexandre Bourget <https://github.com/abourget>`_ wrote `gevent-socketio <https://github.com/abourget/gevent-socketio>`_, which is a socket.io server written in Python.
- `Paul Kienzle <https://github.com/pkienzle>`_, `Zac Lee <https://github.com/zratic>`_, `Josh VanderLinden <https://github.com/codekoala>`_, `Ian Fitzpatrick <https://github.com/ifitzpatrick>`_, `Lucas Klein <https://github.com/lukasklein>`_, `Rui Chicoria <https://github.com/rchicoria>`_, `Travis Odom <https://github.com/burstaholic>`_, `Patrick Huber <https://github.com/stackmagic>`_, `Brad Campbell <https://github.com/bradjc>`_, `Daniel <https://github.com/dabidan>`_, `Sean Arietta <https://github.com/sarietta>`_ submitted code to expand support of the socket.io protocol.
- `Bernard Pratz <https://github.com/guyzmo>`_, `Francis Bull <https://github.com/franbull>`_ wrote prototypes to support xhr-polling and jsonp-polling.
- `Eric Chen <https://github.com/taiyangc>`_, `Denis Zinevich <https://github.com/dzinevich>`_, `Thiago Hersan <https://github.com/thiagohersan>`_, `Nayef Copty <https://github.com/nayefc>`_, `Jörgen Karlsson <https://github.com/jorgen-k>`_, `Branden Ghena <https://github.com/brghena>`_, `Tim Landscheidt <https://github.com/scfc>`_, `Matt Porritt <https://github.com/mattporritt>`_ suggested ways to make the connection more robust.
- `Merlijn van Deen <https://github.com/valhallasw>`_, `Frederic Sureau <https://github.com/fredericsureau>`_, `Marcus Cobden <https://github.com/leth>`_, `Drew Hutchison <https://github.com/drewhutchison>`_, `wuurrd <https://github.com/wuurrd>`_, `Adam Kecer <https://github.com/amfg>`_, `Alex Monk <https://github.com/Krenair>`_, `Vishal P R <https://github.com/vishalwy>`_, `John Vandenberg <https://github.com/jayvdb>`_, `Thomas Grainger <https://github.com/graingert>`_ proposed changes that make the library more friendly and practical for you!


0.6.5
-----
- Updated wait loop to be more responsive under websocket transport

0.6.4
-----
- Fixed support for Python 3
- Fixed thread cleanup

0.6.3
-----
- Upgraded to socket.io protocol 1.x for websocket transport
- Added locks to fix concurrency issues with polling transport
- Fixed SSL support

0.6.1
-----
- Upgraded to socket.io protocol 1.x thanks to Sean Arietta and Joe Palmer

0.5.6
-----
- Backported to support requests 0.8.2

0.5.5
-----
- Fixed reconnection in the event of server restart
- Fixed calling on_reconnect() so that it is actually called
- Set default Namespace=None
- Added support for Python 3.4

0.5.3
-----
- Updated wait loop to exit if the client wants to disconnect
- Fixed calling on_connect() so that it is called only once
- Set heartbeat_interval to be half of the heartbeat_timeout

0.5.2
-----
- Replaced secure=True with host='https://example.com'
- Fixed sending heartbeats thanks to Travis Odom

0.5.1
-----
- Added error handling in the event of websocket timeout
- Fixed sending acknowledgments in custom namespaces thanks to Travis Odom

0.5
---
- Rewrote library to use coroutines instead of threads to save memory
- Improved connection resilience
- Added support for xhr-polling thanks to Francis Bull
- Added support for jsonp-polling thanks to Bernard Pratz
- Added support for query params and cookies

0.4
---
- Added support for custom headers and proxies thanks to Rui and Sajal
- Added support for server-side callbacks thanks to Zac Lee
- Added low-level _SocketIO to remove cyclic references
- Merged Channel functionality into BaseNamespace thanks to Alexandre Bourget

0.3
---
- Added support for secure connections
- Added socketIO.wait()
- Improved exception handling in _RhythmicThread and _ListenerThread

0.2
---
- Added support for callbacks and channels thanks to Paul Kienzle
- Incorporated suggestions from Josh VanderLinden and Ian Fitzpatrick

0.1
---
- Wrapped `code from StackOverflow <http://stackoverflow.com/questions/6692908/formatting-messages-to-send-to-socket-io-node-js-server-from-python-client>`_
- Added exception handling to destructor in case of connection failure


