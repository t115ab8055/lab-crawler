from pydantic import BaseModel


class ForumListItem(BaseModel):
    id: str
    title: str
    url: str
    reply_status: str
    published_at: str
