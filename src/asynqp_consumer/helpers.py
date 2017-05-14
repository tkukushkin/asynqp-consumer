import asyncio
from collections import Coroutine
from typing import Union


async def gather(*coros_or_futures: Union[Coroutine, asyncio.Future], loop: asyncio.BaseEventLoop = None):
    try:
        return await asyncio.gather(*coros_or_futures, loop=loop)
    except Exception:
        for obj in coros_or_futures:
            if isinstance(obj, Coroutine):
                obj.close()
        raise
