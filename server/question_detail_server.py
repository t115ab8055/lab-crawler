import re
from copy import deepcopy
from datetime import datetime

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

from schemas.forum_list import ForumListItem
from schemas.question_detail import Answer, QuestionDetail


class QuestionDetailServer:
    """依已確認的問題、回答與說明節點解析詳情。"""

    def parse_question_detail(self, html: str, list_item: ForumListItem) -> QuestionDetail:
        soup = BeautifulSoup(html, "html.parser")
        fields = self._question_fields(soup.select_one(".qa > ul.question"))
        fields.update(answers=self._parse_answers(soup))
        fields.update(fetched_at=datetime.now().astimezone().isoformat())
        return QuestionDetail.model_validate(list_item.model_dump() | fields)

    def _question_body(self, question: Tag) -> Tag:
        return question.find_all("li", recursive=False)[1]

    def _question_fields(self, question: Tag) -> dict[str, object]:
        body = self._question_body(question)
        fields: dict[str, object] = self._question_metadata(question)
        fields.update(question=self._clean_text(body, "Q："))
        fields.update(question_raw_html=str(body))
        return fields

    def _question_metadata(self, question: Tag) -> dict[str, object]:
        labels = {
            "asker_name": "姓名",
            "industry": "行業別",
            "region": "區域",
            "asked_at": "詢問日期",
        }
        fields = self._metadata_fields(question, labels)
        views = self._metadata(question, "點閱次數")
        fields["view_count"] = int(views.replace(",", ""))
        return fields

    def _metadata_fields(self, node: Tag, labels: dict[str, str]) -> dict[str, object]:
        return {key: self._metadata(node, label) for key, label in labels.items()}

    def _metadata(self, node: Tag, label: str) -> str:
        texts = (row.get_text(strip=True) for row in node.find_all("li", recursive=False))
        text = next(text for text in texts if text.startswith(label))
        return text.removeprefix(label).lstrip("：: ")

    def _parse_answers(self, soup: BeautifulSoup) -> list[Answer]:
        blocks = soup.select(".qa > ul.answer")
        return [self._parse_answer(block, order) for order, block in enumerate(blocks, 1)]

    def _parse_answer(self, block: Tag, order: int) -> Answer:
        body = block.select_one("p.detail")
        fields = self._answer_fields(block)
        fields.update(order=order, raw_html=str(body))
        fields.update(self._answer_content(body))
        return Answer.model_validate(fields)

    def _answer_fields(self, block: Tag) -> dict[str, object]:
        names = block.select(".accountant > p")
        fields: dict[str, object] = {"answered_at": self._metadata(block, "回覆日期")}
        fields["accountant_name"] = names[0].get_text(strip=True)
        fields["accountant_role"] = names[1].get_text(strip=True)
        return fields

    def _answer_content(self, body: Tag) -> dict[str, object]:
        clean = deepcopy(body)
        notices = clean.select(':scope > span[style="font-size:10px"]')
        notice_text = self._notice_text(notices)
        return {"text": self._clean_text(clean, "A："), "notice_text": notice_text}

    def _notice_text(self, notices: list[Tag]) -> str:
        return "\n".join(self._plain_text(node.extract()) for node in notices)

    def _clean_text(self, node: Tag, prefix: str) -> str:
        return self._plain_text(node).removeprefix(prefix).strip()

    def _plain_text(self, node: Tag) -> str:
        return self._render_node(node).strip()

    def _render_node(self, node: Tag | NavigableString) -> str:
        if isinstance(node, Comment):
            return ""
        if isinstance(node, NavigableString):
            return self._render_string(node)
        return self._render_tag(node)

    def _render_tag(self, node: Tag) -> str:
        if node.name == "br":
            return "\n"
        text = "".join(self._render_node(child) for child in node.children)
        return f"\n{text}\n" if node.name in {"p", "div", "li", "ul", "ol"} else text

    def _render_string(self, node: NavigableString) -> str:
        text = re.sub(r"\n[ \t]+", "", str(node).replace("\r\n", "\n")).strip("\t")
        if "\n" in text and text.isspace():
            return ""
        previous = node.previous_sibling
        return text.lstrip("\n") if isinstance(previous, Tag) and previous.name == "br" else text
