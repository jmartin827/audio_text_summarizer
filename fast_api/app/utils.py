import logging
import os

import redis


def logging_setup():
    # Logging Setup
    logging.basicConfig(
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    # Set logging level
    logging.getLogger().setLevel(logging.INFO)


def get_redis_client() -> redis.Redis:
    """Initialize Redis client using env variables and check if DB 1 exists.
    Will create DB 1 if it doesn't exist and DB 0 is used for Celery
    """
    # TODO Centralize this function
    # TODO resolve bug as this isn't conditional and occurs each time.

    db_num = int(os.environ.get('REDIS_DB'))
    client = redis.Redis(host=os.environ.get('REDIS_HOST'),
                         port=int(os.environ.get('REDIS_PORT')),
                         db=db_num)

    if not client.exists(db_num):
        client.execute_command('SELECT', db_num)
        logging.info(f"Created Redis DB as required DB {int(os.environ.get('REDIS_DB'))} does not exist.")

    return client
