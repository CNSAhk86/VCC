using System.Collections;
using TMPro;
using UnityEngine;

public class TypeEffect : MonoBehaviour
{
    public TMP_Text textComponent;  // TextMeshPro 컴포넌트
    public float delayBetweenCharacters = 0.1f;  // 문자 간 딜레이
    private string currentMessage = "";  // 현재 타이핑 중인 메시지
    public bool isTyping = false;  // 타이핑 중인지 여부
    public bool hasStartedTyping = false;  // 타이핑이 시작되었는지 여부
    public bool firstTypingDone = false;  // 첫 번째 타이핑 완료 여부

    void Start()
    {
        if (textComponent == null)
        {
            Debug.LogError("TextMeshPro component is not assigned!");
            return;
        }
        // 초기 메시지 타이핑 시작
        StartCoroutine(TypeText("(대화를 시작하려면 아래의 버튼을 눌러 상호작용하세요!)"));
    }

    void Update()
    {
        // Node.LatestMessage가 null이 아니고, 현재 메시지와 다를 때만 처리
        if (Node.LatestMessage != null && Node.LatestMessage != currentMessage)
        {
            currentMessage = Node.LatestMessage;
            StopAllCoroutines();  // 현재 진행 중인 타이핑 코루틴을 중단
            StartCoroutine(TypeText(currentMessage));  // 새 메시지 타이핑 시작
        }
    }

    IEnumerator TypeText(string textToType)
    {
        isTyping = true;  // 타이핑 시작
        textComponent.text = "";  // 텍스트 컴포넌트를 비움
        foreach (char letter in textToType)
        {
            textComponent.text += letter;  // 문자를 하나씩 추가
            yield return new WaitForSeconds(delayBetweenCharacters);
        }
        currentMessage = textToType;  // 타이핑이 끝난 메시지를 현재 메시지로 설정
        isTyping = false;  // 타이핑 종료
        hasStartedTyping = true;  // 타이핑이 시작되었음을 표시

        // 첫 번째 타이핑이 완료되었음을 표시
        if (!firstTypingDone)
        {
            firstTypingDone = true;
        }
    }
}