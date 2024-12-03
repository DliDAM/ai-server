import asyncio
import websockets
import soundfile as sf
import numpy as np

async def receive_and_save_audio(websocket, output_file):
    buffer = b''
    total_chunks_received = 0

    try:
        while True:
            chunk = await websocket.recv()
            total_chunks_received += 1

            if isinstance(chunk, str) and chunk == "END_OF_AUDIO":
                print("End of audio signal received.")
                break

            buffer += chunk

        # 서버에서 받은 데이터를 numpy 배열로 변환하고 .wav 파일로 저장
        with open(output_file, 'wb') as f:
            f.write(buffer)

        print(f"Audio saved to {output_file}")
        print(f"Total chunks received: {total_chunks_received}")

    except Exception as e:
        print(f"Error receiving audio: {e}")

async def send_text_to_server(character_name, text, output_file, server_ip='localhost', server_port=5000):
    uri = f"ws://{server_ip}:{server_port}"
    async with websockets.connect(uri) as websocket:
        data = f"{character_name}|{text}"
        print(f"Sending text to server: {data}")
        await websocket.send(data)

        print("Text sent successfully. Awaiting audio stream...")
        await receive_and_save_audio(websocket, output_file)

async def main(server_ip='localhost', server_port=5000):
    character_name = "deniro"  # 기본 캐릭터 이름

    while True:
        text = input("Enter text to convert to speech (or 'quit' to exit): ")

        if text.lower() == 'quit':
            print("Exiting the client...")
            break

        output_file = "client_output.wav"  # 클라이언트 측에서 저장할 파일 이름
        await send_text_to_server(character_name, text, output_file, server_ip, server_port)

if __name__ == "__main__":
    asyncio.run(main())

