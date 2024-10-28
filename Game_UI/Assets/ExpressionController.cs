using UnityEngine;
using Live2D.Cubism.Framework.Expression;

public class ExpressionController : MonoBehaviour
{
    // CubismExpressionController 컴포넌트에 대한 참조
    public CubismExpressionController expressionController;
    private int previousExpressionIndex = -1;

    void Update()
    {
        // Node.LatestNumber가 업데이트되었는지 확인하고, 업데이트되었으면 적용
        if (Node.LatestNumber != previousExpressionIndex)
        {
            Debug.Log($"Updating expression to index: {Node.LatestNumber}");
            expressionController.CurrentExpressionIndex = Node.LatestNumber;
            previousExpressionIndex = Node.LatestNumber;
        }
    }
}