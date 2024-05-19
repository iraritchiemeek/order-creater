from fastapi import FastAPI, Request, HTTPException
from openai import OpenAI
import json
from api.types import DateFilter, RunConversationResponse
from typing import Optional, List, Dict
from api.te_papa_api import search_te_papa

app = FastAPI()
client = OpenAI()

# In-memory storage for conversation history
conversation_history: List[Dict[str, str]] = []

async def run_conversation(user_message: str) -> RunConversationResponse:
    if not user_message:
        raise HTTPException(status_code=400, detail="Message parameter is required")

    # Add the new user message to the history
    conversation_history.append({"role": "user", "content": user_message})

    messages = [
        {"role": "system", "content": "You are a helpful assistant that is an expert at querying museums archive APIs. Always include all relevant context provided by the user in your queries. If the query seems too broad, prompt the user for additional context that could be provided to return better results before making any function calls. Ensure that location-specific information, such as 'Wellington', is included in the search query if mentioned by the user. Make sure the search query is descriptive enough to provide relevant results."},
    ] + conversation_history

    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_te_papa",
                "description": "Search the Te Papa collections API. The function accepts a search query and an optional date filter. The date filter can be one of the following: 'century', 'decadeOfCentury', or 'year'. For example, '19th century', '1870s', or '1877'. Ensure the search query is descriptive and includes any location-specific information provided by the user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "A descriptive text search query that includes all relevant context and location-specific information"
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
            function_args = json.loads(tool_call.function.arguments)
            print(function_args)
            # Convert date_filter back to DateFilter object if it exists
            if "date_filter" in function_args and function_args["date_filter"]:
                function_args["date_filter"] = DateFilter(**function_args["date_filter"])
            
            function_response = await function_to_call(**function_args)
            results = function_response.results

            # Add the assistant's response to the history
            conversation_history.append({"role": "assistant", "content": response_message.content})

            return RunConversationResponse(
                response=response_message.content or json.dumps(function_args, default=lambda o: o.dict() if isinstance(o, DateFilter) else o),
                results=results,
            )
    return RunConversationResponse(
        response=response_message.content or "No response content",
        results=[]
    )

@app.get("/api/chat")
async def chat(request: Request):
    user_message = request.query_params.get("message")
    if not user_message:
        raise HTTPException(status_code=400, detail="Message parameter is required")
    response = await run_conversation(user_message)
    return response
