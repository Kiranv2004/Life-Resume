from pydantic import BaseModel


class ReportOut(BaseModel):
    report_url: str
