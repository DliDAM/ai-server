# from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# from whisper_live import WhisperModel
# import asyncio
# import tempfile

# router = APIRouter()

# # Initialize Whisper Model (Specify the desired model name)
# model_name = "small"  # You can use "tiny", "small", "medium", or "large"
# whisper_model = WhisperModel(model_name=model_name)

# @router.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     print("Configuring BE Socket")
#     await websocket.accept()
#     print("BE Socket Accepted")
    
#     while True:
#         data = await websocket.receive_text()
#         await websocket.send_text(f"Echo: {data}")

# @router.websocket("/audio/ws")
# async def websocket_audio_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     print("WebSocket connection accepted.")

#     try:
#         # Prepare an async queue to hold incoming audio data
#         audio_queue = asyncio.Queue()

#         # Function to process audio data from the queue
#         async def process_audio_data():
#             # Use a temporary file to write the received audio
#             with tempfile.NamedTemporaryFile(suffix=".wav") as audio_file:
#                 while True:
#                     # Retrieve audio data from the queue
#                     data = await audio_queue.get()
#                     if data is None:
#                         break

#                     # Write the data to the temporary file
#                     audio_file.write(data)
#                     audio_file.flush()

#                     # Perform the transcription
#                     transcription = whisper_model.transcribe(audio_file.name)

#                     # Send the transcription back to the client
#                     await websocket.send_text(transcription)
#                     print(f"Transcribed text: {transcription}")

#         # Start the audio processing task
#         audio_task = asyncio.create_task(process_audio_data())

#         while True:
#             # Receive audio data as bytes
#             data = await websocket.receive_bytes()
            
#             # Add the received audio data to the queue for processing
#             await audio_queue.put(data)

#     except WebSocketDisconnect:
#         print("WebSocket connection closed by client.")

#     except Exception as e:
#         print(f"Error: {e}")

#     finally:
#         # Notify the audio processing task to exit
#         await audio_queue.put(None)
#         # Wait for the audio processing task to complete
#         await audio_task
#         print("WebSocket connection closed.")