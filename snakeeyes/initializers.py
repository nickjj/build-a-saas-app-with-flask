from redis import Redis

from config.settings import REDIS_URL


redis = Redis.from_url(REDIS_URL)
