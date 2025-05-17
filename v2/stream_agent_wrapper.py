import asyncio
import websockets
import json
import logging

import gymnasium as gym

X_POS_ADDRESS, Y_POS_ADDRESS = 0xD362, 0xD361
MAP_N_ADDRESS = 0xD35E

class StreamWrapper(gym.Wrapper):
    def __init__(
        self,
        env,
        stream_metadata={},
        ws_address="wss://transdimensional.xyz/broadcast",
        connect_timeout=5,
        send_timeout=5,
        max_retries=3,
        retry_delay=2,
    ):
        super().__init__(env)
        self.logger = logging.getLogger(__name__)
        self.ws_address = ws_address
        self.stream_metadata = stream_metadata
        self.connect_timeout = connect_timeout
        self.send_timeout = send_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.websocket = None
        self.loop.run_until_complete(
            self.establish_wc_connection()
        )
        self.upload_interval = 300
        self.steam_step_counter = 0
        self.env = env
        self.coord_list = []
        if hasattr(env, "pyboy"):
            self.emulator = env.pyboy
        elif hasattr(env, "game"):
            self.emulator = env.game
        else:
            raise Exception("Could not find emulator!")

    def step(self, action):

        x_pos = self.emulator.memory[X_POS_ADDRESS]
        y_pos = self.emulator.memory[Y_POS_ADDRESS]
        map_n = self.emulator.memory[MAP_N_ADDRESS]
        self.coord_list.append([x_pos, y_pos, map_n])

        if self.steam_step_counter >= self.upload_interval:
            self.stream_metadata["extra"] = f"coords: {len(self.env.seen_coords)}"
            try:
                self.loop.run_until_complete(
                    self.broadcast_ws_message(
                        json.dumps(
                            {
                              "metadata": self.stream_metadata,
                              "coords": self.coord_list
                            }
                        )
                    )
                )
            except Exception as e:
                self.logger.error("Broadcast failed: %s", e)
            self.steam_step_counter = 0
            self.coord_list = []

        self.steam_step_counter += 1

        return self.env.step(action)

    async def broadcast_ws_message(self, message):
        if self.websocket is None:
            await self.establish_wc_connection()
        if self.websocket is None:
            return

        attempt = 0
        while attempt < self.max_retries:
            try:
                await asyncio.wait_for(
                    self.websocket.send(message), timeout=self.send_timeout
                )
                return
            except (websockets.exceptions.WebSocketException, asyncio.TimeoutError) as e:
                self.logger.warning(
                    "Send failed (%s/%s): %s", attempt + 1, self.max_retries, e
                )
                self.websocket = None
                attempt += 1
                await self.establish_wc_connection()
                if self.websocket is None:
                    break

    async def establish_wc_connection(self):
        attempt = 0
        while attempt < self.max_retries:
            try:
                self.logger.info(
                    "Connecting to %s (attempt %s/%s)",
                    self.ws_address,
                    attempt + 1,
                    self.max_retries,
                )
                self.websocket = await asyncio.wait_for(
                    websockets.connect(self.ws_address), timeout=self.connect_timeout
                )
                self.logger.info("Websocket connection established")
                return
            except Exception as e:
                self.logger.warning("Connection failed: %s", e)
                self.websocket = None
                attempt += 1
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay)
        self.logger.error("All websocket connection attempts failed")
