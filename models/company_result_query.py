from pydantic import BaseModel
from typing import Optional, List
from models.social_links_query import SocialLinksQuery


class CompanyResultQuery(BaseModel):
    url: Optional[str]
    legal_name: Optional[str]
    commercial_names: Optional[List[str]]
    all_company_names: Optional[List[str]]
    phone_numbers: Optional[List[str]]
    social_links: Optional[SocialLinksQuery]
    score: Optional[float]
