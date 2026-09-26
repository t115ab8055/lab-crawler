from pydantic import BaseModel

from schemas.forum_list import ForumListItem


class Answer(BaseModel):
    order: int
    accountant_name: str
    accountant_role: str
    answered_at: str
    text: str
    raw_html: str
    notice_text: str


class QuestionDetail(ForumListItem):
    question: str
    question_raw_html: str
    asker_name: str
    industry: str
    region: str
    asked_at: str
    view_count: int
    answers: list[Answer]
    fetched_at: str
