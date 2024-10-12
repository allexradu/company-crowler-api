from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional
from fastapi import HTTPException
import re


class CompanyQuery(BaseModel):
    company_name: Optional[str] = None
    website: Optional[HttpUrl] = None
    phone_number: Optional[str] = None
    facebook_profile: Optional[str] = None

    @field_validator('website')
    def change_https_to_http(cls, website_url):
        website_url_str = str(website_url)
        if website_url_str.startswith("https://"):
            return website_url_str.replace("https://", "http://", 1)
        return website_url_str

    @field_validator('facebook_profile')
    def validate_facebook_profile(cls, facebook_profile):
        if facebook_profile and not re.match(r'^facebook\.com\/[a-zA-Z0-9.-]+$', facebook_profile):
            raise HTTPException(
                status_code = 422,
                detail = [
                    {
                        "type": "value_error",
                        "loc": ["query", "facebook_profile"],
                        "msg": 'Invalid Facebook profile URL, should be in the format "facebook.com/username"',
                        "input": facebook_profile,
                        "ctx": {
                            "error": 'Invalid Facebook profile URL, should be in the format "facebook.com/username"'
                        }
                    }
                ]
            )
        return facebook_profile

    @field_validator('phone_number')
    def clean_phone_number(cls, phone_number):
        if phone_number:
            return re.sub(r'[^\d+]', '', phone_number)
