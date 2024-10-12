from pydantic import BaseModel
from typing import Optional, List


class SocialLinksQuery(BaseModel):
    facebook: Optional[List[str]] = None
    twitter: Optional[List[str]] = None
    linkedin: Optional[List[str]] = None
    instagram: Optional[List[str]] = None
