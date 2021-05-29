from typing import List, Optional
from pydantic import BaseModel

class File(BaseModel):
    id = int
    filename: str

