from app import create_app

# flask cli 는 기본적으로 app.py 에서 app 이라는 이름의 flask 인스턴스를 찾는다. 그래서 변수명이 app.
app = create_app()
