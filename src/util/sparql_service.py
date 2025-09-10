import requests
import time
import random

from src.config.config import (
    logger,
    DEFAULT_USER_AGENT,
    USER_AGENTS,
    TIMEOUT,
    MAX_RETRIES,
    BASE_DELAY,
)


def get_headers(rotating_user_agent=True):
    if rotating_user_agent:
        return {
            "Accept": "application/json",
            "User-Agent": random.choice(USER_AGENTS),
        }
    return {
        "Accept": "application/json",
        "User-Agent": DEFAULT_USER_AGENT,
    }


def execute_request_with_retries(url, params, rotating_user_agent):
    headers = get_headers(rotating_user_agent)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if attempt == MAX_RETRIES:
                raise
            wait = BASE_DELAY * attempt
            logger.warning(
                f"Request failed (attempt {attempt}): {e}. Retrying in {wait}s…"
            )
            time.sleep(wait)


def run_sparql(url, query, rotating_user_agent):
    return execute_request_with_retries(url, {"query": query}, rotating_user_agent)
