from typing import Union
from fastapi import FastAPI
from routers import websocket
from fastapi.responses import FileResponse


app = FastAPI()
app.include_router(websocket.router)
path = './templates/index.html'
audio_path = './templates/audio.html'
audio_file_path = './templates/audio_file.html'
text_to_audio_path = './templates/texttoaudio.html'
@app.get("/")
async def get():
    return FileResponse(text_to_audio_path)

@app.get("/items/{item_id}")
def read_item(item_id : int, q:Union[str, None] = None):
    return {"item_id" : item_id, "q" : q}
    