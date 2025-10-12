import uvicorn
from typing import Union
from fastapi import FastAPI, Response, status
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
def read_item(item_id: int, response: Response):
    if item_id in item_list:
        return item_list.get(item_id)
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"status": "not found"}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item, response: Response):
    if item_id in item_list:
        item.item_id = item_id
        item_list[item_id] = item
        return {"status": "updated"}
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"status": "not found"}

@app.post("/items", status_code=201)
def update_item(item: Item):
    item_list[item.item_id] = item
    return {"status": "created"}

@app.delete("/items/{item_id}")
def remove_item(item_id: int, response: Response):
    if item_id in item_list:
        item_list.pop(item_id)
        return {"status": "deleted"}
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"status": "not found"}
    
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
