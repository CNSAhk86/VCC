import asyncio
import websockets
import soundfile as sf
import sounddevice as sd
from asyncio import Queue
import cv2
from openai import OpenAI
import re
import signal
import uuid
import requests
import io
import os
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

MAX_QUEUE_SIZE = 10

def get_user_credentials():
    api_key = input("Enter your API key (or type Dev's key if you want to use the default): ")
    if api_key == 'Dev_Hana':
        api_key = 'sk-proj-791sIvdv01kwVTveNwELT3BlbkFJiu6rvaxwA5N5EcTaLLJV'
        assistant_id = 'asst_yJuMr3KHNBUDIXgBhhO14A8f'
    else:
        assistant_id = input("Enter your Assistant ID: ")
    return api_key, assistant_id

api_key, ASSISTANT_ID = get_user_credentials()
client = OpenAI(api_key=api_key)

class Sbv2Adapter:
    URL = "http://127.0.0.1:5000/voice"

    def __init__(self) -> None:
        pass

    def _create_audio_query(self, text: str, style: str) -> dict:
        params = {
            "text": text,
            "speaker_id": 0,
            "model_id": 0,
            "length": 1,
            "sdp_ratio": 0.2,
            "noise": 0.6,
            "noisew": 0.8,
            "auto_split": True,
            "split_interval": 1,
            "language": "JP",
            "style": style,
            "style_weight": 5,
        }
        return params

    def _create_request_audio(self, query_data: dict) -> bytes:
        headers = {"accept": "audio/wav"}
        response = requests.get(self.URL, params=query_data, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code}")
        return response.content

    def get_voice(self, text: str, style: str):
        query_data = self._create_audio_query(text, style)
        audio_bytes = self._create_request_audio(query_data)
        audio_stream = io.BytesIO(audio_bytes)
        data, sample_rate = sf.read(audio_stream)
        return data, sample_rate

def handle_exit(sig, frame):
    answer = input("Do you really want to exit? (y/n): ")
    if answer.lower() == 'y':
        print("Exiting program.")
        exit(0)

signal.signal(signal.SIGINT, handle_exit)

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIRECTORY = "./uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

clients = set()

async def event_generator():
    while True:
        await asyncio.sleep(1)
        for client in clients.copy():
            try:
                yield f"data: New audio file available\n\n"
                clients.remove(client)  # 한 번 이벤트를 보낸 후 클라이언트 제거
            except:
                clients.remove(client)

@app.get("/events")
async def get_events(request: Request):
    clients.add(request)
    print("Client connected for SSE")
    try:
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e:
        clients.remove(request)
        print(f"Error: {e}")
        return {"error": str(e)}

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    print(f"Uploaded file saved to {file_path}")  # 파일 경로 출력
    return {"filename": file.filename}

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    print(f"Trying to fetch file from {file_path}")  # 파일 경로 출력
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type='audio/wav')
    print(f"File not found: {file_path}")
    return {"error": "File not found"}

async def notify_clients():
    for client in clients.copy():
        try:
            await client.send_text("data: New audio file available\n\n")
        except:
            clients.remove(client)

async def play_audio_with_fastapi(data, sample_rate):
    output_file = os.path.join(UPLOAD_DIRECTORY, 'synthesized_audio.wav')  # 경로 수정
    sf.write(output_file, data, sample_rate)
    print(f'Audio saved to {output_file}')
    await notify_clients()

async def receive_messages(q: Queue, websocket):
    try:
        while True:
            message = await websocket.recv()
            print(f"Received message: {message}")
            if q.qsize() < MAX_QUEUE_SIZE:
                await q.put((uuid.uuid4(), message))
                print("Message added to queue.")
            else:
                print("Queue is full. Discarding the oldest message.")
                q.get_nowait()
                await q.put((uuid.uuid4(), message))
    except Exception as e:
        print(f"An error occurred while receiving: {e}")
        await asyncio.sleep(5)

async def process_trigger(q: Queue, websocket):
    recording = False
    audio_data = []
    stream = None
    processed_messages = set()
    adapter = Sbv2Adapter()
    processing = False

    def callback(indata, frames, time, status):
        audio_data.append(indata.copy())

    while True:
        print("Waiting for trigger...")
        msg_id, message = await q.get()
        if msg_id in processed_messages:
            q.task_done()
            continue

        print(f"Processing message: {message}")
        processed_messages.add(msg_id)
        message, emotion, japanese_text = preprocess_message(message)
        if japanese_text:
            print(f"Extracted Japanese text: {japanese_text}")

        if processing:
            print("Currently processing another task. Ignoring this trigger.")
            q.task_done()
            continue

        processing = True  # 작업 시작
        try:
            if message == "Trigger Sign" or message == "start_record":
                if not recording:
                    print("Recording started...")
                    recording = True
                    audio_data = []
                    stream = sd.InputStream(callback=callback)
                    stream.start()
                else:
                    print("Recording stopped.")
                    recording = False
                    if stream:
                        stream.stop()
                        stream.close()
                        stream = None
                        filename = os.path.join(UPLOAD_DIRECTORY, "recorded_audio.wav")  # 경로 수정
                        audio_data = [item for sublist in audio_data for item in sublist]
                        sf.write(filename, audio_data, samplerate=44100)
                        print(f"Recorded audio saved to {filename}")
                        text = await extract_text_from_audio_with_whisper(filename)
                        if text:
                            print("Extracted text:", text)
                            await send_text_to_assistant(text, websocket)
                        else:
                            print("Failed to recognize speech.")
                            await send_text_to_assistant("(안들림)", websocket)
            elif message == "Trigger Sign2":
                await handle_camera_and_send_image(websocket)
                print("Handled Trigger Sign2.")
            else:
                await websocket.send(message)
        finally:
            processing = False  # 작업 종료

        q.task_done()

async def handle_camera_and_send_image(websocket):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    print("Camera is running. Press 's' to take a picture.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image.")
            break

        cv2.imshow('Camera', frame)

        key = cv2.waitKey(1)
        if key == ord('s'):
            image_path = os.path.join(UPLOAD_DIRECTORY, 'image.png')  # 경로 수정
            cv2.imwrite(image_path, frame)
            print(f"Image saved as {image_path}")
            break

    cap.release()
    cv2.destroyAllWindows()

    await send_image_to_assistant(image_path, websocket)

async def send_image_to_assistant(image_path, websocket):
    file = client.files.create(
        file=open(image_path, "rb"),
        purpose="vision"
    )
    print(file)

    message = [
        {
            "type": "text",
            "text": " "
        },
        {
            "type": "image_file",
            "image_file": {"file_id": file.id}
        },
    ]

    await send_message_to_assistant(message, websocket)

async def send_text_to_assistant(text, websocket):
    message = [
        {
            "type": "text",
            "text": text
        }
    ]
    await send_message_to_assistant(message, websocket)

async def send_message_to_assistant(message, websocket):
    thread_id = await get_or_create_thread()
    message_response = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message
    )
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=ASSISTANT_ID
    )
    while run.status in ["queued", "in_progress"]:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        await asyncio.sleep(0.5)

    messages = client.beta.threads.messages.list(thread_id=thread_id, order="asc").data
    if messages:
        last_message = messages[-1]
        if last_message.role == "assistant":
            text_content = last_message.content[0].text.value
            preprocessed_message, emotion, japanese_text = preprocess_message(text_content)
            
            if japanese_text:
                print(f"Japanese Text: {japanese_text}")
                style = map_emotion_to_style(emotion)
                data, sample_rate = await synthesize_speech(japanese_text, style)
                
                # 음성 생성 완료 후 전처리된 메시지를 웹소켓으로 전송
                await websocket.send(preprocessed_message)
                
                # 생성된 음성을 FastAPI 서버에 제공
                await play_audio_with_fastapi(data, sample_rate)
            else:
                await websocket.send(preprocessed_message)

async def get_or_create_thread():
    global thread_id
    if 'thread_id' not in globals():
        thread = client.beta.threads.create()
        thread_id = thread.id
    return thread_id

def preprocess_message(message):
    match = re.search(r'(.*)\[(\d+)\]\[(.*?)\]', message)
    if match:
        message_part = match.group(1)
        emotion = int(match.group(2))
        japanese_text = match.group(3)
        return f"{message_part}[{emotion}]", emotion, japanese_text
    return message, None, None

async def extract_text_from_audio_with_whisper(audio_file):
    with open(audio_file, "rb") as audio:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio,
            language="ko",
            response_format="text"
        )
    return response

async def synthesize_speech(japanese_text, style):
    adapter = Sbv2Adapter()
    data, sample_rate = adapter.get_voice(japanese_text, style)
    return data, sample_rate

def map_emotion_to_style(emotion):
    if emotion == 0:
        return "Sad"
    elif emotion == 6:
        return "Disgust"
    elif emotion == 5:
        return "Happy"
    else:
        return "Neutral"

async def main():
    message_queue = Queue()
    print("Starting tasks...")
    
    # FastAPI 서버 실행
    server = uvicorn.Server(config=uvicorn.Config(app, host="0.0.0.0", port=8000))
    server_task = asyncio.create_task(server.serve())
    
    # WebSocket 클라이언트 실행
    uri = "ws://localhost:3333"
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket server.")
        receive_task = asyncio.create_task(receive_messages(message_queue, websocket))
        trigger_task = asyncio.create_task(process_trigger(message_queue, websocket))
        await asyncio.gather(receive_task, trigger_task)
    
    print("Tasks started.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("WebSocket client terminated by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Press any key to exit...")
        exit(1)