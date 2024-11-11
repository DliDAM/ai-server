import asyncio
import websockets
import spacy
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

import torch
async def handle_client(websocket, path):
    try:
        async for message in websocket:
            if '|' in message:
                character_name, text = message.split('|', 1)
            else:
                # 기본값으로 처리
                character_name = "deniro"  # 기본 캐릭터 이름 설정
                text = message

            text_chunks = split_text(text, max_length=200)
            print(text_chunks)
            for chunk in text_chunks:
                audio_stream = generate_audio_stream(chunk, tts, character_name)

                for audio_chunk in audio_stream:
                    # raw 데이터로 전송 (numpy 변환 제거)
                    if isinstance(audio_chunk, torch.Tensor):
                        # torch.Tensor인 경우 CPU로 이동한 후 numpy 변환하지 않고 그대로 전송
                        raw_data = audio_chunk.cpu()
                    elif isinstance(audio_chunk, np.ndarray):
                        raw_data = audio_chunk
                    else:
                        # 그 외의 경우 적절한 형식으로 처리
                        raise TypeError("Unsupported audio chunk type")

                    await websocket.send(raw_data.tobytes())

            await websocket.send("END_OF_AUDIO")

    finally:
        print("Client disconnected.")



async def start_server():
    server = await websockets.serve(handle_client, "0.0.0.0", 5000)
    print("Server listening on port 5000")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(start_server())
