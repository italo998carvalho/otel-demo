import uvicorn
from typing import Union
from fastapi import FastAPI, Response
from pydantic import BaseModel
import requests
from otel import start_span
from opentelemetry.propagate import inject
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI()
base_url = 'http://127.0.0.1:8001'

class Item(BaseModel):
    item_id: int
    name: str
    price: float
    is_offer: Union[bool, None] = None

@app.get('/')
def read_root():
    return {'Application': 'Client'}

@app.get('/items')
@start_span('list-items')
def list_items(response: Response):
    endpoint = base_url + '/items'
    r = requests.get(endpoint, headers=_injected_headers())
    
    response.status_code = r.status_code
    return r.json()

@app.get('/items/{item_id}')
@start_span('read-item')
def read_item(item_id: int, response: Response):
    endpoint = base_url + f'/items/{item_id}'
    r = requests.get(endpoint, headers=_injected_headers())

    response.status_code = r.status_code
    return r.json()

@app.put('/items/{item_id}')
@start_span('update-item')
def update_item(item_id: int, item: Item, response: Response):
    endpoint = base_url + f'/items/{item_id}'
    r = requests.put(
        endpoint,
        json=_build_payload(item),
        headers=_injected_headers()
    )

    response.status_code = r.status_code
    return r.json()

@app.post('/items')
@start_span('create-item')
def create_item(item: Item, response: Response):
    endpoint = base_url + f'/items'
    r = requests.post(
        endpoint,
        json=_build_payload(item),
        headers=_injected_headers()
    )

    response.status_code = r.status_code
    return r.json()

@app.delete('/items/{item_id}')
@start_span('remove-item')
def remove_item(item_id: int, response: Response):
    endpoint = base_url + f'/items/{item_id}'
    r = requests.delete(endpoint, headers=_injected_headers())

    response.status_code = r.status_code
    return r.json()

def _build_payload(item: Item) -> dict[str, any]:
    return {
        'item_id': item.item_id,
        'name': item.name,
        'price': item.price,
        'is_offer': item.is_offer
    }

def _injected_headers():
    headers = {'traceparent': None}
    inject(headers)

    return headers

if __name__ == '__main__':
    FastAPIInstrumentor.instrument_app(app)
    uvicorn.run(app, host='127.0.0.1', port=8000)
