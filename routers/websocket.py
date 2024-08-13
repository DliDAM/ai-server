from fastapi import APIRouter, WebSocket


router = APIRouter()

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