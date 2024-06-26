# This is a simple example that shows how to transcribe a file using vosk server.
# https://github.com/alphacep/vosk-server/blob/master/client-samples/python/asr-test-client.py

import asyncio
import websockets
import sys
import wave


async def run_test(uri):
    async with websockets.connect(uri) as websocket:
        wf = wave.open(sys.argv[1], "rb")
        await websocket.send(
            '{ "config" : { "sample_rate" : %d } }' % (wf.getframerate())
        )
        buffer_size = int(wf.getframerate() * 1)
        while True:
            data = wf.readframes(buffer_size)

            if len(data) == 0:
                break

            await websocket.send(data)
            print(await websocket.recv())

        await websocket.send('{"eof" : 1}')
        print(websocket.recv())


asyncio.run(run_test("ws://localhost:8764"))
