import asyncio
import websockets
import spacy
import json
import os
import uuid
import numpy as np
from scipy.io import wavfile
from tortoise.api_fast import TextToSpeech
from tortoise.utils.audio import load_voices

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
        stream_chunk_size=40  # Adjust chunk size as needed
    )
    for audio_chunk in stream:
        yield audio_chunk


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


async def handle_client(websocket, path):
    try:
        async for data in websocket:
            try:
                data = json.loads(data)
                
                sender_id = data.get('senderId')
                message = data.get('message')
                
                if sender_id is not None:
                    print(f"연결된 사용자: {sender_id}")
                    print(f"메시지: {message}")
                
                if '|' in message:
                    character_name, text = message.split('|', 1)
                else:
                    # user_id를 character_name으로 사용
                    # if weight folder created, change to senderId
                    character_name = "deniro"# str(sender_id)
                    text = message

                text_chunks = split_text(text, max_length=200)
                print(f"사용자 {sender_id}의 텍스트 청크: {text_chunks}")
                audio_chunks = []
                file_path = "audio_files"

                for chunk in text_chunks:
                    audio_stream = generate_audio_stream(chunk, tts, character_name)
                    for audio_chunk in audio_stream:
                        audio_data = audio_chunk
                    #    audio_data = audio_chunk.cpu().numpy().flatten()
                    #    audio_chunks.append(audio_data)
                    #    print("len of audio_data : ",len(audio_data))
                    #    await websocket.send(audio_data.tobytes())
                    
                # 모든 오디오 청크를 하나의 파일로 저장
                if audio_chunks:
                    combined_audio = np.concatenate(audio_chunks)
                    await websocket.send(combined_audio.tobytes())
                    file_name = f"{character_name}.wav"
                    file_path = os.path.join("audio_files", file_name)
                    os.makedirs("audio_files", exist_ok=True)
                    wavfile.write(file_path, 24000, combined_audio)

                await websocket.send("END_OF_AUDIO")
            except json.JSONDecodeError:
                print("잘못된 JSON 형식입니다.")
            except KeyError as e:
                print(f"필수 키가 누락되었습니다: {e}")
    finally:
        print(f"사용자 {sender_id} 연결 해제.")


async def start_server():
    server = await websockets.serve(handle_client, "0.0.0.0", 5000)
    print("서버가 5000번 포트에서 리스닝 중입니다.")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(start_server())

