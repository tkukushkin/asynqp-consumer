# Consumer utility class for AMQP

[![Build Status](https://travis-ci.org/tkukushkin/asynqp-consumer.svg?branch=master)](https://travis-ci.org/tkukushkin/asynqp-consumer)

## Installation

Requirements:
* python >= 3.5 

```sh
pip install asynqp-consumer
```

## Example:

```python
import asyncio
from typing import List

from asynqp_consumer import ConnectionParams, Consumer, Exchange, Message, Queue, QueueBinding


async def callback(messages: List[Message]) -> None:
    for message in messages:
        print(message.body)  # json
        message.ack()


exchange=Exchange('test_exchange')   

consumer = Consumer(
    queue=Queue(
        name='test_queue',
        bindings=[
            QueueBinding(
                exchange=exchange,
                routing_key='test_routing_key'
            ),
        ]
    ),
    connection_params=[  # Round robin
        ConnectionParams.from_string('amqp:////'),
        ConnectionParams(username='test', password='test')
    ],
    callback=callback,
    prefetch_count=100,
    check_bulk_interval=0.3
)

try:
    asyncio.get_event_loop().run_until_complete(consumer.start())
finally:
    consumer.close()
```
