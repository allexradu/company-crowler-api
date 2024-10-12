from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class WebsiteData:
    url: str
    phone_numbers: Optional[List[str]] = field(default_factory = list)
    social_links: Optional[Dict[str, List[str]]] = field(default_factory = dict)
    contact_page: Optional[str] = None
    error: Optional[str] = None
