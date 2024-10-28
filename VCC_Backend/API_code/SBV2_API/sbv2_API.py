import requests
import io
import soundfile as sf
import sounddevice as sd

class Sbv2Adapter:
    URL = "http://127.0.0.1:5000/voice"

    def __init__(self) -> None:
        pass

    def _create_audio_query(self, text: str) -> dict:
        params = {
            "text": text,
            "speaker_id": 0,
            "model_id": 1,
            "length": 1,
            "sdp_ratio": 0.2,
            "noise": 0.6,
            "noisew": 0.8,
            "auto_split": True,
            "split_interval": 1,
            "language": "JP",
            "style": "Neutral",
            "style_weight": 5,
        }
        return params

    def _create_request_audio(self, query_data: dict) -> bytes:
        headers = {"accept": "audio/wav"}
        response = requests.get(self.URL, params=query_data, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code}")
        return response.content

    def get_voice(self, text: str):
        query_data = self._create_audio_query(text)
        audio_bytes = self._create_request_audio(query_data)
        audio_stream = io.BytesIO(audio_bytes)
        data, sample_rate = sf.read(audio_stream)
        return data, sample_rate

def main():
    text = "さようなら。"  # 합성할 일본어 텍스트 작성하는 부분
    adapter = Sbv2Adapter()
    data, sample_rate = adapter.get_voice(text)
    # 파일 저장
    output_file = 'audio.wav'
    sf.write(output_file, data, sample_rate)
    print(f'Audio saved to {output_file}')
    print(f'Playing {output_file}')
    data, sample_rate = sf.read(output_file)
    sd.play(data, sample_rate)
    sd.wait()

if __name__ == "__main__":
    main()