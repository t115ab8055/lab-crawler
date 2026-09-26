from pathlib import Path

from schemas.forum_list import ForumListItem

from .export_server import ExportServer
from .forum_list_server import LIST_URL, ForumListServer
from .http_server import HttpServer


class CrawlServer:
    """依序抓取列表；錯誤直接拋出並中斷任務。"""

    def __init__(self, http: HttpServer, output_dir: str = "output") -> None:
        self.http = http
        self.output_dir = Path(output_dir)
        self.forum_list = ForumListServer()
        self.export = ExportServer()

    def run(self) -> None:
        records = self._crawl_pages()
        self.export.export_json(list(records.values()), self.output_dir / "forum_list.json")

    def _crawl_pages(self) -> dict[str, ForumListItem]:
        records: dict[str, ForumListItem] = {}
        for page in range(1, 8):
            response = self.http.get(LIST_URL.format(page))
            self._collect_records(self.forum_list.parse_forum_list(response.text), records)
        return records

    def _collect_records(
        self, incoming: list[ForumListItem], records: dict[str, ForumListItem]
    ) -> None:
        for record in incoming:
            if record.id in records:
                continue
            records[record.id] = record
