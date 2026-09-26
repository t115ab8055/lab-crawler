from urllib.parse import parse_qs, urljoin, urlsplit

from bs4 import BeautifulSoup, Tag

from schemas.forum_list import ForumListItem

BASE_URL = "https://0800280280.sme.gov.tw/accounting/run.php"
LIST_URL = BASE_URL + "?name=forum&file=forum_list&csId=B&fId=15&page={}"


class ForumListServer:
    """解析列表表格，回傳已回覆資料；結構錯誤直接拋出。"""

    def parse_forum_list(self, html: str) -> list[ForumListItem]:
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select(".search-list > table > tbody > tr")
        return self._parse_rows(rows)

    def _parse_rows(self, rows: list[Tag]) -> list[ForumListItem]:
        records: list[ForumListItem] = []
        for row in rows:
            if record := self._parse_row(row):
                records.append(record)
        return records

    def _parse_row(self, row: Tag) -> ForumListItem | None:
        status = self._reply_status(row)
        if "已回覆" in status:
            return self._build_record(row, status)
        return None

    def _reply_status(self, row: Tag) -> str:
        node = row.select_one('td[data-title="會計師回覆狀態"]')
        return node.get_text(" ", strip=True)

    def _build_record(self, row: Tag, status: str) -> ForumListItem:
        fields = self._link_fields(row)
        fields.update(reply_status=status, published_at=self._published_at(row))
        return ForumListItem(**fields)

    def _link_fields(self, row: Tag) -> dict[str, str]:
        link = self._detail_link(row)
        url = urljoin(BASE_URL, str(link["href"]))
        return {"id": self._parse_id(url), "title": link.get_text(strip=True), "url": url}

    def _detail_link(self, row: Tag) -> Tag:
        return row.select_one('td[data-title="問題標題"] a[href]')

    def _parse_id(self, url: str) -> str:
        return parse_qs(urlsplit(url).query, keep_blank_values=True)["p"][0]

    def _published_at(self, row: Tag) -> str:
        node = row.select_one('td[data-title="發表時間"]')
        return node.get_text(strip=True)
