from datetime import datetime
from time import perf_counter

from server.crawl_server import CrawlServer
from server.http_server import HttpServer


def main():
    http = HttpServer()
    try:
        CrawlServer(http).run()
    finally:
        http.close()


if __name__ == "__main__":
    started_at = datetime.now().astimezone()
    started = perf_counter()
    print(f"開始時間：{started_at.isoformat(timespec='seconds')}")
    try:
        raise SystemExit(main())
    finally:
        print(f"結束時間：{datetime.now().astimezone().isoformat(timespec='seconds')}")
        print(f"總耗時：{perf_counter() - started:.2f} 秒")
