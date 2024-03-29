"""This module works as Interface for the access to the data folder."""
import os
from datetime import datetime
import time
from src.helper.types.transcription_status import TranscriptionStatus
from src.config import CONFIG
from src.helper.file_handler import FileHandler
from src.helper.logger import Color, Logger

class DataHandler:
    """This class handles the data folder."""

    def __init__(
        self,
        status_path: str = CONFIG["status_file_path"],
        audio_file_path: str = CONFIG["audio_file_path"],
        audio_file_format: str = CONFIG["audio_file_format"],
    ):
        self.log = Logger("DataHandler", True, Color.GREEN)
        self.root_path = os.getcwd()
        self.data_folder = os.path.join(self.root_path, "data")
        self.file_handler = FileHandler()

        self.status_path = self.root_path + status_path
        self.audio_file_path = self.root_path + audio_file_path
        self.audio_file_format = audio_file_format

    def get_status_file_by_id(self, transcription_id: str) -> dict:
        """Returns the status file by the given transcription_id."""
        file_name = f"{transcription_id}.json"
        file_path = os.path.join(self.status_path + file_name)
        data = self.file_handler.read_json(file_path)
        if data:
            return data
        return None

    def get_all_status_filenames(self) -> list[str]:
        """Returns all status files."""
        status_files = []
        for filename in os.listdir(self.status_path):
            if filename.endswith(".json"):
                status_files.append(filename)
        return status_files

    def write_status_file(self, transcription_id: str, data: dict) -> None:
        """Writes the status file by the given transcription_id."""
        file_name = f"{transcription_id}.json"
        file_path = os.path.join(self.status_path, file_name)
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.file_handler.write_json(file_path, data)

    def delete_status_file(self, transcription_id: str) -> bool:
        """Deletes the status file by the given transcription_id."""
        file_name = f"{transcription_id}.json"
        file_path = os.path.join(self.status_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
            return True
        self.log.print_error(f"Status file {file_name} not found.")
        return False

    def get_audio_file_path_by_id(self, transcription_id: str) -> str:
        """Returns the audio file path by the given transcription_id."""
        file_name = f"{transcription_id}{self.audio_file_format}"
        file_path = os.path.join(self.audio_file_path + file_name)
        if os.path.isfile(file_path):
            return file_path
        return None

    def update_status_file(
        self, status: str, transcription_id: str, error_message: str = None
    ) -> None:
        """Updates the status file with the given status."""
        file_name = f"{transcription_id}.json"
        file_path = os.path.join(self.status_path, file_name)
        data = self.file_handler.read_json(file_path)
        if data:
            data["status"] = status
            if status == TranscriptionStatus.FINISHED.value:
                data["end_time"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            if error_message is not None:
                data["error_message"] = error_message
            self.file_handler.write_json(file_path, data)
            self.log.print_log(f"Status file {file_name} updated (status: {status})")
        else:
            self.log.print_error(
                f"File for transcription ID {transcription_id} not found, PATH: {self.status_path}"
            )

    def merge_transcript_to_status(
        self, transcription_id: str, transcript_data: dict
    ) -> bool:
        """Merges the transcript file to the status file."""
        status_data = self.get_status_file_by_id(transcription_id)
        if transcript_data and status_data:
            status_data["transcript"] = transcript_data
            self.write_status_file(transcription_id, status_data)
            self.log.print_log(f"Transcript added for {transcription_id}")
            self.update_status_file(
                TranscriptionStatus.FINISHED.value, transcription_id
            )
            return True
        self.log.print_error(
            f"Transcript or Status file for {transcription_id} not found."
        )
        return False

    def clean_up_audio_and_status_files(self, keep_data_for_hours: int = CONFIG["keep_data_for_hours"]) -> None:
        """Deletes status and audio files that are older than the keep_data_for_hours."""
        try:
            for filename in os.listdir(self.status_path):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.status_path, filename)
                    file_time = os.path.getmtime(file_path)
                    # 3600 seconds in an hour
                    if (time.time() - file_time) / 3600 > keep_data_for_hours:
                        os.remove(file_path)
                        self.log.print_log(f"Deleted status file {filename}")
            for filename in os.listdir(self.audio_file_path):
                if filename.endswith(CONFIG["audio_file_format"]):
                    file_path = os.path.join(self.audio_file_path, filename)
                    file_time = os.path.getmtime(file_path)
                    # 3600 seconds in an hour
                    if (time.time() - file_time) / 3600 > keep_data_for_hours:
                        os.remove(file_path)
                        self.log.print_log(f"Deleted audio file {filename}")
        except Exception as e:
            self.log.print_error(f"Error while cleaning up files: {str(e)}")

    def get_status_file_settings(self, transcription_id: str) -> dict:
        """Returns the settings from the status file."""
        try:
            file_name = f"{transcription_id}.json"
            file_path = os.path.join(self.status_path, file_name)
            data = self.file_handler.read_json(file_path)
            if data and "settings" in data:
                return data.get("settings")
        except Exception as e:
            self.log.print_error(
                f"Error getting settings from status file: {str(e)}" + e
            )
        return None

    def save_audio_file(self, audio, transcription_id) -> dict:
        """
        Convert an audio file to 16kHz mono WAV format and save it to a directory.
        """
        try:
            os.makedirs(self.audio_file_path, exist_ok=True)
            audio.set_frame_rate(16000).set_channels(1).export(
                os.path.join(
                    self.audio_file_path, f"{transcription_id}{self.audio_file_format}"
                )
            )
            return {"success": True, "message": "Conversion successful."}
        except Exception as e:
            error_message = f"Audio File creation failed for: {str(e)}"
            self.log.print_error(error_message)
            return {"success": False, "message": error_message}

    def delete_audio_file(self, transcription_id: str) -> bool:
        """Deletes the audio file by the given transcription_id."""
        file_name = f"{transcription_id}{self.audio_file_format}"
        file_path = os.path.join(self.audio_file_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
            return True
        self.log.print_error(f"Audio file {file_name} not found.")
        return False

    def get_number_of_audio_files(self) -> int:
        """
        Returns the number of audio files
        with the config audio file format and
        in the config audio file path.
        """
        audio_files = [
            f
            for f in os.listdir(self.audio_file_path)
            if f.endswith(CONFIG["audio_file_format"])
        ]
        return len(audio_files)
