import asyncio
import json
import os
import uuid
import numpy as np
from scipy.io import wavfile
from fastapi import FastAPI, UploadFile, File, WebSocket, Form
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

@app.post("/receive_audio_file")
async def receive_audio_file(
        senderId: str = Form(...),
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

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        return websocket

    def store_connection(self, sender_id: str, websocket: WebSocket):
        self.active_connections[sender_id] = websocket
        print(f"\n=== WebSocket Connected ===")
        print(f"Sender ID: {sender_id}")
        print("=========================\n")

    def disconnect(self, sender_id: str):
        if sender_id in self.active_connections:
            del self.active_connections[sender_id]
            print(f"\n=== WebSocket Disconnected ===")
            print(f"Sender ID: {sender_id}")
            print("============================\n")

    async def send_audio(self, sender_id: str, audio_data: bytes):
        if sender_id in self.active_connections:
            await self.active_connections[sender_id].send_bytes(audio_data)

    async def send_message(self, sender_id: str, message: str):
        if sender_id in self.active_connections:
            await self.active_connections[sender_id].send_text(message)

manager = ConnectionManager()

def check_and_set_character_name(sender_id,voice_type):
    voices_dir = os.path.join("tortoise/voices", sender_id)

    if os.path.isdir(voices_dir):
        character_name = sender_id
    elif voice_type == 'male':
        character_name = "deniro"
    elif voice_type == 'female':
        character_name = "emma"
    else:
        character_name = voice_type
    # tortoise/voices 경로에 ROSE, GD, BRUNO,GRANDE 목소리 샘플 3가지 추가 후 voice_type으로 변경
    return character_name

# WebSocket 엔드포인트
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                data = json.loads(data)

                # JSON 데이터에서 필요한 정보 추출
                chat_room_id = data.get('chatRoomId')
                sender_id = data.get('senderId')
                voice_type = data.get('voiceType').lower()
                message = data.get('message')
                
                # 필수 필드 확인
                if not all([chat_room_id, sender_id, voice_type, message]):
                    raise ValueError("Missing required fields (chatRoomId, senderId, voice_type or message)")

                # 첫 메시지인 경우 연결 저장
                if sender_id not in manager.active_connections:
                    manager.store_connection(sender_id, websocket)

                # 텍스트 수신 로그
                print(f"\n=== Text Message Received ===")
                print(f"Sender ID: {sender_id}")
                print(f"chat_room_id: {chat_room_id}")
                print(f"Message: {message}")
                print(f"voice_type: {voice_type}")
                print("===========================\n")
                
                if '|' in message:
                    character_name, text = message.split('|', 1)
                else:
                    # voiceType : mine 인 경우 사용자 본인 목소리 가중치 사용
                    # 사용자가 본인 목소리 서버에 전송하지 않은 이상 mine이 AI 서버에 전송될 일 없음
                    # 추후 에러 처리 필요
                    character_name = check_and_set_character_name(sender_id, voice_type)
                    text = message
                    
                text_chunks = split_text(text, max_length=200)
                print(f"사용자 {sender_id}의 텍스트 청크: {text_chunks}")
                
                all_audio_data = []
                for chunk in text_chunks:
                    audio_stream = generate_audio_stream(chunk, tts, character_name)
                    chunk_audio_data = []
                    for audio_chunk in audio_stream:
                        audio_data = audio_chunk.cpu().numpy().flatten()
                        chunk_audio_data.append(audio_data)
                        await manager.send_audio(sender_id, audio_data.tobytes())
                        
                    if chunk_audio_data:
                        combined_chunk = np.concatenate(chunk_audio_data)
                        all_audio_data.append(combined_chunk)
                    
                await manager.send_message(sender_id, "END_OF_AUDIO")
                
            except json.JSONDecodeError:
                print("잘못된 JSON 형식입니다.")
            except Exception as e:
                print(f"오류 발생: {str(e)}")
    except Exception as e:
        print(f"WebSocket 오류: {str(e)}")
    finally:
        if sender_id:
            manager.disconnect(sender_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
