from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class DateFilter(BaseModel):
    facetCreatedDate_century: Optional[str] = Field(None, alias="facetCreatedDate.century")
    facetCreatedDate_decadeOfCentury: Optional[str] = Field(None, alias="facetCreatedDate.decadeOfCentury")
    facetCreatedDate_year: Optional[str] = Field(None, alias="facetCreatedDate.year")

class SearchTePapaRequest(BaseModel):
    query: str
    date_filter: Optional[DateFilter] = None

class SearchTePapaResponse(BaseModel):
    results: List[Dict] = []
    query_url: str

class RunConversationRequest(BaseModel):
    user_message: str

class RunConversationResponse(BaseModel):
    response: str
    results: List[Dict] = []