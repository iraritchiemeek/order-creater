from fastapi import FastAPI, Request, HTTPException
from openai import OpenAI
import json
import httpx
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

app = FastAPI()
client = OpenAI()

load_dotenv()
TE_PAPA_API_KEY = os.environ.get("TE_PAPA_API_KEY")
if not TE_PAPA_API_KEY:
    raise ValueError("TE_PAPA_API_KEY environment variable is not set")
TE_PAPA_API_URL = "https://data.tepapa.govt.nz/collection/search"

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
    query_url: Optional[str] = None

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
            print('///////')
            return SearchTePapaResponse(results=response.json().get("results", []), query_url=body)
        else:
            print('Failed to fetch data from Te Papa API:', response.status_code, response.text)
            return SearchTePapaResponse(results=[], query_url=body)

async def run_conversation(user_message: str) -> RunConversationResponse:
    if not user_message:
        raise HTTPException(status_code=400, detail="Message parameter is required")

    # Extract date_filter from user_message if applicable
    date_filter = None  # Set to None or extract from user_message if needed

    messages = [
        {"role": "system", "content": "You are a helpful assistant for searching the Te Papa collections."},
        {"role": "user", "content": user_message}
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_te_papa",
                "description": "Search the Te Papa collections API. The function accepts a search query and an optional date filter. The date filter can be one of the following: 'century', 'decadeOfCentury', or 'year'. For example, '19th century', '1870s', or '1877'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        },
                        "date_filter": {
                            "type": "object",
                            "properties": {
                                "facetCreatedDate.century": {
                                    "type": "string",
                                    "description": "The century of the creation date, e.g., '19th century'"
                                },
                                "facetCreatedDate.decadeOfCentury": {
                                    "type": "string",
                                    "description": "The decade of the creation date, e.g., '1870s'"
                                },
                                "facetCreatedDate.year": {
                                    "type": "string",
                                    "description": "The exact year of the creation date, e.g., '1877'"
                                }
                            }
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        available_functions = {
            "search_te_papa": search_te_papa,
        }
        messages.append(response_message)
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            print(tool_call.function.arguments)
            print('/////////')
            function_args = json.loads(tool_call.function.arguments)
            print(function_args)
            # Convert date_filter back to DateFilter object if it exists
            if "date_filter" in function_args and function_args["date_filter"]:
                function_args["date_filter"] = DateFilter(**function_args["date_filter"])
            
            function_response = await function_to_call(**function_args)
            results = function_response.results
            return RunConversationResponse(
                response=response_message.content or "No response content",
                results=results,
                query_url=function_args
            )
    return RunConversationResponse(
        response=response_message.content or "No response content",
        results=[],
        query_url=None
    )

@app.get("/api/chat")
async def chat(request: Request):
    user_message = request.query_params.get("message")
    if not user_message:
        raise HTTPException(status_code=400, detail="Message parameter is required")
    response = await run_conversation(user_message)
    return response
