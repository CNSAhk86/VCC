using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using System.Text;

public class SSEManager : MonoBehaviour
{
    public string sseUrl = "http://localhost:8000/events"; // SSE 이벤트 URL

    public IEnumerator SetupSSEConnection()
    {
        Debug.Log("Starting SSE connection...");

        while (true)
        {
            UnityWebRequest request = new UnityWebRequest(sseUrl);
            request.method = UnityWebRequest.kHttpVerbGET;
            request.downloadHandler = new SSEDownloadHandler();

            yield return request.SendWebRequest();

            if (request.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError($"Error connecting to SSE: {request.error}");
                yield return new WaitForSeconds(5); // 연결 실패 시 5초 대기 후 재시도
            }
            else
            {
                Debug.Log("SSE connection established");
                while (!request.isDone)
                {
                    yield return null; // SSE 연결을 유지합니다.
                }
            }
        }
    }

    private class SSEDownloadHandler : DownloadHandlerScript
    {
        private StringBuilder sseBuffer = new StringBuilder();

        public SSEDownloadHandler() : base(new byte[1024]) { }

        protected override bool ReceiveData(byte[] data, int dataLength)
        {
            if (data == null || data.Length < 1)
            {
                return false;
            }

            string receivedString = Encoding.UTF8.GetString(data, 0, dataLength);
            sseBuffer.Append(receivedString);

            while (true)
            {
                int newlineIndex = sseBuffer.ToString().IndexOf("\n");
                if (newlineIndex == -1)
                {
                    break;
                }

                string line = sseBuffer.ToString().Substring(0, newlineIndex).Trim();
                sseBuffer.Remove(0, newlineIndex + 1);

                Debug.Log($"SSE line: {line}"); // 각 라인을 로깅
                if (line.StartsWith("data: "))
                {
                    string eventData = line.Substring("data: ".Length);
                    OnSSEMessage(eventData);
                }
            }

            return true;
        }

        private void OnSSEMessage(string message)
        {
            Debug.Log($"SSE message received: {message}");

            // 메시지를 받으면 오디오를 다운로드하고 재생
            Node.GetInstance().DownloadAndPlayAudio();
        }
    }
}