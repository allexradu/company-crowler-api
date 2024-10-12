from fastapi import Depends, HTTPException

from db import DatabaseConnection
from models.company_query import CompanyQuery
from models.company_result_query import CompanyResultQuery


class CompanyController:
    def __init__(self, app):
        self.app = app
        self.db = DatabaseConnection().db

    def register(self):
        @self.app.get("/company")
        async def company(query: CompanyQuery = Depends()) -> CompanyResultQuery:
            must_not_conditions = [{"exists": {"field": "error"}}]
            should_conditions = []

            if query.website:
                should_conditions.append({"match_phrase": {"url": query.website.lower()}})
            if query.phone_number:
                should_conditions.append({
                    "wildcard": {
                        "phone_numbers": f"*{query.phone_number}*"
                    }
                })
            if query.company_name:
                should_conditions.append(
                    {"match": {"all_company_names": {"query": query.company_name, "operator": "and"}}})
                should_conditions.append(
                    {"fuzzy": {"all_company_names": {"value": query.company_name, "fuzziness": "AUTO"}}})
            if query.facebook_profile:
                should_conditions.append({"match": {"social_links.facebook": query.facebook_profile.lower()}})

            search_query = {
                "bool": {
                    "must_not": must_not_conditions,
                    "should": should_conditions,
                    "minimum_should_match": 1
                }
            }

            response = self.db.search(index = "website_data", body = {"query": search_query})

            if not response['hits']['hits']:
                raise HTTPException(status_code = 404, detail = "Company not found")

            return CompanyResultQuery(**response['hits']['hits'][0]['_source'])
