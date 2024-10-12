from fastapi import FastAPI

from controllers.company_controller import CompanyController

app = FastAPI(
    title = "Company Finder API",
    description = "Find a company by its name, website, phone number and facebook profile.",
    version = "0.1",
    docs_url = "/",
)


company_controller = CompanyController(app)
company_controller.register()