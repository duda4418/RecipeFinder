from __future__ import annotations

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from utils.settings import Settings


def create_http_session(settings: Settings) -> requests.Session:
    retry = Retry(
        total=settings.HTTP_MAX_RETRIES,
        connect=settings.HTTP_MAX_RETRIES,
        read=settings.HTTP_MAX_RETRIES,
        status=settings.HTTP_MAX_RETRIES,
        backoff_factor=settings.HTTP_BACKOFF,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)

    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session
