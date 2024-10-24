import asyncio
import json
import os
import uuid
import numpy as np
from scipy.io import wavfile
from fastapi import FastAPI, UploadFile, File, WebSocket
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from tortoise.api_fast import TextToSpeech
from tortoise.utils.audio import load_voices
import spacy

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영환경에서는 구체적인 도메인을 지정하세요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수 초기화
tts = TextToSpeech()
nlp = spacy.load("en_core_web_sm")

def generate_audio_stream(text, tts, voice_samples):
    print(f"Generating audio stream...: {text}")
    voice_samples, conditioning_latents = load_voices([voice_samples])
    stream = tts.tts_stream(
        text,
        voice_samples=voice_samples,
        conditioning_latents=conditioning_latents,
        verbose=True,
        stream_chunk_size=40
    )
    return stream

def split_text(text, max_length=200):
    doc = nlp(text)
    chunks = []
    chunk = []
    length = 0
    for sent in doc.sents:
        sent_length = len(sent.text)
        if length + sent_length > max_length:
            chunks.append(' '.join(chunk))
            chunk = []
            length = 0
        chunk.append(sent.text)
        length += sent_length + 1
    if chunk:
        chunks.append(' '.join(chunk))
    return chunks

# 파일 업로드 엔드포인트
@app.post("/receive_audio_file/{sender_id}")
async def receive_audio_file(
        senderId: str,
        file: UploadFile = File(...)
        ):
    try:
        sender_id = senderId
        upload_dir = os.path.join("/home/ubuntu/ai-server/tortoise/tortoise/voices",sender_id)
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{sender_id}_{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        return {
            "status": "success",
            "message": "File uploaded successfully",
            "senderId" : sender_id,
            "filename": unique_filename,
            "file_path": file_path
        }
    except Exception as e:
        return {
            "status": "error",
            "senderId" : sender_id,
            "message": f"An error occurred: {str(e)}"
        }

# WebSocket 연결 관리를 위한 ConnectionManager 클래스
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            print(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")

    async def send_audio(self, client_id: str, audio_data: bytes):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_bytes(audio_data)

    async def send_message(self, client_id: str, message: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

manager = ConnectionManager()

# WebSocket 엔드포인트
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                data = json.loads(data)
                message = data.get('message')
                
                print(f"연결된 사용자: {client_id}")
                print(f"메시지: {message}")
                
                if '|' in message:
                    character_name, text = message.split('|', 1)
                else:
                    character_name = "deniro"
                    text = message
                    
                text_chunks = split_text(text, max_length=200)
                print(f"사용자 {client_id}의 텍스트 청크: {text_chunks}")
                
                all_audio_data = []
                for chunk in text_chunks:
                    audio_stream = generate_audio_stream(chunk, tts, character_name)
                    chunk_audio_data = []
                    for audio_chunk in audio_stream:
                        audio_data = audio_chunk.cpu().numpy().flatten()
                        chunk_audio_data.append(audio_data)
                        await manager.send_audio(client_id, audio_data.tobytes())
                        
                    if chunk_audio_data:
                        combined_chunk = np.concatenate(chunk_audio_data)
                        all_audio_data.append(combined_chunk)
                
                if all_audio_data:
                    complete_audio = np.concatenate(all_audio_data)
                    os.makedirs("audio_files", exist_ok=True)
                    file_name = f"{character_name}_{uuid.uuid4()}.wav"
                    file_path = os.path.join("audio_files", file_name)
                    wavfile.write(file_path, 24000, complete_audio)
                    print(f"Audio saved to: {file_path}")
                    
                await manager.send_message(client_id, "END_OF_AUDIO")
                
            except json.JSONDecodeError:
                print("잘못된 JSON 형식입니다.")
            except Exception as e:
                print(f"오류 발생: {str(e)}")
    except Exception as e:
        print(f"WebSocket 오류: {str(e)}")
    finally:
        manager.disconnect(client_id)

if __name__ == "__main__":
   # uvicorn.run(app, host="0.0.0.0", port=8000)
   uvicorn.run(
           app,
           host="0.0.0.0",
           port=8000,
           log_level="info"
           )
