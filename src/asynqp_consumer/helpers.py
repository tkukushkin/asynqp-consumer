import asyncio
from collections.abc import Coroutine
from typing import Any, Awaitable


async def gather(*coros_or_futures: Awaitable[Any], loop: asyncio.BaseEventLoop = None):
    try:
        return await asyncio.gather(*coros_or_futures, loop=loop)
    except Exception:
        for obj in coros_or_futures:
            if isinstance(obj, Coroutine):
                obj.close()
        raise
