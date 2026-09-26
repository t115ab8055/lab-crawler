import os
import random
import time

import requests

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36"
)

DEFAULT_ACCEPT = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"


class HttpServer:
    def __init__(self, interval_min: float = 2.0, interval_max: float = 3.0) -> None:
        self.interval = (interval_min, interval_max)
        self._last_finished: float | None = None
        self.session = requests.Session()
        self._configure_headers()

    def _configure_headers(self) -> None:
        self.session.headers.update({"Accept-Language": "zh-TW,zh;q=0.9"})
        self.session.headers["User-Agent"] = DEFAULT_USER_AGENT
        self.session.headers["Accept"] = DEFAULT_ACCEPT

    def close(self) -> None:
        self.session.close()

    def get(self, url: str) -> requests.Response:
        self._wait_for_interval()
        response = self.session.get(url)
        self._last_finished = time.monotonic()
        response.raise_for_status()
        return response

    def _wait_for_interval(self) -> None:
        if self._last_finished is None:
            return
        interval = random.uniform(*self.interval)
        elapsed = time.monotonic() - self._last_finished
        time.sleep(max(0.0, interval - elapsed))
