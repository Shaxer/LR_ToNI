import uvicorn
from fastapi import FastAPI, HTTPException
import os

from models import UserInfo

import json

app = FastAPI(debug=True)

TEXT_FILE_NAME = 'data.json'


@app.post("/users/", response_model=UserInfo)
async def create_user(user: UserInfo, ):
    user_response = user
    user_json = user.json()
    user_json = json.loads(user_json)
    user_id = user_json.get("user_id")
    if not user_json.get('is_actual'):
        raise HTTPException(403, detail='Not actual record')
    if not os.path.exists(TEXT_FILE_NAME):
        with open(TEXT_FILE_NAME, 'w') as f:
            json.dump([user_json], f, ensure_ascii=False, indent=4)
    else:
        json_records = None
        with open(TEXT_FILE_NAME, 'r') as f:
            json_records = json.load(f)
       
        records = []
        if json_records is not None and len(json_records) > 0:
            for i, record in enumerate(json_records):
                if record.get('user_id') == user_id:
                    record['is_actual'] = False
                records.append(record)
        
        json_records = records + [user_json]
        with open(TEXT_FILE_NAME, 'w') as f:
            json.dump(json_records, f, ensure_ascii=False, indent=4)

    return user_response


@app.get("/users/{user_id}", response_model=UserInfo)
async def get_user(user_id: int):
    data = None
    with open(TEXT_FILE_NAME, 'r') as f:
        data = json.load(f)
    data = list(filter(lambda x: x.get("user_id") == user_id and x.get('is_actual'), data))
    if len(data) < 1:
        raise HTTPException(status_code=404, detail="User not found")
    return data[0]


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    data = None
    with open(TEXT_FILE_NAME, 'r') as f:
        data = json.load(f)

    data = list(filter(lambda x: x.get("user_id") != user_id, data))

    try:
        with open(TEXT_FILE_NAME, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        pass


@app.put("/users/{user_id}")
async def update_user(user_id: int, user: UserInfo, ):
    user = json.loads(user.json())
    data = None
    with open(TEXT_FILE_NAME, 'r') as f:
        data = json.load(f)
    records = []
    if data is not None and len(data) > 0:
        for i, record in enumerate(data):
            if record.get("user_id") == user_id and  record.get('is_actual'):
                records.append(user)
            else:
                records.append(record)
        try:
            with open(TEXT_FILE_NAME, 'w') as f:
                json.dump(records, f, ensure_ascii=False, indent=4)
        except Exception as e:
            pass

if __name__ == "__main__":
      uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)