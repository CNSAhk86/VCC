from openai import OpenAI

api_key = 'sk-proj-791sIvdv01kwVTveNwELT3BlbkFJiu6rvaxwA5N5EcTaLLJV'
ASSISTANT_ID = 'asst_yJuMr3KHNBUDIXgBhhO14A8f'
client = OpenAI(api_key=api_key)

# Step 1: Upload the image
file = client.files.create(
    file=open("image.png", "rb"),
    purpose="vision"
)

print(file)

# Step 2: Create a new thread with the image
thread = client.beta.threads.create(
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "이거 봐봐 사진이야!"
                },
                {
                    "type": "image_file",
                    "image_file": {"file_id": file.id}
                },
            ],
        }
    ]
)

# Step 3: Create a run for the thread
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=ASSISTANT_ID
)

# Wait for the run to complete and fetch the results
while run.status in ["queued", "in_progress"]:
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )

# Retrieve messages to get the assistant's response
messages = client.beta.threads.messages.list(thread_id=thread.id, order="asc")
for message in messages:
    if message.role == "assistant":
        print(f"[ASSISTANT]\n{message.content[0].text.value}\n")