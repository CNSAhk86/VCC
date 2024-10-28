using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;

public class Node : MonoBehaviour
{
    private static Node instance;

    private int triggerSignCount = 0; // Trigger Sign 클릭 횟수

    public string audioUrl = "http://localhost:8000/audio/synthesized_audio.wav"; // FastAPI 서버의 GET 요청 URL
    private AudioSource audioSource;
    private Motion motion; // Motion 스크립트 참조

    private WebSocketManager webSocketManager;
    private SSEManager sseManager;

    public static string LatestMessage { get; set; } = "(대화를 시작하려면 아래의 버튼을 눌러 상호작용해보세요!)";
    public static int LatestNumber { get; set; } = 7;  // 초기 숫자를 설정
    public static string PreviousMessage { get; set; }

    private void Awake()
    {
        if (instance == null)
        {
            instance = this;
            DontDestroyOnLoad(gameObject);
            Debug.Log("Node instance created");
        }
        else
        {
            Destroy(gameObject);
            Debug.Log("Duplicate Node instance destroyed");
        }
    }

    private void Start()
    {
        if (instance != this) return;

        Debug.Log("Starting Node");

        // AudioSource 설정
        audioSource = GameObject.Find("Voice").GetComponent<AudioSource>();
        if (audioSource == null)
        {
            Debug.LogError("Voice AudioSource component not found in the scene.");
            return;
        }
        Debug.Log("AudioSource found");

        // Motion 설정
        motion = FindObjectOfType<Motion>(); // Motion 스크립트를 가진 오브젝트를 검색하여 참조합니다.
        if (motion == null)
        {
            Debug.LogError("Motion component not found in the scene.");
            return;
        }
        Debug.Log("Motion component found");

        // WebSocketManager와 SSEManager 설정
        webSocketManager = gameObject.AddComponent<WebSocketManager>();
        sseManager = gameObject.AddComponent<SSEManager>();

        // 버튼 이벤트 설정
        Button button = GameObject.Find("Button").GetComponent<Button>();
        button.onClick.AddListener(SendTriggerSign);
        Debug.Log("Trigger Sign button event set");

        Button imageButton = GameObject.Find("Image-Button").GetComponent<Button>();
        imageButton.onClick.AddListener(SendTriggerSign2);
        Debug.Log("Trigger Sign2 button event set");

        // WebSocket 및 SSE 연결 시작
        webSocketManager.SetupWebSocketConnection();
        StartCoroutine(sseManager.SetupSSEConnection());
    }

    // 버튼을 눌렀을 때 호출되는 함수입니다.
    public void SendTriggerSign()
    {
        Debug.Log("Sending Trigger Sign message to server");
        webSocketManager.SendWebSocketMessage("Trigger Sign");

        if (UIController.variable == 0)
        {
            UIController.variable = 1;
            Debug.Log("UIController.variable set to 1");
        }
        else
        {
            UIController.variable = 0;
            Debug.Log("UIController.variable set to 0");
        }

        triggerSignCount++;

        if (triggerSignCount % 2 == 0)
        {
            UIController2.triggerSent = true;
        }
        else
        {
            UIController2.triggerSent = false;
        }

        Debug.Log($"Trigger Sign sent. Count: {triggerSignCount}");

        if (motion != null)
        {
            motion.StopAllAudio();
            Debug.Log("Stopped all audio in motion component");
        }
        else
        {
            Debug.LogError("Motion reference is not set.");
        }
    }

    // 이미지 버튼을 눌렀을 때 호출되는 함수입니다.
    public void SendTriggerSign2()
    {
        Debug.Log("Sending Trigger Sign2 message to server");
        webSocketManager.SendWebSocketMessage("Trigger Sign2");

        UIController2.triggerSent = true;
        Debug.Log("Trigger Sign2 sent");

        if (motion != null)
        {
            motion.StopAllAudio();
            Debug.Log("Stopped all audio in motion component");
        }
        else
        {
            Debug.LogError("Motion reference is not set.");
        }
    }

    // 오디오 파일을 다운로드하고 재생하는 메서드입니다.
    public void DownloadAndPlayAudio()
    {
        Debug.Log("Starting DownloadAndPlayAudio method");
        StartCoroutine(DownloadAndPlayAudioCoroutine());
    }

    // 오디오 파일을 다운로드하고 재생하는 코루틴입니다.
    private IEnumerator DownloadAndPlayAudioCoroutine()
    {
        Debug.Log("Starting DownloadAudioCoroutine");
        using (UnityWebRequest www = UnityWebRequestMultimedia.GetAudioClip(audioUrl, AudioType.WAV))
        {
            yield return www.SendWebRequest();

            if (www.result == UnityWebRequest.Result.ConnectionError || www.result == UnityWebRequest.Result.ProtocolError)
            {
                Debug.LogError($"Error downloading audio clip: {www.error}");
                Debug.LogError($"Response Code: {www.responseCode}");
                Debug.LogError($"Response Length: {www.downloadHandler.data.Length}");
            }
            else
            {
                Debug.Log("Audio clip downloaded successfully");
                Debug.Log($"Response Code: {www.responseCode}");
                Debug.Log($"Response Length: {www.downloadHandler.data.Length}");

                AudioClip audioClip = DownloadHandlerAudioClip.GetContent(www);
                if (audioClip == null)
                {
                    Debug.LogError("Failed to load AudioClip from server response");
                }
                else
                {
                    Debug.Log("Playing downloaded audio clip");
                    PlayAudioClip(audioClip);
                }
            }
        }
    }

    // 오디오 클립을 재생하는 메서드입니다.
    private void PlayAudioClip(AudioClip clip)
    {
        if (audioSource.isPlaying)
        {
            audioSource.Stop();
            Debug.Log("Stopped currently playing audio");
        }
        audioSource.clip = clip;
        audioSource.Play();
        Debug.Log("Started playing audio clip");
    }

    // 인스턴스를 반환하는 정적 메서드입니다.
    public static Node GetInstance()
    {
        return instance;
    }
}