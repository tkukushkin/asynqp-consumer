import asyncio
from typing import Tuple

import asynqp

from asynqp_consumer.records import ConnectionParams


async def connect_and_open_channel(
        connection_params: ConnectionParams,
        loop: asyncio.BaseEventLoop = None,
) -> Tuple[asynqp.Connection, asynqp.Channel]:
    loop = loop or asyncio.get_event_loop()
    return await asynqp.connect_and_open_channel(
        host=connection_params.host,
        port=connection_params.port,
        username=connection_params.username,
        password=connection_params.password,
        virtual_host=connection_params.virtual_host,
        loop=loop
    )
