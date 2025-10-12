import uvicorn
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import requests
from otel import start_span

app = FastAPI()
base_url = 'http://127.0.0.1:8001'

class Item(BaseModel):
    item_id: int
    name: str
    price: float
    is_offer: Union[bool, None] = None

@app.get('/')
def read_root():
    return {'Server': 'A'}

@app.get('/items')
@start_span('list-items')
def list_items():
    endpoint = base_url + '/items'
    r = requests.get(endpoint)
    return r.json()

@app.get('/items/{item_id}')
@start_span('read-item')
def read_item(item_id: int, q: Union[str, None] = None):
    endpoint = base_url + f'/items/{item_id}'
    r = requests.get(endpoint)
    return r.json()

@app.put('/items/{item_id}')
@start_span('update-item')
def update_item(item_id: int, item: Item):
    endpoint = base_url + f'/items/{item_id}'
    r = requests.put(endpoint, json=_build_payload(item))
    return r.json()

@app.post('/items')
@start_span('create-item')
def create_item(item: Item):
    endpoint = base_url + f'/items'
    r = requests.post(endpoint, json=_build_payload(item))
    return r.json()

@app.delete('/items/{item_id}')
@start_span('remove-item')
def remove_item(item_id: int):
    endpoint = base_url + f'/items/{item_id}'
    r = requests.delete(endpoint)
    return r.json()

def _build_payload(item: Item) -> dict[str, any]:
    return {
        'item_id': item.item_id,
        'name': item.name,
        'price': item.price,
        'is_offer': item.is_offer
    }

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
