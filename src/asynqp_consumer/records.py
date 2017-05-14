from typing import NamedTuple, Dict, Union, List
from urllib.parse import urlparse


class Exchange(NamedTuple):
    name: str
    type: str = 'topic'
    durable: bool = True
    auto_delete: bool = False
    internal: bool = False
    arguments: Dict[str, Union[int, float, str]] = None


class QueueBinding(NamedTuple):
    exchange: Exchange
    routing_key: str
    arguments: Dict[str, Union[int, float, str]] = None


class Queue(NamedTuple):
    name: str
    bindings: List[QueueBinding] = []
    durable: bool = True
    exclusive: bool = False
    auto_delete: bool = False
    arguments: Dict[str, Union[int, float, str]] = None


class ConnectionParams(NamedTuple):

    host: str = 'localhost'
    port: int = 5672
    username: str = 'guest'
    password: str = 'guest'
    virtual_host: str = '/'

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
