import asyncio
import websockets
import sounddevice as sd
import soundfile as sf
from asyncio import Queue
import speech_recognition as sr

# 큐의 최대 크기 설정
MAX_QUEUE_SIZE = 10

async def receive_messages(q: Queue):
    uri = "ws://localhost:3333"  # WebSocket 서버의 주소 및 포트 번호
    try:
        async with websockets.connect(uri) as websocket:
            while True:
                message = await websocket.recv()
                print(f"Received message from Unity client: {message}")
                # 큐에 메시지를 넣을 때 큐의 크기가 한계값을 초과하는지 확인
                if q.qsize() < MAX_QUEUE_SIZE:
                    await q.put(message)  # 메시지를 큐에 추가
                else:
                    print("Queue is full. Discarding the oldest message.")
                    q.get_nowait()  # 큐에서 가장 오래된 메시지 제거
                    await q.put(message)  # 새로운 메시지 추가
    except Exception as e:
        print(f"An error occurred: {e}")
        # 에러 발생 시 잠시 대기 후 다시 연결을 시도함
        await asyncio.sleep(5)

async def record_audio(q: Queue):
    recording = False
    audio_data = []
    stream = None
    
    def callback(indata, frames, time, status):
        if status:
            print(status)
        if recording:
            audio_data.append(indata.copy())
    
    while True:
        message = await q.get()  # 큐에서 메시지를 가져옴
        if message == "Trigger Sign":
            if not recording:
                print("Recording started...")
                recording = True
                audio_data = []  # 이전 오디오 데이터를 초기화
                stream = sd.InputStream(callback=callback)
                stream.start()
            else:
                print("Recording stopped.")
                recording = False
                if stream:
                    stream.stop()
                    stream.close()
                    stream = None
                    # 오디오 파일로 저장
                    filename = "recorded_audio.wav"
                    audio_data = [item for sublist in audio_data for item in sublist]
                    sf.write(filename, audio_data, samplerate=44100)
                    print(f"Audio file saved as '{filename}'")
                    # 텍스트 추출
                    text = extract_text_from_audio(filename)
                    if text:
                        print("Extracted text:", text)
                    else:
                        print("음성 인식 실패. 다시 시도하세요.")
        elif message == "stop_record":
            if recording:
                print("Recording stopped.")
                recording = False
                if stream:
                    stream.stop()
                    stream.close()
                    stream = None
                    # 오디오 파일로 저장
                    filename = "recorded_audio.wav"
                    audio_data = [item for sublist in audio_data for item in sublist]
                    sf.write(filename, audio_data, samplerate=44100)
                    print(f"Audio file saved as '{filename}'")
                    # 텍스트 추출
                    text = extract_text_from_audio(filename)
                    if text:
                        print("Extracted text:", text)
                    else:
                        print("음성 인식 실패. 다시 시도하세요.")

def extract_text_from_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        try:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language='ko-KR')  # 한국어로 설정
            return text
        except sr.UnknownValueError:
            print("음성을 인식할 수 없습니다.")
            return None
        except sr.RequestError as e:
            print("음성 인식 서비스를 요청할 수 없습니다; {0}".format(e))
            return None

async def main():
    message_queue = Queue()
    receive_task = asyncio.create_task(receive_messages(message_queue))
    record_task = asyncio.create_task(record_audio(message_queue))
    await asyncio.gather(receive_task, record_task)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("WebSocket client terminated by user.")