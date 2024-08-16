from fastapi import APIRouter, WebSocket
import asyncio
import uuid
import json
from queue import Queue
from datetime import datetime, timedelta
from time import sleep
import threading
import wave # <- 임시로 import하는거. 추후 삭제 필요.

router = APIRouter()

# Thread safe Queue for passing data from the threaded recording callback.
text_queue = Queue()

# Thread safe Queue for passing result from STT Thread
result_queue = Queue()

# EventObject for Stopping Thread
stop_event = threading.Event()

async def read_wav(file_path):
    with wave.open(file_path, 'rb') as wav_file:
        frames = wav_file.readframes(wav_file.getnframes())
    return frames

async def textToSpeech(stop_event):
    print("[TTSThread] TTS Thread Executed")

    while not stop_event.is_set():
        sleep(3)
        try:
            now = datetime.utcnow()
            # pop text from the queue.
            if not text_queue.empty():
                processed_result = read_wav("../received_audio.wav")
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
                #audio_id = str(uuid.uuid4())
                await websocket.send(audio_result)
                
        except Exception as e:
            print(f"[ProcessTask] Error : {e}")
            break
    
    print("[ProcessTask] Process Task Destroyed")

async def websocket_task(websocket: WebSocket):
    # Load Model Here 
    device = 'cuda'
    print("[WebSocketTask]-[****] Model Loaded Successfully with", device)

    # Accept WebSocket
    connection_uuid = await websocket.receive_bytes()
    print("[WebSocketTask] Connection [" + connection_uuid + "] Accepted")

    # Execute TTS Thread until WebSocket Disconnected
    ttsThread = threading.Thread(target=textToSpeech, args=stop_event)
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
async def websocket_endpoint(websocket: WebSocket):
    print("Configuring BE Socket")
    await websocket.accept()
    print("BE Socket Accepted")
    
    await asyncio.create_task(websocket_task(websocket))


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print("Configuring BE Socket")
    await websocket.accept()
    print("BE Socket Accepted")
    
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")

@router.websocket("/audio/ws")
async def websocket_endpoint(websocket: WebSocket):
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
