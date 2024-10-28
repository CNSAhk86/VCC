using System.Collections;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public class SceneTransition2 : MonoBehaviour
{
    public Image fadeImage;          // 페이드 이미지를 위한 UI Image
    public float fadeDuration = 1f;  // 페이드 인/아웃 지속 시간
    public float waitTime = 5f;      // 다음 씬으로 넘어가기 전 대기 시간

    void Start()
    {
        // 시작 시 페이드 인
        StartCoroutine(FadeIn());

        // 일정 시간이 지나면 다음 씬으로 전환
        StartCoroutine(TransitionAfterTime());
    }

    IEnumerator FadeIn()
    {
        float t = fadeDuration;
        while (t > 0f)
        {
            t -= Time.deltaTime;
            fadeImage.color = new Color(0f, 0f, 0f, t / fadeDuration);
            yield return null;
        }
        fadeImage.color = new Color(0f, 0f, 0f, 0f);
    }

    IEnumerator FadeOutAndLoadScene(string sceneName)
    {
        float t = 0f;
        while (t < fadeDuration)
        {
            t += Time.deltaTime;
            fadeImage.color = new Color(0f, 0f, 0f, t / fadeDuration);
            yield return null;
        }
        fadeImage.color = new Color(0f, 0f, 0f, 1f);
        SceneManager.LoadScene(sceneName);
    }

    IEnumerator TransitionAfterTime()
    {
        // 지정된 시간 동안 대기
        yield return new WaitForSeconds(waitTime);

        // 페이드 아웃 후 다음 씬으로 전환
        StartCoroutine(FadeOutAndLoadScene("Chat")); // "NextSceneName"을 실제 씬 이름으로 변경
    }
}