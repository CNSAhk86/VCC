import asyncio
import websockets
import sounddevice as sd
import soundfile as sf
from asyncio import Queue
import speech_recognition as sr
import time
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

def extract_text_from_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        try:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data, language='ko-KR')
        except Exception as e:
            print(f"Error recognizing speech: {e}")
            return None

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
            content = message.content[0].text.value
            print(f"[ASSISTANT]\n{content}\n")
            # 응답에서 답변과 번호를 분리
            try:
                answer, number = content.rsplit(' ', 1)
                number = number.strip("[]")
                await websocket.send(answer)
                await websocket.send(number)
            except ValueError:
                print("Failed to split the content properly.")
                await websocket.send(content)  # 형식이 다를 경우 전체 응답 전송
    print("---" * 20)

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