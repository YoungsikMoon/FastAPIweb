# pip install fastapi
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
# pip install Jinja2==3.1.2
from fastapi.templating import Jinja2Templates
# pip install "uvicorn[standard]"
import uvicorn
# pip install python-multipart
from typing_extensions import Annotated
# pip install SQLAlchemy==1.4.0
# pip install mysqlclient
from sqlalchemy import create_engine

templates = Jinja2Templates(directory = "templates")

app = FastAPI()

@app.get("/")
def hello():
    return {"message":"안녕"}

@app.get("/test")
def test(request: Request):
    print(request)
    return templates.TemplateResponse("test.html", context={'request' : request, 'a':2})

@app.get("/test/{name}")
def test_name(request: Request, name: str):
    print(name)
    return templates.TemplateResponse("test.html", {'request' : request, 'a':name})

@app.get("/test_get")
def test_get(request: Request):
    return templates.TemplateResponse("test_get.html", {"request" : request})

@app.post("/test_post")
def test_post(request: Request, name: Annotated[str, Form()], pwd: Annotated[str, Form()]):
    print(name, pwd)
    return templates.TemplateResponse("test_post.html", {"request" : request, 'name':name, 'pwd':pwd})

# 데이터셋 참고 : https://github.com/shiny0510/Oracle_Table_exam/blob/main/%EC%B5%9C%EC%A2%85%EC%88%98%EC%A0%951125.txt
db_connection = create_engine('mysql://root:1111@127.0.0.1:3306/alpaco9')

@app.get("/mysqltest")
def mysqltest(request: Request):
    query = db_connection.execute("select * from player")
    result_db = query.fetchall()
    result = []
    for data in result_db:
        temp = {'player_id' : data[0], 'player_name' : data[1]}
        result.append(temp)
    print('mysqltest 완료')
    return templates.TemplateResponse("sqltest.html", {'request':request, 'result_table' : result})


@app.get("/detail")
def detail(request: Request, id:str, name:str):
    query = db_connection.execute("select * from player where player_id = {} and player_name like '{}'".format(id,name))
    result_db = query.fetchall()
    result = []
    for i in result_db:
        temp = {'player_id' : i[0], 'player_name' : i[1], 'team_name':i[2], 'height':i[-2],'weight':i[-1]}
        result.append(temp)
    print('detail 완료')
    return templates.TemplateResponse("detail.html", {'request':request, 'result_table' : result})


@app.post("/update")
def update(
    request: Request, 
    id: str, 
    name: str, 
    pname: Annotated[str, Form()] = '', 
    tname: Annotated[str, Form()] = '', 
    weight: Annotated[int, Form()] = 0, 
    height: Annotated[int, Form()] = 0):
    print(pname, tname, weight, height)
    if pname != '':
        db_connection.execute(f"update player set player_name = '{pname}' where player_id = {id} and player_name like '{name}'")
        name = pname
    if tname != '':
        db_connection.execute(f"update player set tname = '{tname}' where player_id = {id} and player_name like '{name}'")
    if height != 0:
        db_connection.execute(f"update player set height = {height} where player_id = {id} and player_name like '{name}'")
    if weight != 0:
        db_connection.execute(f"update player set weight = {weight} where player_id = {id} and player_name like '{name}'")

    
    print('update 완료')
    return RedirectResponse(url="/mysqltest", status_code=303)


@app.get("/delete")
def delete(request: Request, id:str, name:str):
    db_connection.execute(f"delete from player where player_id = {id} and player_name like '{name}'")
    print('delete 완료')
    return RedirectResponse(url="/mysqltest", status_code=303)

if __name__ == '__main__':
    uvicorn.run(app, host="localhost", port=8000)