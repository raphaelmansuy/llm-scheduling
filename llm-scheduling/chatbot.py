import os
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall
import json
from colorama import Fore, Style, init
from datetime import datetime

# Initialize colorama for colored output
init(autoreset=True)

# Load your OpenAI API key from an environment variable
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Load the system prompt from the file
with open('task/prompt.md', 'r') as file:
    system_prompt = file.read()

def get_appointment_json():
    return {
        "name": "get_appointment_json",
        "description": "Generate a JSON object containing all relevant appointment information",
        "parameters": {
            "type": "object",
            "properties": {
                "patient": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "date_of_birth": {"type": "string"},
                        "contact": {
                            "type": "object",
                            "properties": {
                                "phone": {"type": "string"},
                                "email": {"type": "string"}
                            }
                        },
                        "patient_type": {"type": "string", "enum": ["new", "existing"]}
                    }
                },
                "appointment": {
                    "type": "object",
                    "properties": {
                        "reason": {"type": "string"},
                        "symptoms": {"type": "array", "items": {"type": "string"}},
                        "urgency_level": {"type": "string", "enum": ["routine", "urgent", "emergency"]},
                        "date_time": {"type": "string"},
                        "department": {"type": "string"},
                        "physician": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "specialty": {"type": "string"}
                            }
                        },
                        "type": {"type": "string", "enum": ["in-person", "virtual"]}
                    }
                },
                "instructions": {
                    "type": "object",
                    "properties": {
                        "pre_appointment": {"type": "array", "items": {"type": "string"}},
                        "required_documents": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "additional_services": {
                    "type": "object",
                    "properties": {
                        "tests_scheduled": {"type": "array", "items": {"type": "string"}},
                        "parking_info": {"type": "string"}
                    }
                },
                "follow_up": {
                    "type": "object",
                    "properties": {
                        "reminder_preference": {"type": "string", "enum": ["SMS", "email", "call"]},
                        "feedback_provided": {"type": "boolean"}
                    }
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "scheduling_timestamp": {"type": "string"},
                        "ai_assistant_version": {"type": "string"}
                    }
                }
            }
        }
    }

def get_response(messages: list[ChatCompletionMessageParam]) -> ChatCompletionMessage:
    try:
        chat_completion: ChatCompletion = client.chat.completions.create(
            messages=messages,
            model="gpt-4o-mini",
            tools=[{"type": "function", "function": get_appointment_json()}],
            tool_choice="auto"
        )
        return chat_completion.choices[0].message
    except Exception as e:
        return ChatCompletionMessage(role="assistant", content=f"Error: {str(e)}")

def print_conversation_history(conversation):
    for message in conversation[1:]:  # Skip the system message
        if message['role'] == 'user':
            print(f"{Fore.CYAN}User: {message['content']}")
        else:
            print(f"{Fore.GREEN}AI: {message['content']}\n")

def main():
    conversation: list[ChatCompletionMessageParam] = [{"role": "system", "content": system_prompt}]
    
    print(f"{Fore.YELLOW}Welcome to your AI assistant powered by GPT-4!")
    print(f"{Fore.YELLOW}Type 'exit' or 'quit' to end the conversation.")
    print(f"{Fore.YELLOW}Type 'history' to view the conversation history.")
    print(f"{Fore.YELLOW}Type 'clear' to clear the conversation history.")
    print(f"{Fore.YELLOW}Include '/JSON' in your message to get the appointment JSON.\n")
    
    while True:
        user_input = input(f"{Fore.CYAN}You: ")
        
        if user_input.lower() in ["exit", "quit"]:
            break
        elif user_input.lower() == "history":
            print_conversation_history(conversation)
            continue
        elif user_input.lower() == "clear":
            conversation = [{"role": "system", "content": system_prompt}]
            print(f"{Fore.YELLOW}Conversation history cleared.")
            continue
        
        json_requested = "/json" in user_input.lower()
        user_message = user_input ## r_input.replace("/json", "").strip()
        
        if user_message:
            conversation.append({"role": "user", "content": user_message})
        
        ai_response = get_response(conversation)
        
        if json_requested and ai_response.tool_calls:
            for tool_call in ai_response.tool_calls:
                if isinstance(tool_call, ChatCompletionMessageToolCall) and tool_call.function.name == "get_appointment_json":
                    json_output = json.loads(tool_call.function.arguments)
                    print(f"{Fore.GREEN}AI: Here's the appointment JSON:")
                    print(json.dumps(json_output, indent=2))
            
            # Remove the last user message if it only contained /JSON
            if not user_message:
                conversation.pop()
            
            # Continue the conversation without storing the JSON interaction
            continue_message = "Please continue our conversation."
            conversation.append({"role": "user", "content": continue_message})
            ai_response = get_response(conversation)
        
        print(f"{Fore.GREEN}AI: {ai_response.content}\n")
        conversation.append({"role": "assistant", "content": ai_response.content or ""})
    
    # Save the conversation to a JSON file
    if len(conversation) > 1:
        with open('conversation.json', 'w') as json_file:
            json.dump(conversation, json_file, indent=4)
        print(f"{Fore.YELLOW}Your conversation has been saved to 'conversation.json'.")
    
    print(f"{Fore.YELLOW}Thank you for using the AI assistant. Goodbye!")

if __name__ == "__main__":
    main()