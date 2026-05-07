import redis
import redis.asyncio as async_redis

redis_client = redis.Redis(host="localhost", port=6379, db=0)
async_redis_client = async_redis.Redis(host="localhost", port=6379, db=0)
