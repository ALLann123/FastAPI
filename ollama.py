from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="qwen2.5:3b-instruct",   # <-- changed
    temperature=0.8,
    num_predict=256,
)

while True:
    userInput=input("USER: ")

    if userInput=="exit" or userInput == "quit":
        print(f"AI: Goodbye")
        break
    messages = [
        ("system", "You are a helpful assistant."),
        ("human", userInput),
    ]

    response = llm.invoke(messages)
    print(response.content)
    print("\n")

