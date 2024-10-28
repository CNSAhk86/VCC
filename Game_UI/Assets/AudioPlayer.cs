// using System.Collections;
// using UnityEngine;
// using UnityEngine.Networking;
// using System.Text.RegularExpressions;

// public class AudioPlayer : MonoBehaviour
// {
//     public string audioUrl = "http://localhost:8000/audio/synthesized_audio.wav"; // FastAPI 서버의 GET 요청 URL
//     public string eventUrl = "http://localhost:8000/events"; // FastAPI 서버의 SSE 이벤트 URL
//     private AudioSource audioSource;

//     void Start()
//     {
//         audioSource = gameObject.AddComponent<AudioSource>();
//         Debug.Log("AudioSource component added.");
//         StartCoroutine(ListenForAudioUpdates());
//     }

//     private IEnumerator ListenForAudioUpdates()
//     {
//         Debug.Log("Starting ListenForAudioUpdates coroutine.");
//         using (UnityWebRequest www = UnityWebRequest.Get(eventUrl))
//         {
//             www.SetRequestHeader("Accept", "text/event-stream");
//             yield return www.SendWebRequest();

//             if (www.result == UnityWebRequest.Result.ConnectionError || www.result == UnityWebRequest.Result.ProtocolError)
//             {
//                 Debug.LogError(www.error);
//             }
//             else
//             {
//                 Debug.Log("SSE connection established.");
//                 string responseText = www.downloadHandler.text;
//                 string[] events = Regex.Split(responseText, @"\r\n\r\n");
//                 foreach (string evt in events)
//                 {
//                     if (evt.StartsWith("data:"))
//                     {
//                         Debug.Log("New audio file available");
//                         DownloadAndPlayAudio();
//                     }
//                 }
//             }
//         }
//     }

//     public void DownloadAndPlayAudio()
//     {
//         Debug.Log("Starting DownloadAndPlayAudio.");
//         StartCoroutine(DownloadAudioCoroutine());
//     }

//     private IEnumerator DownloadAudioCoroutine()
//     {
//         Debug.Log("Starting DownloadAudioCoroutine.");
//         using (UnityWebRequest www = UnityWebRequestMultimedia.GetAudioClip(audioUrl, AudioType.WAV))
//         {
//             yield return www.SendWebRequest();

//             if (www.result == UnityWebRequest.Result.ConnectionError || www.result == UnityWebRequest.Result.ProtocolError)
//             {
//                 Debug.LogError(www.error);
//             }
//             else
//             {
//                 Debug.Log("Audio clip downloaded successfully.");
//                 AudioClip audioClip = DownloadHandlerAudioClip.GetContent(www);
//                 if (audioClip == null)
//                 {
//                     Debug.LogError("Failed to load AudioClip from server response.");
//                 }
//                 else
//                 {
//                     Debug.Log("Playing downloaded audio clip.");
//                     PlayAudioClip(audioClip);
//                 }
//             }
//         }
//     }

//     private void PlayAudioClip(AudioClip clip)
//     {
//         if (audioSource.isPlaying)
//         {
//             audioSource.Stop();
//         }
//         audioSource.clip = clip;
//         audioSource.Play();
//         Debug.Log("Playing audio clip...");
//     }
// }