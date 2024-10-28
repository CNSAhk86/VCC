using UnityEngine;
using Live2D.Cubism.Framework.MouthMovement;

public class MouthMover : MonoBehaviour
{
    private CubismMouthController mouthController;
    private TypeEffect typeEffect;

    private float currentMouthOpening = 0f;
    private float targetMouthOpening = 0f;
    private float mouthChangeSpeed = 2.0f;  
    private float nextChangeTime = 0f;

    void Start()
    {
        mouthController = GetComponent<CubismMouthController>();
        if (mouthController == null)
        {
            Debug.LogError("CubismMouthController component not found.");
        }

        typeEffect = FindObjectOfType<TypeEffect>();
        if (typeEffect == null)
        {
            Debug.LogError("TypeEffect component not found.");
        }
    }

    void Update()
    {
        if (mouthController != null && typeEffect != null)
        {
            if (typeEffect.hasStartedTyping && typeEffect.firstTypingDone)
            {
                if (typeEffect.isTyping)
                {
                    if (Time.time >= nextChangeTime)
                    {
                        targetMouthOpening = Random.Range(0.4f, 1f);  // 랜덤한 목표 입 모양 설정 (더 크게)
                        mouthChangeSpeed = Random.Range(2.0f, 6.0f);  // 랜덤한 속도로 변화
                        nextChangeTime = Time.time + Random.Range(0.05f, 0.15f);  // 랜덤한 시간 후에 변화
                    }
                }
                else
                {
                    // 타이핑 중이 아닐 때 입 모양을 천천히 닫음
                    targetMouthOpening = 0f;
                    mouthChangeSpeed = 1.5f;  // 입을 닫을 때의 속도를 느리게 설정
                }

                currentMouthOpening = Mathf.MoveTowards(currentMouthOpening, targetMouthOpening, mouthChangeSpeed * Time.deltaTime);
                mouthController.SetMouthOpening(currentMouthOpening);
            }
            else
            {
                // 첫 번째 타이핑이 완료되지 않았을 때 입 모양을 닫음
                currentMouthOpening = Mathf.MoveTowards(currentMouthOpening, 0f, 1.5f * Time.deltaTime);
                mouthController.SetMouthOpening(currentMouthOpening);
            }
        }
    }
}