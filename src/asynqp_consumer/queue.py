import asynqp

from asynqp_consumer.records import Queue


async def declare_queue(channel: asynqp.Channel, queue: Queue) -> asynqp.Queue:
    asynqp_queue = await channel.declare_queue(
        name=queue.name,
        durable=queue.durable,
        exclusive=queue.exclusive,
        auto_delete=queue.auto_delete,
        arguments=queue.arguments,
    )

    for binding in queue.bindings:
        exchange = await channel.declare_exchange(
            name=binding.exchange.name,
            type=binding.exchange.type,
            durable=binding.exchange.durable,
            auto_delete=binding.exchange.auto_delete,
            arguments=binding.exchange.arguments,
        )

        await asynqp_queue.bind(
            exchange=exchange,
            routing_key=binding.routing_key,
            arguments=binding.arguments,
        )
    return asynqp_queue
