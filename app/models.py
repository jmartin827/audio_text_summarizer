from pydantic import BaseModel


# TODO create a model or two
class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None
