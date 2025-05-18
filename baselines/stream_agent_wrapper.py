import asyncio
import threading
import websockets
import json

import gymnasium as gym

X_POS_ADDRESS, Y_POS_ADDRESS = 0xD362, 0xD361
MAP_N_ADDRESS = 0xD35E


class StreamWrapper(gym.Wrapper):
    def __init__(self, env, stream_metadata={}):
        super().__init__(env)
        self.ws_address = "wss://transdimensional.xyz/broadcast"
        self.stream_metadata = stream_metadata
        self.loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.loop_thread.start()
        self.websocket = None
        asyncio.run_coroutine_threadsafe(self.establish_wc_connection(), self.loop)
        self.upload_interval = 300
        self.stream_step_counter = 0
        self.env = env
        self.coord_queue = []
        if hasattr(env, "pyboy"):
            self.emulator = env.pyboy
        elif hasattr(env, "game"):
            self.emulator = env.game
        else:
            raise Exception("Could not find emulator!")

    def step(self, action):

        x_pos = self.emulator.get_memory_value(X_POS_ADDRESS)
        y_pos = self.emulator.get_memory_value(Y_POS_ADDRESS)
        map_n = self.emulator.get_memory_value(MAP_N_ADDRESS)
        self.coord_queue.append([x_pos, y_pos, map_n])

        self.stream_step_counter += 1
        if self.stream_step_counter >= self.upload_interval:
            metadata = dict(self.stream_metadata)
            metadata["extra"] = f"coords: {len(self.env.seen_coords)}"
            coords = self.coord_queue.copy()
            self.coord_queue.clear()
            message = json.dumps({"metadata": metadata, "coords": coords})
            self.loop.call_soon_threadsafe(
                self.loop.create_task, self.broadcast_ws_message(message)
            )
            self.stream_step_counter = 0

        return self.env.step(action)

    async def broadcast_ws_message(self, message):
        if self.websocket is None:
            await self.establish_wc_connection()
        if self.websocket is not None:
            try:
                await self.websocket.send(message)
            except websockets.exceptions.WebSocketException:
                self.websocket = None
            except Exception:
                self.websocket = None

    async def establish_wc_connection(self):
        try:
            self.websocket = await websockets.connect(self.ws_address)
        except Exception:
            self.websocket = None
