class Config:
    DATA_DIR = '/pic_search_image_collections/'
    SECRET_KEY = 'your_secret_key'
    CACHE_TYPE = 'redis'
    CACHE_DEFAULT_TIMEOUT = 60 * 60 * 24 * 365 * 100
    # Add other configuration variables here
    QDRANT_CLIENT_PARAMS = {'host': 'qdrant', 'port': 6333}
    EMBEDDING_SIZE = 512
    MAX_CONTENT_LENGTH = 300 * 1024 * 1024
    CACHE_REDIS_HOST = 'redis'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 0
    CACHE_REDIS_URL = 'redis://redis:6379/0'

