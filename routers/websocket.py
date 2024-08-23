from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import os
import uuid
import json
from queue import Queue
from datetime import datetime, timedelta
from time import sleep
import threading
from typing import List
import logging
import wave # <- 임시로 import하는거. 추후 삭제 필요.

router = APIRouter()

# Thread safe Queue for passing data from the threaded recording callback.
text_queue = Queue()

# Thread safe Queue for passing result from STT Thread
result_queue = Queue()

# EventObject for Stopping Thread
stop_event = threading.Event()

# ======================== new project 08/23 ======================== #
# 로그 확인용 <- 추후 삭제
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("websocket")

async def process_tts(text: str) -> bytes:
    # TTS 처리 (여기서는 단순히 바이너리 데이터를 반환하는 예시)
    # 실제로는 TTS 엔진을 사용하여 음성 데이터를 생성
    await asyncio.sleep(1)  # TTS 처리 시간 시뮬레이션
    response = b"dummy binary audio data"
    logger.info(f"Sending message: {response}")
    return b"dummy binary audio data"  # 추후 실제 음성 데이터로 대체

@router.websocket("/ws/new")
async def websocket_TTS(websocket: WebSocket):
    await websocket.accept()
    try:
        # Worker 코루틴을 별도로 실행하여 Queue 처리
        asyncio.create_task(worker(websocket))

        while True:
            data = await websocket.receive_text()
            logger.info(f"Received message: {data}")
            words = data.split()
            
            chunk_size = 7 # 이 부분은 성능에 따라서 변경 가능
            chunks = [words[i:i+chunk_size] for i in range(0,len(words), chunk_size)]
            for chunk in chunks:
                text_queue.put(chunk)

    except WebSocketDisconnect:
        print("WebSocket connection closed")

# Queue를 처리하는 작업자 함수
async def worker(websocket : WebSocket):
    while True:
        if not text_queue.empty():
            text = text_queue.get()
            audio_data = await process_tts(text)
            logger.info("----input----")
            await websocket.send_bytes(audio_data)
            logger.info("----output-----")
        await asyncio.sleep(0.1)  # Queue가 비어있는지 확인하는 주기

# ================================================================================================ #
def read_wav(file_path):
    with wave.open(file_path, 'rb') as wav_file:
        frames = wav_file.readframes(wav_file.getnframes())
    return 

async def textToSpeech(stop_event):
    print("[TTSThread] TTS Thread Executed")

    while not stop_event.is_set():
        sleep(3)
        try:
            now = datetime.utcnow()
            # pop text from the queue.
            if not text_queue.empty():
                audio_file_path = "./data/received_audio.wav"
                processed_result = read_wav(audio_file_path)
                if processed_result != None:
                    result_queue.put(processed_result)

        except Exception as e:
            print(f"[TTSThread] Error processing text data: {e}")
            break

    print("[TTSThread] TTS Thread Destroyed")

async def process_thread(websocket: WebSocket):
    print("[ProcessTask] Process Task Initiated")
    while not stop_event.is_set():
        await asyncio.sleep(0.25)
        try:
            if not result_queue.empty():
                audio_result = result_queue.get()
                while chunk := audio_result.read(1024):
                    await websocket.send_bytes(chunk)
                
        except Exception as e:
            print(f"[ProcessTask] Error : {e}")
            break
    
    print("[ProcessTask] Process Task Destroyed")

async def websocket_task(websocket: WebSocket):
    # Load Model Here 
    device = 'cuda'
    print("[WebSocketTask]-[****] Model Loaded Successfully with", device)

    # Accept WebSocket
    #connection_uuid = await websocket.receive_bytes()
    #print("[WebSocketTask] Connection [" + connection_uuid + "] Accepted")

    # Execute TTS Thread until WebSocket Disconnected
    
    ttsThread = threading.Thread(target=textToSpeech, args=(stop_event,))
    ttsThread.start()

    processTask = asyncio.create_task(process_thread(websocket))

    # Receive Text
    try:
        while True:
            text_data = await websocket.receive_text()
            text_queue.put(text_data)

            # Sleep for other async functions
            await asyncio.sleep(0)

    except Exception as e:
        print(f"[WebSocketTask] WebSocket error: {e}")
    finally:
        stop_event.set()
        ttsThread.join()
        processTask.cancel()

        # clear stop_event for next Socket Connection
        stop_event.clear()

        while not text_queue.empty():
            text_queue.get()

        while not result_queue.empty():
            result_queue.get()

        if websocket.client_state.name != "DISCONNECTED":
            await websocket.close()

        print("[WebSocketTask] Connection Closed")

#======= WebSocket ========#
@router.websocket("/tts/ws")
async def tts_endpoint(websocket: WebSocket):
    print("Configuring BE Socket")
    await websocket.accept()
    print("BE Socket Accepted")
    
    await asyncio.create_task(websocket_task(websocket))

@router.websocket("/ws")
async def websocket_test_endpoint(websocket: WebSocket):
    print("Configuring BE Socket")
    await websocket.accept()
    print("BE Socket Accepted")
    
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")

@router.websocket("/audio/ws")
async def websocket_audio_test_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection accepted.")
    
    try:
        while True:
            # 음성 데이터를 바이너리로 수신
            data = await websocket.receive_bytes()
            # 데이터 처리 예: 파일로 저장
            with open("received_audio.wav", "wb") as f:
                f.write(data)
            # 클라이언트에 데이터 전송 (예: 수신 완료 알림)
            await websocket.send_text("Audio received and saved.")
    except Exception as e:
        print("Error:", e)
    finally:
        print("WebSocket connection closed.")

#======= WebSocket ========#
@router.websocket("/tts")
async def websocket_tts_test_endpoint(websocket: WebSocket):
    print("Configuring BE Socket")
    await websocket.accept()
    print("BE Socket Accepted")
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received text data: {data}")
            audio_file_path = "./data/received_audio.wav"
            if os.path.exists(audio_file_path):
                with open(audio_file_path, "rb") as audio_file:
                    while chunk := audio_file.read(1024):
                        await websocket.send_bytes(chunk)
                    #processed_result = read_wav(audio_file_path)
                    #await websocket.send_bytes(processed_result)
            else:
                    await websocket.send_text("Audio file not found.")
    except Exception as e:
        print("Exception as",e)
    finally:
        print("WebSocket connection closed.")