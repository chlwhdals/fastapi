from fastapi import FastAPI, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from starlette.middleware.sessions import SessionMiddleware

# FastAPI 앱 생성
app = FastAPI()

# 세션을 위한 비밀키 설정
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

# Static 및 Templates 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# SQLite 데이터베이스 설정
DATABASE_URL = "sqlite:///./test.db"  # 데이터베이스 파일 이름
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 사용자 모델 정의
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

# 데이터베이스 초기화
Base.metadata.create_all(bind=engine)

# 의존성: 데이터베이스 세션 생성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 메인 페이지
@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    username = request.session.get("username")
    if username:
        return templates.TemplateResponse("main.html", {"request": request, "username": username})
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

# 로그인 처리
@app.post("/login")
async def login(
    request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if user and user.password == password:
        request.session["username"] = username
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})

# 로그아웃
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)

# 회원가입 페이지
@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

# 회원가입 처리
@app.post("/signup")
async def signup(
    request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if user:
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Username already exists"})
    new_user = User(username=username, password=password)
    db.add(new_user)
    db.commit()
    return RedirectResponse("/", status_code=302)
