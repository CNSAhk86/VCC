using UnityEngine;
using WebSocketSharp;

public class WebSocketManager : MonoBehaviour
{
    private WebSocket ws;
    public string wsUrl = "ws://127.0.0.1:3333"; // WebSocket URL

    public void SetupWebSocketConnection()
    {
        ws = new WebSocket(wsUrl);
        ws.OnMessage += ws_OnMessage;
        ws.OnOpen += ws_OnOpen;
        ws.OnClose += ws_OnClose;
        ws.OnError += ws_OnError;

        ws.ConnectAsync();
    }

    private void ws_OnMessage(object sender, MessageEventArgs e)
    {
        Debug.Log($"WebSocket message received: {e.Data}");

        // 서버로부터 받은 메시지를 처리하여 latestMessage와 latestNumber에 저장합니다.
        string receivedData = e.Data;
        int bracketIndex = receivedData.LastIndexOf('[');
        if (bracketIndex != -1)
        {
            string message = receivedData.Substring(0, bracketIndex).Trim();
            string numberStr = receivedData.Substring(bracketIndex).Trim(' ', '[', ']');

            if (!int.TryParse(message, out _) || message.Length > 1)
            {
                Node.LatestMessage = message;
            }
            if (int.TryParse(numberStr, out int number))
            {
                Node.LatestNumber = number;
            }
        }
        else
        {
            if (!int.TryParse(receivedData, out _) || receivedData.Length > 1)
            {
                Node.LatestMessage = receivedData;
            }
            Node.LatestNumber = 0;
        }

        Debug.Log($"Updated latestMessage: {Node.LatestMessage}");
        Debug.Log($"Updated latestNumber: {Node.LatestNumber}");

        // 메시지 변경 감지
        if (Node.LatestMessage != Node.PreviousMessage)
        {
            UIController2.latestMessageChanged = true;
            Node.PreviousMessage = Node.LatestMessage;
        }
    }

    private void ws_OnOpen(object sender, System.EventArgs e)
    {
        Debug.Log("WebSocket connection opened");
    }

    private void ws_OnClose(object sender, CloseEventArgs e)
    {
        Debug.Log("WebSocket connection closed");
    }

    private void ws_OnError(object sender, ErrorEventArgs e)
    {
        Debug.LogError($"WebSocket error: {e.Message}");
    }

    public void SendWebSocketMessage(string message)
    {
        if (ws != null && ws.IsAlive)
        {
            ws.Send(message);
            Debug.Log($"Sent message: {message}");
        }
        else
        {
            Debug.LogError("WebSocket connection is not open.");
        }
    }

    private void OnDestroy()
    {
        if (ws != null)
        {
            ws.Close();
            Debug.Log("Closed WebSocket connection");
        }
    }
}