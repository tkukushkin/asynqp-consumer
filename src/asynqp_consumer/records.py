from abc import ABCMeta
from typing import Dict, List, Union
from urllib.parse import urlparse


ArgumentsType = Dict[str, Union[int, float, str]]


class BaseObject(metaclass=ABCMeta):

    __slots__ = []

    def __eq__(self, other):
        if type(self) != type(other):  # pylint: disable=unidiomatic-typecheck
            return False
        for name in self.__slots__:
            if getattr(self, name) != getattr(other, name):
                return False
        return True

    def __repr__(self):
        return '<{} {}>'.format(
            type(self).__name__,
            ' '.join('{}={}'.format(name, getattr(self, name)) for name in self.__slots__)
        )


class Exchange(BaseObject):

    __slots__ = ['name', 'type', 'durable', 'auto_delete', 'internal', 'arguments']

    def __init__(self, name: str, type: str = 'topic', durable: bool = True, auto_delete: bool = False,
                 internal: bool = False, arguments: ArgumentsType = None):
        self.name = name
        self.type = type
        self.durable = durable
        self.auto_delete = auto_delete
        self.internal = internal
        self.arguments = arguments


class QueueBinding(BaseObject):

    __slots__ = ['exchange', 'routing_key', 'arguments']

    def __init__(self, exchange: Exchange, routing_key: str, arguments: ArgumentsType = None):
        self.exchange = exchange
        self.routing_key = routing_key
        self.arguments = arguments


class Queue(BaseObject):

    __slots__ = ['name', 'bindings', 'durable', 'exclusive', 'auto_delete', 'arguments']

    def __init__(self, name: str, bindings: List[QueueBinding] = None, durable: bool = True, exclusive: bool = False,
                 auto_delete: bool = False, arguments: ArgumentsType = None):
        self.name = name
        self.bindings = bindings
        self.durable = durable
        self.exclusive = exclusive
        self.auto_delete = auto_delete
        self.arguments = arguments


class ConnectionParams(BaseObject):

    __slots__ = ['host', 'port', 'username', 'password', 'virtual_host']

    def __init__(self, host: str = 'localhost', port: int = 5672, username: str = 'guest', password: str = 'guest',
                 virtual_host: str = '/'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.virtual_host = virtual_host

    @classmethod
    def from_string(cls, connection_string: str) -> 'ConnectionParams':
        parse_result = urlparse(connection_string)
        assert parse_result.scheme == 'amqp', 'Scheme must be amqp'
        kwargs = {
            'virtual_host': parse_result.path[1:] if parse_result.path else None
        }
        if parse_result.hostname:
            kwargs['host'] = parse_result.hostname
        if parse_result.port:
            kwargs['port'] = int(parse_result.port)
        if parse_result.username:
            kwargs['username'] = parse_result.username
        if parse_result.password:
            kwargs['password'] = parse_result.password
        return cls(**kwargs)
