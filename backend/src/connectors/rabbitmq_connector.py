import json

import aio_pika
from aio_pika.abc import (
    AbstractChannel,
    AbstractConnection,
    AbstractExchange,
    ExchangeType,
)


class RabbitManager:
    _connection: AbstractConnection
    _channel: AbstractChannel
    exchange: AbstractExchange

    def __init__(self, url: str):
        self.url = url

    async def connect(self):
        self._connection = await aio_pika.connect_robust(self.url)

        self._channel = await self._connection.channel()

        self.exchange = await self._channel.declare_exchange(
            "x.links.events", type=ExchangeType.DIRECT, durable=True
        )
        queue = await self._channel.declare_queue("analytics.clicks", durable=True)
        await queue.bind(exchange=self.exchange, routing_key="link.clicked")

    async def publish_event(self, routing_key: str, payload: dict):
        if not self.exchange:
            raise RuntimeError("RabbitMQ is not connected")

        body = json.dumps(payload, default=str).encode("utf-8")
        message = aio_pika.Message(
            body=body,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json",
        )
        await self.exchange.publish(message, routing_key=routing_key)

    async def close(self):
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
