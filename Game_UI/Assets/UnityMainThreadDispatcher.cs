using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System;

public class UnityMainThreadDispatcher : MonoBehaviour
{
    private static readonly Queue<Action> _executionQueue = new Queue<Action>();

    public static UnityMainThreadDispatcher Instance() {
        return FindObjectOfType<UnityMainThreadDispatcher>();
    }

    public void Enqueue(Action action) {
        lock (_executionQueue) {
            _executionQueue.Enqueue(action);
        }
    }

    void Update() {
        while (_executionQueue.Count > 0) {
            _executionQueue.Dequeue().Invoke();
        }
    }
}