import asynqp
import pytest
from tests.utils import future

from asynqp_consumer import Queue, QueueBinding, Exchange

from asynqp_consumer.queue import declare_queue


@pytest.mark.asyncio
async def test_declare_queue(mocker):
    # arrange
    asynqp_queue = mocker.Mock(spec=asynqp.Queue)
    asynqp_queue.bind.return_value = future()

    asynqp_exchange = mocker.Mock(spec=asynqp.Exchange)

    channel = mocker.Mock(spec=asynqp.Channel)
    channel.declare_queue.return_value = future(asynqp_queue)
    channel.declare_exchange.return_value = future(asynqp_exchange)

    # act
    result = await declare_queue(channel, Queue(
        name='test-queue',
        bindings=[
            QueueBinding(
                exchange=Exchange('test-exchange'),
                routing_key='test-routing-key',
            )
        ]
    ))

    # assert
    assert result is asynqp_queue

    channel.declare_queue.assert_called_once_with(
        name='test-queue',
        durable=True,
        exclusive=False,
        auto_delete=False,
        arguments=None,
    )

    channel.declare_exchange.assert_called_once_with(
        name='test-exchange',
        type='topic',
        durable=True,
        auto_delete=False,
        arguments=None,
    )

    asynqp_queue.bind.assert_called_once_with(
        exchange=asynqp_exchange,
        routing_key='test-routing-key',
        arguments=None,
    )
