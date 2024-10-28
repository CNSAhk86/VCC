using UnityEngine;
using System.Collections;

public class UIController : MonoBehaviour
{
    public static int variable = 0; // 전역 변수처럼 사용할 static 변수

    private Transform spriteTransform; // 현재 오브젝트의 Transform

    private Vector3 initialPosition;
    private Vector3 targetPosition;
    private bool isTransitioning = false;
    private float transitionDuration = 0.5f; // 트랜지션 지속 시간

    void Start()
    {
        // 현재 오브젝트의 Transform을 가져옵니다.
        spriteTransform = GetComponent<Transform>();
        if (spriteTransform == null)
        {
            Debug.LogError("Transform component is missing on this GameObject.");
            return;
        }

        // Transform의 초기 위치를 설정합니다.
        initialPosition = spriteTransform.localPosition;
        targetPosition = initialPosition + new Vector3(0, -2, 0); // 초기 위치에서 아래로 2 단위만큼 이동
    }

    void Update()
    {
        if (spriteTransform == null) return;

        if (!isTransitioning)
        {
            if (variable == 1 && spriteTransform.localPosition != targetPosition)
            {
                StartCoroutine(MoveToPosition(targetPosition));
            }
            else if (variable == 0 && spriteTransform.localPosition != initialPosition)
            {
                StartCoroutine(MoveToPosition(initialPosition));
            }
        }
    }

    private IEnumerator MoveToPosition(Vector3 targetPos)
    {
        isTransitioning = true;
        float elapsedTime = 0;
        Vector3 startingPos = spriteTransform.localPosition;

        while (elapsedTime < transitionDuration)
        {
            float t = elapsedTime / transitionDuration;
            t = t < 0.5f ? 2 * t * t : -1 + (4 - 2 * t) * t; // Ease In Out Quad
            spriteTransform.localPosition = Vector3.Lerp(startingPos, targetPos, t);
            elapsedTime += Time.deltaTime;
            yield return null;
        }

        spriteTransform.localPosition = targetPos;
        isTransitioning = false;
    }
}