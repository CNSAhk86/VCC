using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;
using System.Collections;

public class SceneTransition : MonoBehaviour
{
    public Image fadeImage;
    public float fadeDuration = 1.5f;
    private AudioSource audioSource; // AudioSource 필드

    void Start()
    {
        // AudioSource 컴포넌트를 가져옴
        audioSource = GetComponent<AudioSource>();
        // 시작 시 페이드 인
        StartCoroutine(FadeIn());
    }

    public void OnButtonClicked(string sceneName)
    {
        // 버튼 클릭 시 페이드 아웃 후 장면 전환
        StartCoroutine(FadeOutAndLoadScene(sceneName));
    }

    IEnumerator FadeIn()
    {
        float t = fadeDuration;
        while (t > 0f)
        {
            t -= Time.deltaTime;
            float alpha = t / fadeDuration;
            fadeImage.color = new Color(0f, 0f, 0f, alpha);
            if (audioSource != null)
            {
                audioSource.volume = 1f - alpha; // 음량 증가
            }
            yield return null;
        }
        fadeImage.color = new Color(0f, 0f, 0f, 0f);
        if (audioSource != null)
        {
            audioSource.volume = 1f; // 음량을 완전히 켬
        }
    }

    IEnumerator FadeOutAndLoadScene(string sceneName)
    {
        float t = 0f;
        while (t < fadeDuration)
        {
            t += Time.deltaTime;
            float alpha = t / fadeDuration;
            fadeImage.color = new Color(0f, 0f, 0f, alpha);
            if (audioSource != null)
            {
                audioSource.volume = 1f - alpha; // 음량 감소
            }
            yield return null;
        }
        fadeImage.color = new Color(0f, 0f, 0f, 1f);
        if (audioSource != null)
        {
            audioSource.volume = 0f; // 음량을 완전히 끔
        }
        SceneManager.LoadScene(sceneName);
    }
}