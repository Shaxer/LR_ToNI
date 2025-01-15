from pydantic import BaseModel
import datetime


class UserInfo(BaseModel):
    user_id: int
    user_name: str
    user_surname: str| None
    age: int | None 
    height: int | None
    weight: float | None
    time_of_add: datetime.datetime 
    is_actual: bool | None
    