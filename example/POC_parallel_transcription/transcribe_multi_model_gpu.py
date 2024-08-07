import concurrent.futures
import time
import threading

from faster_whisper import WhisperModel

start_time_total = time.time()  # Record the start time

files = [
    "audio.wav",
    "audio.wav",
    "audio.wav",
]


def transcribe_file(file_path, counter):
    print(f"Transcribing with GPU {counter}")
    model = WhisperModel(
        "large",
        device="cuda",
        compute_type="float16",
        device_index=counter,
    )
    start_time = time.time()  # Record the start time
    print(f"Transcribing {file_path}")
    segments, info = model.transcribe(file_path)
    segments = list(segments)
    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time  # Calculate elapsed time
    print(f"counter {counter} took {elapsed_time:.4f} seconds to execute.")


with concurrent.futures.ThreadPoolExecutor(10) as executor:
    executor.counter = 0
    results = []
    for i, file in enumerate(files):
        # wait 0.1 sec, to avoid errors caused by race conditions
        time.sleep(0.5)
        print(f"Submitting {file}, Executor counter: {executor.counter}")
        result = executor.submit(transcribe_file, file, counter=executor.counter)
        executor.counter += 1
        results.append(result)
        print(f"Active threads: {threading.active_count()}")

    for result in concurrent.futures.as_completed(results):
        print(result.result())  # this is required to wait for the function to conclude
        print("Done")

end_time_total = time.time()  # Record the end time
elapsed_time_total = end_time_total - start_time_total  # Calculate elapsed time
print(f"Total took {elapsed_time_total:.4f} seconds to execute.")