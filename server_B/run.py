import uvicorn
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(port=8001)

class Item(BaseModel):
    item_id: int
    name: str
    price: float
    is_offer: Union[bool, None] = None

item_list = {}

@app.get("/")
def read_root():
    return {"Server": "B"}

@app.get("/items")
def list_items():
    return [x.model_dump() for x in item_list.values()]

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return item_list.get(item_id, {})

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    item.item_id = item_id
    item_list[item_id] = item
    return "updated"

@app.post("/items")
def update_item(item: Item):
    item_list[item.item_id] = item
    return "created"

@app.delete("/items/{item_id}")
def remove_item(item_id: int):
    if item_id in item_list:
        item_list.pop(item_id)
        return "deleted"
    else:
        return "not found"
    
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
