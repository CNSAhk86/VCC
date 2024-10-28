import asyncio
import websockets
import sounddevice as sd
import soundfile as sf
from asyncio import Queue
import speech_recognition as sr
import cv2
import json
from openai import OpenAI

api_key = 'sk-proj-791sIvdv01kwVTveNwELT3BlbkFJiu6rvaxwA5N5EcTaLLJV'
ASSISTANT_ID = 'asst_yJuMr3KHNBUDIXgBhhO14A8f'
client = OpenAI(api_key=api_key)

MAX_QUEUE_SIZE = 10

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

async def record_and_process_audio(q: Queue, websocket):
    recording = False
    audio_data = []
    stream = None

    def callback(indata, frames, time, status):
        if recording:
            audio_data.append(indata.copy())

    while True:
        message = await q.get()
        print(f"Processing message: {message}")  # 메시지 처리 상태 출력
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
                        await send_text_to_assistant(text, websocket)  # 응답을 WebSocket으로 전송
                    else:
                        print("Failed to recognize speech. Please try again.")
        elif message == "Trigger Sign2":
            await handle_camera_and_send_image(websocket)
            print("Handled Trigger Sign2.")

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

    # Send image to OpenAI and get a response
    await send_image_to_assistant(image_path, websocket)

async def send_image_to_assistant(image_path, websocket):
    # Step 1: Upload the image
    file = client.files.create(
        file=open(image_path, "rb"),
        purpose="vision"
    )
    print(file)

    # Step 2: Create a new thread with the image
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

    # Step 3: Create a run for the thread
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )

    # Wait for the run to complete and fetch the results
    while run.status in ["queued", "in_progress"]:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        await asyncio.sleep(0.5)

    # Retrieve messages to get the assistant's response
    messages = client.beta.threads.messages.list(thread_id=thread.id, order="asc")
    for message in messages:
        if message.role == "assistant":
            print(f"[ASSISTANT]\n{message.content[0].text.value}\n")
            await websocket.send(message.content[0].text.value)

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
        if message.role == "assistant":  # Assistant의 응답만 처리
            print(f"[ASSISTANT]\n{message.content[0].text.value}\n")
            await websocket.send(message.content[0].text.value)  # 응답을 WebSocket 서버로 전송

async def main():
    message_queue = Queue()
    print("Starting tasks...")
    uri = "ws://localhost:3333"
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket server.")
        receive_task = asyncio.create_task(receive_messages(message_queue))
        record_task = asyncio.create_task(record_and_process_audio(message_queue, websocket))  # websocket 인자 추가
        await asyncio.gather(receive_task, record_task)
    print("Tasks started.")

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("WebSocket client terminated by user.")