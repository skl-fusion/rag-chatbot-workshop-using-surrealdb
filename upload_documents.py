#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: upload_documents.py
Description: Automates the process of downloading a large text document, in this case, the complete works of William Shakespeare,
             from a specified URL. The script chunks the text into manageable pieces, generates text embeddings for each chunk
             using OpenAI's API, and uploads both the original text chunks and their corresponding embeddings to a SurrealDB database.
             It's designed for applications requiring text analysis and embedding-based text retrieval. Ensure environmental variables
             for database credentials and OpenAI API key are set correctly in a `.env` file.

Usage:
    Before running the script, make sure to configure the `.env` file with the required credentials (DB_USER, DB_PASSWORD, OPENAI_API_KEY).
    To run the script, execute `python upload_documents.py` from the command line. Ensure the SurrealDB server is running and accessible.
"""
import requests
import re
import os
import asyncio
from surrealdb import Surreal
from openai import OpenAI
from dotenv import load_dotenv

collection_name = "text_embeddings"
text_field_name="text"
embedding_field_name="embedding"
model="text-embedding-3-small"


def download_text(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to download the text. Status code: {response.status_code}")
        return ""

def chunk_text(text):
    chunks = re.split(r'(\r?\n){3}', text)
    non_empty_chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    return non_empty_chunks

async def create_embedding(openai_client, query_string, model=model):
    response = openai_client.embeddings.create(
        input=query_string,
        model=model
    )
    query_embedding = response.data[0].embedding
    return query_embedding

async def save_text_and_embedding(db, text, embedding, collection_name=collection_name, text_field_name=text_field_name, embedding_field_name=embedding_field_name):
    data = {
        text_field_name: text,
        embedding_field_name: embedding,
    }
    await db.create(collection_name, data)

async def db_info(db):
    query = f"INFO FOR DB;"
    try:
        results = await db.query(query)
        print(results)
    except Exception as e:
        print(f"There was a problem creating the index: {e}")

    query = f"INFO FOR TABLE ROOT;"
    try:
        results = await db.query(query)
        print(results)
    except Exception as e:
        print(f"There was a problem creating the index: {e}")

async def upload_text(db, openai_client, chunks, collection_name=collection_name, text_field_name=text_field_name, embedding_field_name=embedding_field_name, model=model):
    print(f"Uploading chunks... (this may take a while)")
    for chunk in chunks:
        try:
            embedding = await create_embedding(openai_client, chunk, model)
            await save_text_and_embedding(db, chunk, embedding, collection_name, text_field_name, embedding_field_name)
            print(f"Uploaded chunk: {chunk[:42]}...")
        except Exception as e:
            print(f"Failed to upload chunk. Error: {e}")
 
async def main():
    load_dotenv()
    url = "https://raw.githubusercontent.com/borkabrak/markov/master/Complete-Works-of-William-Shakespeare.txt"

    shakespeare_text = download_text(url)

    chunks = chunk_text(shakespeare_text)
    
    async with Surreal("ws://localhost:8000/rpc") as db:
        await db.signin({
            "user": os.getenv("DB_USER", "default_username"), 
            "pass": os.getenv("DB_PASSWORD", "default_password")
        })
        await db.use("test", "test")

        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        upload_task = asyncio.create_task(upload_text(db, openai_client, chunks))

        await upload_task
        await db_info(db)

if __name__ == "__main__":
    asyncio.run(main())