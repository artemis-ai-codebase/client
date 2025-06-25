import asyncio
import base64
import concurrent.futures
import json
import os
import time
from threading import Thread

import websockets

from Recorder import get_recorder
from Speaker import speaker
from Style import Style
from config import websocket_endpoint, device_name
from functions_calling import tools, execute_tool_call
from wakeword import wait_for_wakeword


def path_to_base64_uri(path: str) -> str:
    with open(path, "rb") as f:
        wav_bytes = f.read()

    wav_base64 = base64.b64encode(wav_bytes).decode('utf-8')
    return "data:audio/wav;base64," + wav_base64


class AgentState:
    IDLE = 0
    SPEAKING = 1
    LISTENING = 2


class NegotiationStatus:
    IDLE = 0
    ACCEPTED = 1
    REJECTED = 2
    PENDING = 3


class Agent:
    def __init__(self, token):
        self.token = token
        self.state = AgentState.IDLE
        self.messages = []
        self.socket = None
        self.negotiationState = NegotiationStatus.IDLE
        self.loop = None
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        self.async_thread = Thread(target=self._run_event_loop, daemon=True)
        self.async_thread.start()

    def _run_event_loop(self):
        """Run the asyncio event loop in a separate thread"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._async_main())

    async def _async_main(self):
        """Main async function that handles WebSocket connection"""
        try:
            self.socket = await websockets.connect(websocket_endpoint + "?token=" + self.token)

            print(Style.CYAN + f"Setting up {len(tools)} tools")
            time.sleep(1)
            await self.socket.send(json.dumps({
                "type": "toolsDefinition",
                "tools": tools
            }))

            while True:
                try:
                    message = await self.socket.recv()
                    data = json.loads(message)

                    if data["type"] == "negotiationResponse":
                        if data["status"] == "accepted":
                            print(Style.GREEN + "Negotiation accepted")
                            self.negotiationState = NegotiationStatus.ACCEPTED
                        elif data["status"] == "rejected":
                            print(Style.YELLOW + "Negotiation rejected")
                            self.negotiationState = NegotiationStatus.REJECTED
                            self.state = AgentState.IDLE
                    elif data["type"] == "toolCallRequest":
                        tool_name = data["tool_call"]["function"]["name"]
                        tool_args = json.loads(data["tool_call"]["function"]["arguments"])
                        print(Style.GREEN + "Received tool call request:", tool_name)
                        try:
                            output = execute_tool_call(tool_name, tool_args)
                        except Exception as e:
                            output = str(e)
                        await self.socket.send(json.dumps({
                            "type": "toolCallResponse",
                            "tool_call_id": data["tool_call"]["id"],
                            "content": output
                        }))
                    elif data["type"] == "voiceResponse":
                        print(Style.GREEN + "Received voice response")

                        self.messages = data["messages"]
                        message = self.messages[-1]
                        print(Style.RESET + ">>> " + message["content"])

                        audio_bytes = base64.b64decode(str(data["audio"]).split(',')[1])
                        with open("temp.mp3", "wb") as f:
                            f.write(audio_bytes)

                        self.state = AgentState.SPEAKING
                        speaker.play("temp.mp3")

                        print(Style.GRAY + "Speaking")
                        while speaker.is_playing and self.state == AgentState.SPEAKING:
                            time.sleep(0.01)
                        speaker.stop()
                        if self.state == AgentState.SPEAKING:
                            if "?" in message["content"]:
                                self.negotiationState = NegotiationStatus.ACCEPTED
                                self.listen()
                            else:
                                self.state = AgentState.IDLE
                                print(Style.GRAY + "Waiting for wake word")

                except websockets.exceptions.ConnectionClosed:
                    print(Style.RED + "Websocket connection closed")
                    print(self.socket.close_code, self.socket.close_reason)
                    os._exit(1)
                except Exception as e:
                    print(Style.RED + "Error in event loop:", e)
                    os._exit(1)
        except Exception as e:
            print(Style.RED + "Failed to connect to WebSocket:", e)
            os._exit(1)

    def run_agent(self):
        """Main synchronous loop"""
        print(Style.GRAY + "Waiting for wake word")
        while True:
            wait_for_wakeword()
            if self.state == AgentState.LISTENING:
                continue
            self._schedule_async(self.perform_negotiation())
            self.listen()

    def listen(self):
        self.state = AgentState.LISTENING
        get_recorder().record_while_speaking("input.mp3", record_before_speaking=True)
        while get_recorder().is_recording and self.state == AgentState.LISTENING:
            time.sleep(0.01)
        get_recorder().is_recording = False
        if self.state == AgentState.LISTENING:
            while self.negotiationState == NegotiationStatus.PENDING:
                time.sleep(0.01)
            if self.negotiationState == NegotiationStatus.ACCEPTED:
                self._schedule_async(self.send_voice_request("input.mp3"))
            else:
                self.state = AgentState.IDLE
                self.negotiationState = NegotiationStatus.IDLE

    def _schedule_async(self, coro):
        """Schedule an async coroutine to run in the async event loop"""
        if self.loop and not self.loop.is_closed():
            asyncio.run_coroutine_threadsafe(coro, self.loop)

    async def perform_negotiation(self):
        if self.socket:
            print(Style.CYAN + "Sending negotiation")
            self.negotiationState = NegotiationStatus.PENDING
            priority = 0
            if speaker.is_playing:
                priority += 1
            await self.socket.send(json.dumps({
                "type": "negotiationRequest",
                "device_name": device_name,
                "priority_score": priority
            }))

    async def send_voice_request(self, path: str):
        if self.negotiationState == NegotiationStatus.ACCEPTED and self.socket:
            print(Style.CYAN + "Sending speech")
            await self.socket.send(json.dumps({
                "type": "voiceRequest",
                "messages": self.messages,
                "audio": path_to_base64_uri(path)
            }))
            self.negotiationState = NegotiationStatus.IDLE
