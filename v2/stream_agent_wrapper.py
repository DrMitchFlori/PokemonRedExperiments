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
        self.coord_queue = asyncio.Queue()
        self.upload_interval = 300
        self.send_interval = 0.5
        self.websocket = None
        self.env = env
        self.coord_list = []
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        if hasattr(env, "pyboy"):
            self.emulator = env.pyboy
        elif hasattr(env, "game"):
            self.emulator = env.game
        else:
            raise Exception("Could not find emulator!")

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.create_task(self.establish_wc_connection())
        self.loop.create_task(self._periodic_sender())
        self.loop.run_forever()

    def step(self, action):

        x_pos = self.emulator.memory[X_POS_ADDRESS]
        y_pos = self.emulator.memory[Y_POS_ADDRESS]
        map_n = self.emulator.memory[MAP_N_ADDRESS]
        asyncio.run_coroutine_threadsafe(
            self.coord_queue.put([x_pos, y_pos, map_n]), self.loop
        )

        return self.env.step(action)

    async def broadcast_ws_message(self, message):
        if self.websocket is None:
            await self.establish_wc_connection()
        if self.websocket is not None:
            try:
                await self.websocket.send(message)
            except websockets.exceptions.WebSocketException:
                self.websocket = None

    async def establish_wc_connection(self):
        try:
            self.websocket = await websockets.connect(self.ws_address)
        except Exception:
            self.websocket = None

    async def _periodic_sender(self):
        batch = []
        while True:
            try:
                coord = await asyncio.wait_for(
                    self.coord_queue.get(), timeout=self.send_interval
                )
                batch.append(coord)
                if len(batch) >= self.upload_interval:
                    await self._send_batch(batch)
                    batch = []
            except asyncio.TimeoutError:
                if batch:
                    await self._send_batch(batch)
                    batch = []

    async def _send_batch(self, batch):
        self.stream_metadata["extra"] = f"coords: {len(self.env.seen_coords)}"
        await self.broadcast_ws_message(
            json.dumps({"metadata": self.stream_metadata, "coords": batch})
        )
