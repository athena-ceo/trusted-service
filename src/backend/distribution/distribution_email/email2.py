from pydantic import BaseModel


class Email(BaseModel):
    from_email_address: str
    to_email_address: str
    subject: str
    body: str
