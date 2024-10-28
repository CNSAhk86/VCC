import time
from openai import OpenAI

api_key = 'API 키 입력'
ASSISTANT_ID = '어시스턴트 키 입력'

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=api_key)

def create_thread_and_run(user_input):
    """새 스레드를 생성하고 사용자 입력으로 메시지를 제출한 후 실행합니다."""
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input,
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID,
    )
    return thread, run

def wait_on_run(run, thread):
    """Run의 상태가 완료될 때까지 대기합니다."""
    while run.status in ["queued", "in_progress"]:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def print_messages(thread):
    """스레드에서 모든 메시지를 출력합니다."""
    messages = client.beta.threads.messages.list(thread_id=thread.id, order="asc")
    for message in messages:
        role = message.role.upper()
        text = message.content[0].text.value
        print(f"[{role}]\n{text}\n")
    print("---" * 20)

inputs = [
    "GPT4 프롬프팅 테스트"
]

threads_and_runs = [create_thread_and_run(input) for input in inputs]

# 모든 실행이 완료될 때까지 기다립니다.
for thread, run in threads_and_runs:
    wait_on_run(run, thread)

# 각 스레드의 메시지를 출력합니다.
for thread, _ in threads_and_runs:
    print_messages(thread)