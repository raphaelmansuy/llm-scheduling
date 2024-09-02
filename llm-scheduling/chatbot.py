import os
from openai import OpenAI
import json
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

# Load your OpenAI API key from an environment variable
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Load the system prompt from the file
with open('task/prompt.md', 'r') as file:
    system_prompt = file.read()

def get_response(messages):
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="gpt-4o-mini",  # Changed to gpt-4o-mini
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def print_conversation_history(conversation):
    for message in conversation[1:]:  # Skip the system message
        if message['role'] == 'user':
            print(f"{Fore.CYAN}User: {message['content']}")
        else:
            print(f"{Fore.GREEN}AI: {message['content']}\n")

def main():
    conversation = [{"role": "system", "content": system_prompt}]
    
    print(f"{Fore.YELLOW}Welcome to your AI assistant powered by gpt-4o-mini!")
    print(f"{Fore.YELLOW}Type 'exit' or 'quit' to end the conversation.")
    print(f"{Fore.YELLOW}Type 'history' to view the conversation history.")
    print(f"{Fore.YELLOW}Type 'clear' to clear the conversation history.\n")
    
    while True:
        user_input = input(f"{Fore.CYAN}You: ")
        
        if user_input.lower() in ["exit", "quit"]:
            break
        elif user_input.lower() == "history":
            print_conversation_history(conversation)
        elif user_input.lower() == "clear":
            conversation = [{"role": "system", "content": system_prompt}]
            print(f"{Fore.YELLOW}Conversation history cleared.")
        else:
            conversation.append({"role": "user", "content": user_input})
            
            ai_response = get_response(conversation)
            
            print(f"{Fore.GREEN}AI: {ai_response}\n")
            
            conversation.append({"role": "assistant", "content": ai_response})
    
    # Save the conversation to a JSON file
    if len(conversation) > 1:
        with open('conversation.json', 'w') as json_file:
            json.dump(conversation, json_file, indent=4)
        print(f"{Fore.YELLOW}Your conversation has been saved to 'conversation.json'.")
    
    print(f"{Fore.YELLOW}Thank you for using the AI assistant. Goodbye!")

if __name__ == "__main__":
    main()