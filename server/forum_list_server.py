import re
from urllib.parse import parse_qs, urljoin, urlsplit

from bs4 import BeautifulSoup


BASE_URL = "https://0800280280.sme.gov.tw/accounting/run.php"
LIST_URL = BASE_URL + "?name=forum&file=forum_list&csId=B&fId=15&page={}"


class ForumListServer:
    """解析列表表格，回傳已回覆資料；結構錯誤直接拋出。"""

    def parse_forum_list(self, html):
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select(".search-list > table > tbody > tr")
        if not rows:
            raise ValueError("找不到列表資料列")
        return self._parse_rows(rows)

    def _parse_rows(self, rows):
        records = []
        for row in rows:
            record = self._parse_row(row)
            if record is not None:
                records.append(record)
        return records

    def _parse_row(self, row):
        status = self._reply_status(row)
        if "已回覆" not in status:
            return None
        return self._build_record(row, status)

    def _reply_status(self, row):
        node = row.select_one('td[data-title="會計師回覆狀態"]')
        if node is None:
            raise ValueError("缺少回覆狀態欄位")
        return node.get_text(" ", strip=True)

    def _build_record(self, row, status):
        link = row.select_one('td[data-title="問題標題"] a[href]')
        url = self._detail_url(link)
        record = dict(id=self._parse_id(url), title=link.get_text(strip=True), url=url)
        record.update(reply_status=status, published_at=self._published_at(row))
        return record

    def _detail_url(self, link):
        if link is None or not link.get_text(strip=True):
            raise ValueError("缺少問題標題或詳情連結")
        return urljoin(BASE_URL, link["href"])

    def _parse_id(self, url):
        values = parse_qs(urlsplit(url).query, keep_blank_values=True).get("p", [])
        if len(values) != 1 or re.fullmatch(r"[0-9]+", values[0]) is None:
            raise ValueError("詳情 URL 缺少合法且唯一的 p 參數")
        return values[0]

    def _published_at(self, row):
        node = row.select_one('td[data-title="發表時間"]')
        return (node.get_text(strip=True) or None) if node is not None else None
