"""Module to handle the WebSocket server"""
import asyncio
import json
import websockets
from pydub import AudioSegment
from src.config import CONFIG
from src.api.websocket.websockets_settings import (
    default_websocket_settings,
)
from src.transcription.transcriber import Transcriber

WAIT_FOR_TRANSCRIPTION = 4  # seconds to wait for transcription
TRANSCRIPTION_TIMEOUT_SLEEP = 60  # seconds to sleep after timeout
TIMEOUT_COUNT = 3  # number of timeouts before stopping the server


class WebSocketServer:
    """Class to handle the WebSocket server"""

    def __init__(self, port=1235, host="localhost"):
        self.server = None
        self.host = host
        self.port = port
        self.settings = default_websocket_settings()
        self.transcriber = Transcriber([CONFIG["STREAM_MODEL"]])
        self.timeout_counter = 0
        self.is_busy = (
            False  # Flag to indicate if the server is currently handling a client
        )

    async def start_server(self):
        """Function to start the WebSocket server"""
        async with websockets.serve(self.echo, self.host, self.port):
            await asyncio.Future()

    async def echo(self, websocket):
        """Function to handle the WebSocket connection"""
        if self.is_busy:
            await websocket.send("Server is currently busy. Please try again later.")
            await websocket.close()
            return

        self.is_busy = True  # Set the flag when a client is being served

        try:
            if self.timeout_counter > TIMEOUT_COUNT:
                await websocket.close()
                await asyncio.sleep(TRANSCRIPTION_TIMEOUT_SLEEP)
                self.timeout_counter = 0

            audio_data = bytearray()
            async for message in websocket:
                audio_data.extend(message)
                break
            await self.handle_transcription(audio_data, websocket)
        finally:
            self.is_busy = False  # Reset the flag when the client session ends

    async def handle_transcription(self, audio_data, websocket):
        """Initiates the transcription process and waits for the result."""
        # start transcription
        audio_segment = AudioSegment(
            data=audio_data, sample_width=2, frame_rate=16000, channels=1
        )
        response = self.transcriber.transcribe_audio_audio_segment(
            audio_segment, CONFIG["STREAM_MODEL"], self.settings
        )

        if response is None:
            response = "Transcription timed out"
            self.timeout_counter += 1
        else:
            self.timeout_counter = 0

        if isinstance(response, dict):
            await websocket.send(json.dumps(response))
        else:
            await websocket.send(str(response))
