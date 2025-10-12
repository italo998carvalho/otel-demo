import uvicorn
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()
base_url = 'http://127.0.0.1:8000'

class Item(BaseModel):
    item_id: int
    name: str
    price: float
    is_offer: Union[bool, None] = None

@app.get("/")
async def read_root():
    return {"Server": "A"}

@app.get("/items")
async def list_items():
    endpoint = base_url + '/items'
    return requests.get(endpoint)

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    endpoint = base_url + f'/items/{item_id}'
    return requests.get(endpoint)

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    endpoint = base_url + f'/items/{item_id}'
    return requests.put(endpoint, json=item)

@app.post("/items")
async def update_item(item: Item):
    endpoint = base_url + f'/items'
    return requests.post(endpoint, json=item)

@app.delete("/items/{item_id}")
async def remove_item(item_id: int):
    endpoint = base_url + f'/items/{item_id}'
    return requests.delete(endpoint)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
