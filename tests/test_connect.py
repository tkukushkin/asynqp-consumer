import asynqp
import pytest
from tests.utils import future

from asynqp_consumer import ConnectionParams
from asynqp_consumer.connect import connect_and_open_channel


@pytest.mark.asyncio
async def test_connect_and_open_channel(mocker, event_loop):
    # arrange
    connection = mocker.Mock(spec=asynqp.Connection)

    channel = mocker.Mock(spec=asynqp.Channel)

    asynqp_connect_and_open_channel = mocker.patch(
        'asynqp_consumer.connect.asynqp.connect_and_open_channel',
        autospec=True,
        return_value=future((connection, channel))
    )

    # act
    result = await connect_and_open_channel(ConnectionParams(), event_loop)

    # assert
    assert result == (connection, channel)

    asynqp_connect_and_open_channel.assert_called_once_with(
        host='localhost',
        port=5672,
        username='guest',
        password='guest',
        virtual_host='/',
        loop=event_loop,
    )
