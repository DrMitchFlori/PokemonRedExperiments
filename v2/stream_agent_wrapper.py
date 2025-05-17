import asyncio
import json
import threading
from collections import deque

import websockets

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
        self.loop.call_soon_threadsafe(
            asyncio.create_task, self.establish_wc_connection()
        )
        self.upload_interval = 300
        self.steam_step_counter = 0
        self.env = env
        self.coord_queue = deque()
        if hasattr(env, "pyboy"):
            self.emulator = env.pyboy
        elif hasattr(env, "game"):
            self.emulator = env.game
        else:
            raise Exception("Could not find emulator!")

    def _schedule_send(self, message: str) -> None:
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(asyncio.create_task, self.broadcast_ws_message(message))

    def _read_memory(self, address):
        if hasattr(self.emulator, "get_memory_value"):
            return self.emulator.get_memory_value(address)
        if hasattr(self.emulator, "memory"):
            return self.emulator.memory[address]
        raise Exception("Emulator memory interface not found")

    def step(self, action):

        x_pos = self._read_memory(X_POS_ADDRESS)
        y_pos = self._read_memory(Y_POS_ADDRESS)
        map_n = self._read_memory(MAP_N_ADDRESS)
        self.coord_queue.append([x_pos, y_pos, map_n])

        if self.steam_step_counter >= self.upload_interval:
            self.stream_metadata["extra"] = f"coords: {len(self.env.seen_coords)}"
            coords = list(self.coord_queue)
            self.coord_queue.clear()
            message = json.dumps({"metadata": self.stream_metadata, "coords": coords})
            self._schedule_send(message)
            self.steam_step_counter = 0

        self.steam_step_counter += 1

        return self.env.step(action)

    async def broadcast_ws_message(self, message):
        if self.websocket is None:
            await self.establish_wc_connection()
        if self.websocket is not None:
            try:
                await self.websocket.send(message)
                return
            except websockets.exceptions.WebSocketException:
                pass
        self.websocket = None
        await self.establish_wc_connection()
        if self.websocket is not None:
            try:
                await self.websocket.send(message)
            except websockets.exceptions.WebSocketException:
                self.websocket = None

    async def establish_wc_connection(self):
        try:
            self.websocket = await websockets.connect(self.ws_address)
        except:
            self.websocket = None

    def close(self):
        if self.websocket is not None:
            fut = asyncio.run_coroutine_threadsafe(self.websocket.close(), self.loop)
            try:
                fut.result(1)
            except Exception:
                pass
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.loop_thread.join(timeout=1)
        return super().close()
