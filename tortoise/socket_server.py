import asyncio
import websockets
import spacy
import urllib.parse
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
        # URL에서 쿼리 파라미터 파싱
        query_params = urllib.parse.parse_qs(urllib.parse.urlparse(path).query)
        user_id = query_params.get('user_id', ['default'])[0]
        
        print(f"연결된 사용자: {user_id}")
        
        async for message in websocket:
            if '|' in message:
                character_name, text = message.split('|', 1)
            else:
                # user_id를 character_name으로 사용
                character_name = user_id
                text = message

            text_chunks = split_text(text, max_length=200)
            print(f"사용자 {user_id}의 텍스트 청크: {text_chunks}")
            for chunk in text_chunks:
                audio_stream = generate_audio_stream(chunk, tts, character_name)

                for audio_chunk in audio_stream:
                    audio_data = audio_chunk.cpu().numpy().flatten()
                    await websocket.send(audio_data.tobytes())

            await websocket.send("END_OF_AUDIO")

    finally:
        print(f"사용자 {user_id} 연결 해제.")


async def start_server():
    server = await websockets.serve(handle_client, "0.0.0.0", 90)
    print("서버가 90번 포트에서 리스닝 중입니다.")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(start_server())
