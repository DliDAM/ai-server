from typing import Union
from fastapi import FastAPI, UploadFile, File, Form
from routers import websocket
from fastapi.responses import FileResponse
import os
import shutil


app = FastAPI()
#app.include_router(websocket.router)
path = './templates/index.html'
audio_path = './templates/audio.html'
audio_file_path = './templates/audio_file.html'
text_to_audio_path = './templates/texttoaudio.html'

@app.get("/")
async def get():
    return FileResponse(text_to_audio_path)

@app.post("/audio")
async def upload_audio(audio_file: UploadFile = File(...), user_id: str = Form(...)):
    # 사용자 ID를 기반으로 저장 디렉토리 설정
    save_directory = f"tortoise/tortoise/voices/{user_id}"
    
    # 디렉토리가 없으면 생성
    os.makedirs(save_directory, exist_ok=True)
    
    # 파일 저장
    file_path = os.path.join(save_directory, audio_file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)
    
    return {"message": f"사용자 {user_id}의 오디오 파일이 성공적으로 업로드되었습니다.", "file_name": audio_file.filename, "user_id": user_id}

