from fastapi import FastAPI, UploadFile, Form, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder 
from fastapi.staticfiles import StaticFiles
from typing import Annotated 
import sqlite3

# "db.db"라는 이름의 SQLite 데이터베이스 파일에 연결
con = sqlite3.connect('db.db', check_same_thread=False)
# 데이터베이스에 SQL 명령어를 실행하는 도구
cur = con.cursor()

cur.execute(f"""
            CREATE TABLE IF NOT EXISTS items (
	              id INTEGER PRIMARY KEY,
	              title TEXT NOT NULL,
	              image BLOB,
	              price INTEGER NOT NULL,
	              description TEXT,
	              place TEXT NOT NULL,
	              insertAt INTEGER NOT NULL
            );
            """)

app = FastAPI()

# "/items"라는 주소로 POST 요청이 들어오면 이 함수를 실행
# POST 요청 : 서버야! 이 정보 좀 저장해줘! 라는 요청
@app.post("/items")
# async는 "비동기 처리"를 위한 키워드. → 즉, 사진 파일을 읽는 동안 다른 작업도 할 수 있게 함
async def create_item(image: UploadFile,
                      title: Annotated[str, Form()],
                      price: Annotated[int, Form()],
                      description: Annotated[str, Form()],
                      place: Annotated[str, Form()],
                      insertAt: Annotated[int, Form()]
                      ):
  image_bites = await image.read()
  cur.execute(f"""
              INSERT INTO
              items(title, image, price, description, place, insertAt)
              VALUES
              ('{title}', '{image_bites.hex()}', {price}, '{description}', '{place}',{insertAt})
              """)
  con.commit()
  return "200"

@app.get("/items")
async def get_items():
  # 컬럼명도 같이 가져옴
  con.row_factory = sqlite3.Row
  cur = con.cursor()
  rows = cur.execute(f"""
                     SELECT * FROM items;
                    """).fetchall()
  return JSONResponse(jsonable_encoder([dict(row) for row in rows]))

# 이미지 요청
@app.get("/images/{item_id}")
async def get_image(item_id):
  cur = con.cursor()
  image_bytes = cur.execute(f"""
                            SELECT image FROM items WHERE id = {item_id}
                            """).fetchone()[0]
  return Response(content=bytes.fromhex(image_bytes))

app.mount("/", StaticFiles(directory="frontend", html=True),name="frontend")