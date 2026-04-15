from pydantic import BaseModel, field_validator


class RegisterBody(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_valid(cls, v):
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Le pseudo doit contenir au moins 2 caractères")
        return v

    @field_validator("password")
    @classmethod
    def password_valid(cls, v):
        if len(v) < 4:
            raise ValueError("Le mot de passe doit contenir au moins 4 caractères")
        return v


class LoginBody(BaseModel):
    username: str
    password: str


class UsernameBody(BaseModel):
    username: str


class MessageBody(BaseModel):
    from_user: str
    to_user: str
    content: str
