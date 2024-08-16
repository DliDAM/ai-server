import asyncio
import websockets
import argparse

async def receive_and_save_audio(websocket, output_file):
    buffer = b''
    total_chunks_received = 0

    try:
        while True:
            chunk = await websocket.recv()
            total_chunks_received += 1

            # Check if the received data marks the end of the audio stream
            if isinstance(chunk, str) and chunk == "END_OF_AUDIO":
                print("End of audio signal received.")
                break

            # Accumulate the buffer
            buffer += chunk

        # Write the raw byte data to a file
        with open(output_file, 'wb') as file:
            file.write(buffer)
        
        print(f"Audio saved to {output_file}")
        print(f"Total chunks received: {total_chunks_received}")
        print(f"Total audio length (bytes): {len(buffer)}")

    except Exception as e:
        print(f"Error receiving audio: {e}")

async def send_text_to_server(character_name, text, output_file, server_ip='localhost', server_port=5000):
    uri = f"ws://{server_ip}:{server_port}"
    async with websockets.connect(uri) as websocket:
        # Format the data to be sent to the server
        data = f"{character_name}|{text}"
        print(f"Sending text to server: {data}")
        await websocket.send(data)

        # Confirm sending was successful
        print("Text sent successfully. Awaiting audio stream...")
        
        await receive_and_save_audio(websocket, output_file)

async def main(server_ip='localhost', server_port=5000):
    character_name = "deniro"

    while True:
        # Prompt the user for text input
        text = input("Enter text to convert to speech (or 'quit' to exit): ")

        if text.lower() == 'quit':
            print("Exiting the client...")
            break

        # Generate a unique output file name
        output_file = "output.raw"

        # Send the text to the server
        await send_text_to_server(character_name, text, output_file, server_ip, server_port)

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())