import logging
import os

import redis
from fastapi import HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS


def logging_setup():
    # Logging Setup
    logging.basicConfig(
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    # Set logging level
    logging.getLogger().setLevel(logging.INFO)


def get_redis_client(db_num: int) -> redis.Redis:
    """Initialize Redis client.
    DB 0 is Celery
    DB 1 is task status
    DB 2 is for IP rate limiting
    """
    # Centralize this function
    client = redis.Redis(host=os.environ.get('REDIS_HOST'),
                         port=int(os.environ.get('REDIS_PORT')),
                         db=db_num)

    client.execute_command('SELECT', db_num)

    return client


def check__limit_job_count(ip_address: str, job_uuid: str, limit: int) -> None:
    """Ensures an IP address can't have more than X jobs running at once"""
    # TODO consider using Celery Que to maintain list
    # TODO if a Celery task fails the que will not shorten until the Redis entry expires.
    client = get_redis_client(db_num=int(os.environ.get('REDIS_DB_IP')))

    # Decode Redis value into a list and handles potential exceptions
    try:
        que_info = [item.decode() for item in client.lrange(ip_address, 0, -1)]
        que_count = client.llen(ip_address)
    except redis.ResponseError:
        logging.error(f'Redis issue with query {ip_address}')
        raise HTTPException(
            HTTP_429_TOO_MANY_REQUESTS, f"Too Many Requests"
        )

    logging.info(f'Initial Que found from key {ip_address}: {que_info}')
    if not que_info:
        logging.info(f'Creating initial entry for IP quota/endpoint throttling: {ip_address} Job: {job_uuid}')
        client.rpush(ip_address, job_uuid) and client.expire(ip_address, 1200)
        return None

    if que_count >= limit:
        logging.info(f'Denied user {ip_address} from submitting more than {que_count} jobs')
        raise HTTPException(
            HTTP_429_TOO_MANY_REQUESTS, f"Too Many Requests. You already have {que_count} jobs in que"
        )

    # Add job to que and set expire to 20 minutes
    client.rpush(ip_address, job_uuid) and client.expire(ip_address, 1200)
    logging.info(f'Added job {job_uuid} to {ip_address}. Currently have {que_count} submitted jobs in que')
