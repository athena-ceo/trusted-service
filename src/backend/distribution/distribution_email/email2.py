from pydantic import BaseModel
from typing import Optional, List, Union


class Email(BaseModel):
    from_email_address: str
    # accept a single address (str) or a list of addresses
    to_email_address: Union[str, List[str]]
    subject: str
    body: str
    # optional list of BCC addresses
    bcc_email_address: Optional[List[str]] = None
