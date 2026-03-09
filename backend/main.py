import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

import aiosqlite
import bcrypt
import jwt
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

DB_FILE = "data/vault.db"
STORAGE_DIR = "data/vault_data"
SECRET_KEY = "lmao-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


class UserCreate(BaseModel):
    username: str
    password: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@asynccontextmanager
async def lifespan(_: FastAPI):
    os.makedirs(STORAGE_DIR, exist_ok=True)
    async with aiosqlite.connect(DB_FILE, timeout=20) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                size INTEGER NOT NULL,
                uploader TEXT NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/me")
async def verify_token(current_user: str = Depends(get_current_user)):
    return {"username": current_user}


@app.post("/login")
async def login(user: UserCreate):
    async with aiosqlite.connect(DB_FILE, timeout=20) as db:
        async with db.execute(
            "SELECT password_hash FROM users WHERE username = ?", (user.username,)
        ) as cursor:
            row = await cursor.fetchone()

            if not row or not verify_password(user.password, row[0]):
                raise HTTPException(
                    status_code=401, detail="Incorrect username or password"
                )

            access_token = create_access_token(data={"sub": user.username})
            return {"access_token": access_token, "token_type": "bearer"}


@app.get("/files")
async def list_files(_: str = Depends(get_current_user)):
    async with aiosqlite.connect(DB_FILE, timeout=20) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT id, filename, size, uploader, upload_date 
            FROM files 
            ORDER BY upload_date DESC
        """) as cursor:
            rows = await cursor.fetchall()
            return {"files": [dict(row) for row in rows]}


@app.post("/files")
async def handle_upload(
    files: list[UploadFile] = File(...), current_user: str = Depends(get_current_user)
):
    uploaded_records = []

    async with aiosqlite.connect(DB_FILE, timeout=20) as db:
        for file in files:
            if not file.filename:
                continue

            file_path = os.path.join(STORAGE_DIR, file.filename)
            content = await file.read()

            with open(file_path, "wb") as f:
                f.write(content)

            await db.execute(
                "INSERT INTO files (filename, size, uploader) VALUES (?, ?, ?)",
                (file.filename, len(content), current_user),
            )
            uploaded_records.append({"filename": file.filename, "size": len(content)})

        await db.commit()

    return {
        "message": f"Upload successful by {current_user}",
        "files": uploaded_records,
    }


@app.get("/file/{id}")
async def fetch_file(id: int, _: str = Depends(get_current_user)):
    async with aiosqlite.connect(DB_FILE, timeout=20) as db:
        async with db.execute(
            "SELECT filename FROM files WHERE id = ?", (id,)
        ) as cursor:
            row = await cursor.fetchone()

            if not row:
                raise HTTPException(
                    status_code=404, detail="File record not found in database"
                )

            filename = row[0]
            file_path = os.path.join(STORAGE_DIR, filename)

            if not os.path.exists(file_path):
                raise HTTPException(
                    status_code=404, detail="Physical file missing from vault"
                )

            return FileResponse(
                path=file_path, filename=filename, media_type="application/octet-stream"
            )


@app.delete("/file/{id}")
async def delete_file(id: int, current_user: str = Depends(get_current_user)):
    async with aiosqlite.connect(DB_FILE, timeout=20) as db:
        async with db.execute(
            "SELECT filename, uploader FROM files WHERE id = ?", (id,)
        ) as cursor:
            row = await cursor.fetchone()

            if not row:
                raise HTTPException(
                    status_code=404, detail="File record not found in database"
                )

            filename = row[0]
            uploader = row[1]

            if current_user != uploader:
                raise HTTPException(
                    status_code=403, detail="You can only delete your own files"
                )

            file_path = os.path.join(STORAGE_DIR, filename)

            if os.path.exists(file_path):
                os.remove(file_path)

            await db.execute("DELETE FROM files WHERE id = ?", (id,))
            await db.commit()

            return {"message": f"File '{filename}' successfully deleted"}
