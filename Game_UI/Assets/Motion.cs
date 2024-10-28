using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Motion : MonoBehaviour
{
    private Animator mAnimator;
    public AudioSource[] audioSources; // 여러 AudioSource를 참조할 배열
    private int previousNumber = -1;

    void Start()
    {
        mAnimator = GetComponent<Animator>();
        if (mAnimator == null)
        {
            Debug.LogError("Animator component not found on " + gameObject.name);
        }
        if (audioSources == null || audioSources.Length == 0)
        {
            Debug.LogError("Audio sources not assigned or empty.");
        }
        else
        {
            foreach (AudioSource audioSource in audioSources)
            {
                audioSource.playOnAwake = false; // 오디오가 시작할 때 재생되지 않도록 설정
            }
        }
    }

    // Update is called once per frame
    void Update()
    {
        if (mAnimator != null)
        {
            int currentNumber = Node.LatestNumber; // 현재 Node.LatestNumber 값 가져오기

            // 이전 값과 현재 값이 다를 때만 트리거 설정
            if (currentNumber != previousNumber)
            {
                Debug.Log("Setting Trigger for: " + currentNumber);
                switch (currentNumber)
                {
                    case 0:
                        mAnimator.SetTrigger("crying");
                        break;
                    case 1:
                        mAnimator.SetTrigger("sulky");
                        break;
                    case 2:
                        mAnimator.SetTrigger("shyness");
                        break;
                    case 3:
                        mAnimator.SetTrigger("teasing");
                        break;
                    case 4:
                        mAnimator.SetTrigger("singing");
                        if (audioSources.Length > 0)
                        {
                            StartCoroutine(PlayRandomClipWithDelay(4f)); // 4초 지연 후 랜덤 오디오 클립 재생
                        }
                        break;
                    case 5:
                        mAnimator.SetTrigger("affection");
                        break;
                    case 6:
                        mAnimator.SetTrigger("serious");
                        break;
                    case 7:
                        mAnimator.SetTrigger("normal");
                        break;
                    default:
                        Debug.LogWarning("Unhandled LatestNumber value: " + currentNumber);
                        break;
                }

                // 이전 값을 현재 값으로 업데이트
                previousNumber = currentNumber;
            }
        }
    }

    private IEnumerator PlayRandomClipWithDelay(float delay)
    {
        yield return new WaitForSeconds(delay); // 지연 시간 대기

        // 랜덤 오디오 소스 선택
        int randomIndex = Random.Range(0, audioSources.Length);
        AudioSource randomSource = audioSources[randomIndex];

        Debug.Log("Playing clip: " + randomSource.clip.name);

        randomSource.Play();
    }

    // 모든 오디오 소스를 정지시키는 메서드 추가
    public void StopAllAudio()
    {
        Debug.Log("Stopping all audio sources...");
        foreach (AudioSource audioSource in audioSources)
        {
            audioSource.Stop();
            Debug.Log("Stopped audio: " + audioSource.clip.name);
        }
        Debug.Log("All audio sources stopped.");
    }
}