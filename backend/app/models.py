from pydantic import BaseModel


class UsernameBody(BaseModel):
    username: str


class MessageBody(BaseModel):
    from_user: str
    to_user: str
    content: str
