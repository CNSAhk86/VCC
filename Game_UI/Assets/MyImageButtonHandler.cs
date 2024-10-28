using UnityEngine;
using UnityEngine.UI;

public class MyImageButtonHandler : MonoBehaviour
{
    public Node node;

    void Start()
    {
        Button button = GetComponent<Button>();
        button.onClick.AddListener(OnImageButtonClick);
    }

    void OnImageButtonClick()
    {
        node.SendTriggerSign2();
    }
}