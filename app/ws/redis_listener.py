import asyncio
import json

from app.core.redis import async_redis_client
from app.ws.manager import manager


async def redis_listener():
    pubsub = async_redis_client.pubsub()
    await pubsub.psubscribe("user:*")

    async for message in pubsub.listen():
        if message["type"] != "pmessage":
            continue

        channel = message["channel"].decode()
        user_id = channel.split(":")[1]

        data = json.loads(message["data"])

        await manager.send(user_id, data)
