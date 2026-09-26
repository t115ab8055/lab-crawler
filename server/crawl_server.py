from pathlib import Path

from .export_server import ExportServer
from .forum_list_server import ForumListServer, LIST_URL


class CrawlServer:
    """依序抓取列表；錯誤直接拋出並中斷任務。"""

    def __init__(self, http, output_dir="output"):
        self.http = http
        self.output_dir = Path(output_dir)
        self.forum_list = ForumListServer()
        self.export = ExportServer()

    def run(self):
        records = self._crawl_pages()
        self.export.export_json(list(records.values()), self.output_dir / "forum_list.json")

    def _crawl_pages(self):
        records = {}
        for page in range(1, 8):
            response = self.http.get(LIST_URL.format(page))
            self._collect_records(self.forum_list.parse_forum_list(response.text), records)
        return records

    def _collect_records(self, incoming, records):
        for record in incoming:
            if record["id"] in records:
                continue
            records[record["id"]] = record
