from dotenv import load_dotenv
import os
import httpx
import json
from typing import Optional
from api.types import DateFilter, SearchTePapaResponse

load_dotenv()
TE_PAPA_API_KEY = os.environ.get("TE_PAPA_API_KEY")
if not TE_PAPA_API_KEY:
    raise ValueError("TE_PAPA_API_KEY environment variable is not set")
TE_PAPA_API_URL = "https://data.tepapa.govt.nz/collection/search"

async def search_te_papa(query: str, date_filter: Optional[DateFilter] = None) -> SearchTePapaResponse:
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': TE_PAPA_API_KEY
    }
    filters = []
    body = {
        "query": f"{query} AND collection:Photography AND _exists_:hasRepresentation",
        "defaultOperator": "AND",
        "size": 18,
        "filters": filters
    }
    if date_filter:
        for field, value in date_filter.dict(by_alias=True, exclude_unset=True).items():
            filters.append({
                "field": f"production.{field}",
                "keyword": value
            })
        body["filters"] = filters

    async with httpx.AsyncClient() as client:
        print('Querying Te Papa API...')
        print(body)
        response = await client.post(TE_PAPA_API_URL, headers=headers, json=body)
        if response.status_code == 200:
            print(response)
            return SearchTePapaResponse(results=response.json().get("results", []), query_url=json.dumps(body))
        else:
            print('Failed to fetch data from Te Papa API:', response.status_code, response.text)
            return SearchTePapaResponse(results=[], query_url=json.dumps(body))