""" Entry point for the API """
import json
import multiprocessing
from src.helper.model_handler import ModelHandler
from src.helper.logger import Color, Logger
from src.api.rest.run import run_flask_app_prod
from src.api.websocket.run import run_websocket_app
from src.config import CONFIG
from src.transcription.run import run_file_transcriber

LOGGER = Logger("app.py", True, Color.GREEN)

def run(port, websocket_port, environment, host):
    """start flask & websockets apps for development and production based on environment"""

    if environment == "production":
        LOGGER.print_log("Running production..")
        transcription_runner = multiprocessing.Process(
            target=run_file_transcriber,
            args=(),
        )
        websocket_server = multiprocessing.Process(
            target=run_websocket_app,
            args=(
                websocket_port,
                host,
            ),
        )
        flask_server = multiprocessing.Process(
            target=run_flask_app_prod,
            args=(
                port,
                host,
            ),
        )
        transcription_runner.start()
        websocket_server.start()
        flask_server.start()
        transcription_runner.join()
        websocket_server.join()
        flask_server.join()

if __name__ == "__main__":
    LOGGER.print_log(CONFIG)
    ModelHandler().setup_models(json.loads(CONFIG["AVAILABLE_MODELS"]))
    run(CONFIG["PORT"], CONFIG["WEBSOCKET_PORT"], CONFIG["ENVIRONMENT"], CONFIG["HOST"])
