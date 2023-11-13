"""
This module contains the Flask app and the API endpoints.
"""
from whispercpp_binding.transcribe_to_json import transcript_to_json
from transcription_handler import get_transcription_status, handle_transcription_request
from flask import Flask

app = Flask(__name__)

if __name__ == '__main__':
    app.run()


def main() -> None:
    """Loop to handle request queue"""
    results = transcript_to_json(
        main_path="/whisper.cpp/main",
        model_path="/whisper.cpp/models/ggml-small.bin",
        audio_file_path="/whisper.cpp/samples/jfk.wav",
        output_file="/data/main",
        debug=True,
    )
    print(results)


# main()



# Base endpoint with API usage information
@app.route("/")
def welcome():
    """Function that returns information about the API usage."""
    api_info = """
Welcome to the Transcription API!

Here are the available endpoints:

1. `/transcribe` (POST): Transcribe audio files over HTTP.
   Example: curl -X POST http://your-server-address/transcribe -H "Content-Type: audio/*" --data-binary @your-audio-file.mp3

2. `/get_transcription_status/<transcription_id>` (GET): Get transcription status for a given transcription ID.
   Example: curl http://your-server-address/get_transcription_status/your-transcription-id

3. `/stream_transcribe` (POST): Transcribe streaming audio over Websockets.
   Example: Implement WebSocket connection and send audio data. (Work in progress)

Feel free to explore and use these endpoints for your transcription needs!
"""

    return api_info

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    """API endpoint to transcribe an audio file"""
    return handle_transcription_request()

@app.route('/get_transcription_status/<transcription_id>', methods=['GET'])
def get_transcription_status_route(transcription_id):
    """API endpoint to get the status of a transcription"""
    return get_transcription_status(transcription_id)

@app.route("/stream_transcribe", methods=["POST"])
def stream_transcribe():
    """transcribes an audio stream"""
