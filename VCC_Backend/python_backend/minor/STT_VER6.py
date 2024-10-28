import asyncio
import websockets
import sounddevice as sd
import soundfile as sf
from asyncio import Queue
import speech_recognition as sr
import json
import cv2
from openai import OpenAI
import re
import signal
import msvcrt  # 키 입력 감지를 위해 추가

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

def handle_exit(sig, frame):
    answer = input("Do you really want to exit? (y/n): ")
    if answer.lower() == 'y':
        print("Exiting program.")
        exit(0)

signal.signal(signal.SIGINT, handle_exit)

async def receive_messages(q: Queue):
    uri = "ws://localhost:3333"
    print("Trying to connect to WebSocket server...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket server.")
            while True:
                message = await websocket.recv()
                print(f"Received message: {message}")
                if q.qsize() < MAX_QUEUE_SIZE:
                    await q.put(message)
                    print("Message added to queue.")
                else:
                    print("Queue is full. Discarding the oldest message.")
                    q.get_nowait()
                    await q.put(message)
    except Exception as e:
        print(f"An error occurred while connecting or receiving: {e}")
        await asyncio.sleep(5)

async def record_and_process_audio(websocket):
    recording = False
    audio_data = []
    stream = None

    def callback(indata, frames, time, status):
        if recording:
            audio_data.append(indata.copy())

    while True:
        print("Waiting for recording trigger...")
        message = await websocket.recv()
        print(f"Processing message: {message}")
        message, japanese_text = preprocess_message(message)
        if japanese_text:
            print(f"Extracted Japanese text: {japanese_text}")

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
                    filename = "recorded_audio.wav"
                    audio_data = [item for sublist in audio_data for item in sublist]
                    sf.write(filename, audio_data, samplerate=44100)
                    text = extract_text_from_audio(filename)
                    if text:
                        print("Extracted text:", text)
                        await send_text_to_assistant(text, websocket)
                    else:
                        print("Failed to recognize speech. Please try again.")
        elif message == "Trigger Sign2":
            await handle_camera_and_send_image(websocket)
            print("Handled Trigger Sign2.")
        else:
            await websocket.send(message)

def extract_text_from_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        try:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data, language='ko-KR')
        except Exception as e:
            print(f"Error recognizing speech: {e}")
            return None

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
            image_path = 'image.png'
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

    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "이거 봐봐!"
                    },
                    {
                        "type": "image_file",
                        "image_file": {"file_id": file.id}
                    },
                ],
            }
        ]
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )

    while run.status in ["queued", "in_progress"]:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        await asyncio.sleep(0.5)

    messages = client.beta.threads.messages.list(thread_id=thread.id, order="asc")
    for message in messages:
        if message.role == "assistant":
            print(f"[ASSISTANT]\n{message.content[0].text.value}\n")
            preprocessed_message, japanese_text = preprocess_message(message.content[0].text.value)
            if japanese_text:
                print(f"Extracted Japanese text: {japanese_text}")
            await websocket.send(preprocessed_message)

async def send_text_to_assistant(text, websocket):
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=text
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )
    while run.status in ["queued", "in_progress"]:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        await asyncio.sleep(0.5)
    messages = client.beta.threads.messages.list(thread_id=thread.id, order="asc")
    for message in messages:
        if message.role == "assistant":
            print(f"[ASSISTANT]\n{message.content[0].text.value}\n")
            preprocessed_message, japanese_text = preprocess_message(message.content[0].text.value)
            if japanese_text:
                print(f"Extracted Japanese text: {japanese_text}")
            await websocket.send(preprocessed_message)

def preprocess_message(message):
    match = re.search(r'(\[.*?\])\[(.*?)\]', message)
    if match:
        message_part = match.group(1)
        japanese_text = match.group(2)
        message = message.replace(f"{message_part}[{japanese_text}]", message_part)
        return message, japanese_text
    return message, None

async def main():
    message_queue = Queue()
    print("Starting tasks...")
    uri = "ws://localhost:3333"
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket server.")
        receive_task = asyncio.create_task(receive_messages(message_queue))
        process_task = asyncio.create_task(process_messages(message_queue, websocket))
        await asyncio.gather(receive_task, process_task)
    print("Tasks started.")

async def process_messages(q: Queue, websocket):
    while True:
        message = await q.get()
        print(f"Processing message: {message}")
        message, japanese_text = preprocess_message(message)
        if japanese_text:
            print(f"Extracted Japanese text: {japanese_text}")
        
        if message == "Trigger Sign" or message == "start_record":
            await record_and_process_audio(websocket)
        elif message == "Trigger Sign2":
            await handle_camera_and_send_image(websocket)
        else:
            await websocket.send(message)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("WebSocket client terminated by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Press any key to exit...")
        msvcrt.getch()
        exit(1)
        
# 시작하자마자 이미지 인식 시키면 메세지를 계속 보내는 오류는 아직 수정하지 못했습니다.
# 음성 인식 쓰레드와 이미지 인식 쓰레드가 동일한 쓰레드에서 처리되는지도 확인이 필요합니다.
# 음성 대화 이후 이미지 인식을 진행시켜야 원활한 동작이 가능할 겁니다.