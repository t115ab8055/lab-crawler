from pathlib import Path

from pydantic import TypeAdapter

from schemas.forum_list import ForumListItem
from schemas.question_detail import QuestionDetail

from .export_server import ExportServer
from .forum_list_server import LIST_URL, ForumListServer
from .http_server import HttpServer
from .question_detail_server import QuestionDetailServer


class CrawlServer:
    """依序抓取列表；錯誤直接拋出並中斷任務。"""

    def __init__(self, http: HttpServer, output_dir: str = "output") -> None:
        self.http = http
        self.output_dir = Path(output_dir)
        self.forum_list = ForumListServer()
        self.export = ExportServer()
        self.question_detail = QuestionDetailServer()

    def run(self) -> None:
        records = self._crawl_pages()
        self.export.export_json(list(records.values()), self.output_dir / "forum_list.json")
        self.crawl_question_details()
        self.export_question_csv()

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

    def crawl_question_details(self) -> None:
        records: dict[str, QuestionDetail] = {}
        for item in self._read_forum_list():
            self._collect_detail(item, records)
        self.export.export_json(list(records.values()), self.output_dir / "question_details.json")

    def _read_forum_list(self) -> list[ForumListItem]:
        content = (self.output_dir / "forum_list.json").read_text(encoding="utf-8")
        return TypeAdapter(list[ForumListItem]).validate_json(content)

    def _collect_detail(self, item: ForumListItem, records: dict[str, QuestionDetail]) -> None:
        if item.id in records:
            return
        response = self.http.get(item.url)
        records[item.id] = self.question_detail.parse_question_detail(response.text, item)

    def export_question_csv(self) -> None:
        content = (self.output_dir / "question_details.json").read_text(encoding="utf-8")
        records = TypeAdapter(list[QuestionDetail]).validate_json(content)
        self.export.export_qa_csv(records, self.output_dir / "qa.csv")
