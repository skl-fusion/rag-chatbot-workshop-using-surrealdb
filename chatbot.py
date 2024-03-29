#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: chatbot.py
Description: Facilitates a chatbot that utilizes OpenAI's API for understanding and responding to user queries within the context of Shakespearean works. 
The script processes user inputs, generates responses using a combination of OpenAI's GPT models, custom logic, and queries a SurrealDB database for text segments using cosine similarity of text embeddings. 
It's designed for applications requiring nuanced text interpretation and response generation, such as educational tools, literary exploration interfaces, or interactive entertainment experiences. 

Note: This script is structured to demonstrate an integration of AI and database technologies for creating responsive and context-aware chat applications. It simulates dialogues and utilizes environmental variables for configuration.
"""
import asyncio
import json
import os
from surrealdb import Surreal
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
client = OpenAI(api_key=OPENAI_API_KEY)
collection_name = "text_embeddings"
text_field_name="text"
embedding_field_name="embedding"

async def create_embedding(client, query_string, model="text-embedding-3-small"):
    response = client.embeddings.create(input=query_string, model=model)
    query_embedding = response.data[0].embedding
    return query_embedding

async def search_embeddings(db, query_embedding, top_n, collection_name=collection_name, embedding_field_name=embedding_field_name , additional_fields="*", order_by="cosine_similarity DESC"):
    select_fields = f"{additional_fields}, vector::similarity::cosine({embedding_field_name}, {query_embedding}) as cosine_similarity"
    
    query = f"""
    SELECT {select_fields} 
    FROM {collection_name}
    ORDER BY {order_by}
    LIMIT {top_n};
    """
    results = await db.query(query)
    return results

async def query_database(query, top_n=1):
    async with Surreal("ws://localhost:8000/rpc") as db:
        await db.signin({"user": DB_USER, "pass": DB_PASSWORD})
        await db.use("test", "test")
        texts = []
        query_embedding = await create_embedding(client, query)
        search_results = await search_embeddings(db, query_embedding, top_n=top_n)
        for item in search_results[0]['result']:  # Adjusted to access nested 'result'
            text = item.get('text', 'N/A')  # Default to 'N/A' if not found
            cosine_similarity = item.get('cosine_similarity', 0)  # Default to 0 if not found
            texts.append({'text': text})
        return texts
    
messages=[
    {
    "role": "system",
    "content": "You have the tool `read_document`. Use `read_document` in the following circumstances:\n    -ALWAYS\n\nGiven a query that requires retrieval from the documentation, your turn will consist of two steps:\n1. Call the `read_document` command with a query string to retrieve information from the document.\n2. Write a response to the user based on the retrieved information.\n\nThe `read_document` command has the following format:\n    `read_document query: str` Retrieves information relevant to the query from the provided documentation. This tool is designed to access a broad range of information, ensuring responses are informed by the documentation’s content. \n\nYou are tasked with the role of a Shakespearean assistant, equipped with the ability to directly access and quote any part of Shakespeare's works. Your main responsibility is to always quote Shakespeare and respond in the style of Shakespeare.\n- Always be polite, professional, and respectful to users.\n- Provide accurate, clear, and concise information.\n- If you encounter a request that violates guidelines or you're unsure about, politely decline to provide the requested content or information.\n- Continuously learn from user interactions to improve your responses and the user experience."
    },
    {
    "role": "user",
    "content": "write 3 senteces about how amazing this tutorial has been, make sure its inspired by the works of shakespeare"
    }
]    
tools = [
    {
        "type": "function",
        "function": {
            "name": "read_documents",
            "description": "Retrieves documents based on a query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query text.",
                    },
                },
                "required": ["query"],
            },
        },
    },
]


async def run_conversation(messages,tools):
    has_tool_calls = True

    while has_tool_calls:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if not tool_calls:
            has_tool_calls = False
            messages.append(response_message)
        else:
            available_functions = {
                "read_documents": query_database,
            }
            messages.append(response_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions.get(function_name)
                if function_to_call:
                    function_args = json.loads(tool_call.function.arguments)
                    if function_name == "read_documents":
                        function_response = await function_to_call(function_args.get("query"))
                        function_response = json.dumps({"text": function_response})
                        messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response,
                        }
                    )

    return messages

if __name__ == "__main__":
    print(asyncio.run(run_conversation(messages,tools)))
