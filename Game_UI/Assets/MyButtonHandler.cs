using UnityEngine;
using UnityEngine.UI;

public class MyButtonHandler : MonoBehaviour
{
    public Node node;

    void Start()
    {
        Button button = GetComponent<Button>();
        if (button == null)
        {
            Debug.LogError("Button component not found on this GameObject.");
            return;
        }
        
        button.onClick.AddListener(OnButtonClick);
        Debug.Log("Button listener added.");
    }

    void OnButtonClick()
    {

        // Node 스크립트의 SendTriggerSign 메서드를 호출
        if (node != null)
        {
            node.SendTriggerSign();
            Debug.Log("Node.SendTriggerSign called.");
        }
        else
        {
            Debug.LogError("Node reference is not set.");
        }
    }
}