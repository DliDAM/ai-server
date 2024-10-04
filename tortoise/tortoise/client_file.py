import asyncio
import websockets
import os

async def handle_client(websocket, path):
    client_id = path.strip('/')  # WebSocket path에서 client_id 추출
    directory_path = os.path.join('tortoise', 'tortoise', 'voices', client_id)

    os.makedirs(directory_path, exist_ok=True)

    for i in range(1, 4):  
        filename = f'new recording {i}.wav'  # 파일 이름 변경하기
        file_path = os.path.join(directory_path, filename)
        
        print(f"Waiting to receive {filename}...")
        
        audio_data = await websocket.recv()
        
        # Write the received audio data to the file
        with open(file_path, 'wb') as audio_file:
            audio_file.write(audio_data)
        
        print(f"Saved {filename} to {file_path}")

    print("All files received. Quitting server.")
    await websocket.close()

async def main():
    async with websockets.serve(handle_client, 'localhost', 5000):
        print("WebSocket server started")
        await asyncio.Future() 

if __name__ == "__main__":
    asyncio.run(main())