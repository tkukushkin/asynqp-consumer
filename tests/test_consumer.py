import asyncio
import json
from asyncio import Future
from unittest import mock

import asynqp
import pytest

from asynqp_consumer import ConnectionParams, Consumer, Exchange, Queue, QueueBinding, Message
from asynqp_consumer.consumer import ConsumerCloseException

from tests.utils import future


def get_consumer(**kwargs):
    return Consumer(
        queue=Queue(
            name='test_queue',
            bindings=[
                QueueBinding(
                    exchange=Exchange('test_exchange'),
                    routing_key='test_routing_key'
                )
            ]
        ),
        connection_params=[
            ConnectionParams(
                host='test_host',
                port=1234,
                username='test_username',
                password='test_password',
                virtual_host='test_virtual_host',
            )
        ],
        **kwargs
    )


async def simple_callback(messages):
    pass


@pytest.mark.asyncio
async def test_start__two_attempts(mocker, event_loop):
    # arrange
    consumer = get_consumer(callback=simple_callback)

    mocker.patch.object(consumer, '_connect', side_effect=iter([OSError, future()]))
    mocker.patch.object(consumer, '_disconnect', return_value=future())
    mocker.patch.object(consumer, '_process_queue', return_value=future())
    mocker.patch.object(consumer, '_check_bulk', return_value=future())

    consumer._connection = mocker.Mock(spec=asynqp.Connection)
    consumer._connection.closed = asyncio.Future(loop=event_loop)

    mocker.patch('asynqp_consumer.consumer.gather', autospec=True, return_value=future())
    Future = mocker.patch('asynqp_consumer.consumer.asyncio.Future', autospec=True)
    Future.return_value.done.side_effect = iter([False, False, True])
    Future.return_value._loop = event_loop

    consumer._connection.closed.set_exception(ConsumerCloseException)

    sleep = mocker.patch('asynqp_consumer.consumer.asyncio.sleep', return_value=future())

    # act
    await consumer.start(loop=event_loop)

    # assert
    assert consumer._connect.mock_calls == [
        mocker.call(loop=event_loop),
        mocker.call(loop=event_loop),
    ]
    consumer._disconnect.assert_called_once_with()
    consumer._process_queue.assert_called_once_with(loop=event_loop)
    consumer._check_bulk.assert_called_once_with(loop=event_loop)
    sleep.assert_called_once_with(3, loop=event_loop)


@pytest.mark.asyncio
async def test__connect__ok(mocker, event_loop):
    # arrange
    connection = mocker.Mock(spec=asynqp.Connection)

    channel = mocker.Mock(spec=asynqp.Channel)
    channel.set_qos.return_value = future()

    connect_and_open_channel = mocker.patch('asynqp_consumer.consumer.connect_and_open_channel', autospec=True)
    connect_and_open_channel.return_value = future((connection, channel))

    asynqp_queue = mocker.Mock(spec=asynqp.Queue)

    declare_queue = mocker.patch('asynqp_consumer.consumer.declare_queue', autospec=True)
    declare_queue.return_value = future(asynqp_queue)

    consumer = get_consumer(callback=simple_callback)

    # act
    await consumer._connect(loop=event_loop)

    # assert
    connect_and_open_channel.assert_called_once_with(ConnectionParams(
        host='test_host',
        port=1234,
        username='test_username',
        password='test_password',
        virtual_host='test_virtual_host',
    ), event_loop)

    declare_queue.assert_called_once_with(channel, Queue(
        name='test_queue',
        bindings=[
            QueueBinding(
                exchange=Exchange('test_exchange'),
                routing_key='test_routing_key'
            )
        ]
    ))

    channel.set_qos.assert_called_once_with(prefetch_count=0)

    assert consumer._connection is connection
    assert consumer._channel is channel
    assert consumer._queue is asynqp_queue


@pytest.mark.asyncio
async def test__disconnect_ok(mocker):
    # arrange
    consumer = get_consumer(callback=simple_callback)

    connection = mocker.patch.object(consumer, '_connection', autospec=True)
    connection.close.return_value = future()

    channel = mocker.patch.object(consumer, '_channel', autospec=True)
    channel.close.return_value = future()

    # act
    await consumer._disconnect()

    # assert
    consumer._connection.close.assert_called_once_with()
    consumer._channel.close.assert_called_once_with()


def test_close(mocker):
    # arrange
    consumer = get_consumer(callback=simple_callback)
    consumer._closed = asyncio.Future()

    connection = mocker.patch.object(consumer, '_connection', autospec=True)
    connection.closed = Future()

    # act
    consumer.close()

    # assert
    assert consumer._closed.done()
    assert isinstance(consumer._closed.exception(), ConsumerCloseException)


class AsyncIter:

    def __init__(self, iterable):
        self.iterable = iter(iterable)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iterable)
        except StopIteration:
            raise StopAsyncIteration


@pytest.mark.asyncio
async def test__process_queue__when_prefetch_count_is_0(mocker, event_loop):
    # arrange
    consumer = get_consumer(callback=simple_callback, prefetch_count=0)
    mocker.patch.object(consumer, '_get_messages_iterator', return_value=future(AsyncIter([
        mock.Mock(spec=asynqp.IncomingMessage),
        mock.Mock(spec=asynqp.IncomingMessage),
    ])))
    mocker.patch.object(consumer, '_process_bulk', return_value=future())

    # act
    await consumer._process_queue(loop=event_loop)

    # assert
    assert len(consumer._messages) == 2
    assert isinstance(consumer._messages[0], Message)
    assert isinstance(consumer._messages[1], Message)
    assert not consumer._process_bulk.called


@pytest.mark.asyncio
async def test__process_queue__when_prefetch_count_is_not_0(mocker, event_loop):
    # arrange
    consumer = get_consumer(callback=simple_callback, prefetch_count=1)
    mocker.patch.object(consumer, '_get_messages_iterator', return_value=future(AsyncIter([
        mock.Mock(spec=asynqp.IncomingMessage),
        mock.Mock(spec=asynqp.IncomingMessage),
    ])))
    mocker.patch.object(consumer, '_process_bulk', side_effect=iter([future(), future()]))

    # act
    await consumer._process_queue(loop=event_loop)

    # assert
    assert len(consumer._messages) == 2
    assert isinstance(consumer._messages[0], Message)
    assert isinstance(consumer._messages[1], Message)
    consumer._process_bulk.mock_calls == [mocker.call(), mocker.call()]


@pytest.mark.asyncio
async def test__process_queue__when_message_is_invalid_json(mocker, event_loop):
    # arrange
    consumer = get_consumer(callback=simple_callback, prefetch_count=1)

    message = mock.Mock(spec=asynqp.IncomingMessage)
    message.json.side_effect = json.JSONDecodeError('message', '', 0)
    message.body = 'Error json'

    mocker.patch.object(consumer, '_get_messages_iterator', return_value=future(AsyncIter([message])))

    # act
    await consumer._process_queue(loop=event_loop)

    # assert
    assert consumer._messages == []


@pytest.mark.asyncio
async def test__process_queue__ack_message_when_json_is_invalid(mocker, event_loop, capsys):
    # arrange
    consumer = get_consumer(callback=simple_callback, prefetch_count=1, reject_invalid_json=False)

    message = asynqp.IncomingMessage(
        body="Invalid JSON",
        sender=None,
        delivery_tag=None,
        exchange_name=None,
        routing_key=None,
    )
    mocker.patch.object(message, 'ack', autospec=True)
    mocker.patch.object(consumer, '_get_messages_iterator', return_value=future(AsyncIter([message])))
    logger_exception = mocker.patch('asynqp_consumer.consumer.logger.exception')

    # act
    await consumer._process_queue(loop=event_loop)

    # assert
    assert consumer._messages == []
    message.ack.assert_called_once_with()
    logger_exception.assert_called_once_with('Failed to parse message body: %s', b'Invalid JSON')


class SomeException(Exception):
    pass


@pytest.mark.asyncio
async def test__iter_messages(mocker, event_loop):
    # arrange
    queue = mocker.Mock(spec=asynqp.Queue)
    queue.consume.return_value = future()

    consumer = get_consumer(callback=simple_callback, prefetch_count=0)
    mocker.patch.object(consumer, '_queue', new=queue)

    queue = mocker.patch('asynqp_consumer.consumer.asyncio.Queue').return_value
    queue.get.side_effect = iter([
        future(Message(mock.Mock(spec=asynqp.IncomingMessage))),
        future(Message(mock.Mock(spec=asynqp.IncomingMessage))),
        future(exception=SomeException),
    ])

    # act
    result = []
    with pytest.raises(SomeException):
        messages_iterator = await consumer._get_messages_iterator(loop=event_loop)
        async for message in messages_iterator:
            result.append(message)

    # assert
    assert len(result) == 2
    assert isinstance(result[0], Message)
    assert isinstance(result[1], Message)


@pytest.mark.asyncio
async def test__consume_with_arguments(mocker, event_loop):
    # arrange
    queue = mocker.Mock(spec=asynqp.Queue)
    queue.consume.return_value = future()

    consume_arguments = {'x-priority': 100}
    consumer = get_consumer(callback=simple_callback, prefetch_count=0, consume_arguments=consume_arguments)
    mocker.patch.object(consumer, '_queue', new=queue)
    asyncio_queue = mocker.patch('asynqp_consumer.consumer.asyncio.Queue').return_value

    # act
    await consumer._get_messages_iterator(loop=event_loop)

    # assert
    queue.consume.assert_called_once_with(callback=asyncio_queue.put_nowait, arguments=consume_arguments)
