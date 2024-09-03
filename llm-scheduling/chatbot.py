import os
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall
import json
from colorama import Fore, Style, init
from datetime import datetime, timedelta
import textwrap
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

MODEL="gpt-4o-mini"

# Initialize colorama for colored output
init(autoreset=True)

# Initialize Rich console
console = Console()

# Load your OpenAI API key from an environment variable
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Load the system prompt from the file
with open('task/prompt.md', 'r') as file:
    system_prompt = file.read()

def get_appointment_json():
    """
    Generate a JSON object containing all relevant appointment information.
    """
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

def get_doctor_availabilities():
    """
    Get the available time slots for doctors by specialty.
    """
    return {
        "name": "get_doctor_availabilities",
        "description": "Get the available time slots for doctors by specialty",
        "parameters": {
            "type": "object",
            "properties": {
                "specialty": {"type": "string"},
                "date": {"type": "string"},
            },
            "required": ["specialty", "date"]
        }
    }

def get_doctor_specialties_string():
    doctors = {
        "General Practitioner": ["Dr. Smith", "Dr. Johnson"],
        "Cardiologist": ["Dr. Lee", "Dr. Garcia"],
        "Pediatrician": ["Dr. Patel", "Dr. Brown"],
        "Dermatologist": ["Dr. Wilson", "Dr. Taylor"],
        "Neurologist": ["Dr. Anderson", "Dr. Thomas"]
    }
    
    specialty_string = "Available Specialties and Doctors:\n"
    for specialty, doctor_list in doctors.items():
        specialty_string += f"\n{specialty}:\n"
        for doctor in doctor_list:
            specialty_string += f"  - {doctor}\n"
    return specialty_string

def mock_doctor_availabilities(specialty: str, date: str) -> dict:
    """
    Mock function to simulate doctor availabilities based on specialty and date.
    """
    doctors = {
        "General Practitioner": ["Dr. Smith", "Dr. Johnson"],
        "Cardiologist": ["Dr. Lee", "Dr. Garcia"],
        "Pediatrician": ["Dr. Patel", "Dr. Brown"],
        "Dermatologist": ["Dr. Wilson", "Dr. Taylor"],
        "Neurologist": ["Dr. Anderson", "Dr. Thomas"]
    }

    time_slots = ["9:00 AM", "10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM", "4:00 PM"]

    # Make the specialty matching more flexible
    matching_specialty = next((s for s in doctors.keys() if specialty.lower() in s.lower()), None)

    if matching_specialty:
        available_doctors = doctors[matching_specialty]
        available_slots = []
        for doctor in available_doctors:
            for slot in time_slots:
                available_slots.append(f"{doctor} - {slot}")
                if len(available_slots) >= 4:
                    break
            if len(available_slots) >= 4:
                break
        
        return {
            "specialty": matching_specialty,
            "date": date,
            "available_slots": [
                {"doctor": slot.split(" - ")[0], "time": slot.split(" - ")[1]}
                for slot in available_slots[:4]
            ]
        }
    else:
        return {
            "specialty": specialty,
            "date": date,
            "available_slots": []
        }

def get_response(messages: list[ChatCompletionMessageParam]) -> ChatCompletionMessage:
    """
    Get a response from the AI based on the conversation history.
    """
    try:
        tools: list[ChatCompletionToolParam] = [
            {
                "type": "function",
                "function": get_appointment_json()
            },
            {
                "type": "function",
                "function": get_doctor_availabilities()
            }
        ]
        chat_completion: ChatCompletion = client.chat.completions.create(
            messages=messages,
            model= MODEL,  # Updated to a valid model name
            tools=tools,
            tool_choice="auto"
        )
        return chat_completion.choices[0].message
    except Exception as e:
        return ChatCompletionMessage(role="assistant", content=f"Error: {str(e)}")

def print_conversation_history(conversation):
    """
    Print the conversation history to the console.
    """
    for message in conversation[1:]:  # Skip the system message
        if message['role'] == 'user':
            console.print(Panel(message['content'], title="User", border_style="cyan"))
        elif message['role'] == 'assistant':
            console.print(Panel(message['content'], title="AI", border_style="green"))
        elif message['role'] == 'function':
            console.print(Panel(message['content'], title="Function", border_style="yellow"))
    print()

def display_welcome_message():
    """
    Display a welcome message to the user.
    """
    welcome_text = """
    Welcome to your AI assistant powered by GPT-4!

    Commands:
    - Type 'exit' or 'quit' to end the conversation
    - Type 'history' to view the conversation history
    - Type 'clear' to clear the conversation history
    - Include '/JSON' in your message to get the appointment JSON

    Let's start chatting!
    """
    console.print(Panel(welcome_text, title="AI Assistant", border_style="yellow"))

def display_ai_response(response):
    """
    Display the AI's response in a formatted manner.
    """
    wrapped_response = textwrap.fill(response, width=100)
    console.print(Panel(wrapped_response, title="AI", border_style="green"))

def display_json(json_data):
    """
    Display JSON data in a formatted manner.
    """
    json_str = json.dumps(json_data, indent=2)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="JSON Output", border_style="magenta"))

def main():
    """
    Main function to run the chatbot application.
    """
    # Add the current date and time to the system prompt
    current_datetime = datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
    doctor_specialties = get_doctor_specialties_string()
    updated_system_prompt = f"{system_prompt}\n\nCurrent Date and Time: {current_datetime}\n\n{doctor_specialties}"

    conversation: list[ChatCompletionMessageParam] = [{"role": "system", "content": updated_system_prompt}]

    display_welcome_message()

    while True:
        user_input = input(f"{Fore.CYAN}You: ")

        if user_input.lower() in ["exit", "quit"]:
            break
        elif user_input.lower() == "history":
            print_conversation_history(conversation)
            continue
        elif user_input.lower() == "clear":
            conversation = [{"role": "system", "content": updated_system_prompt}]
            console.print("[yellow]Conversation history cleared.")
            continue

        json_requested = "/json" in user_input.lower()
        user_message = user_input

        if user_message:
            conversation.append({"role": "user", "content": user_message})

        ai_response = get_response(conversation)

        if ai_response.tool_calls:
            for tool_call in ai_response.tool_calls:
                if isinstance(tool_call, ChatCompletionMessageToolCall):
                    if tool_call.function.name == "get_appointment_json":
                        json_output = json.loads(tool_call.function.arguments)
                        console.print("[green]AI: Here's the appointment JSON:")
                        display_json(json_output)
                    elif tool_call.function.name == "get_doctor_availabilities":
                        args = json.loads(tool_call.function.arguments)
                        availabilities = mock_doctor_availabilities(args["specialty"], args["date"])
                        console.print("[green]AI: Here are the doctor's availabilities:")
                        display_json(availabilities)

                        # Format availability information for the AI
                        availability_info = (
                            f"For {availabilities['specialty']} on {availabilities['date']}, "
                            f"the following slots are available:\n"
                        )
                        for slot in availabilities['available_slots']:
                            availability_info += f"- {slot['doctor']} at {slot['time']}\n"

                        # Add availability info to the conversation
                        conversation.append({
                            "role": "function",
                            "name": "get_doctor_availabilities",
                            "content": json.dumps(availabilities)
                        })

                        # Ask AI to reformulate the availability information
                        reformulate_prompt = (
                            "Please reformulate the doctor availability information in plain English, "
                            "making it easy for the user to understand. Include all relevant details "
                            "such as the specialty, date, and available time slots with doctor names."
                        )
                        conversation.append({"role": "user", "content": reformulate_prompt})

                        # Get AI's reformulated response
                        ai_response = get_response(conversation)
                        display_ai_response(ai_response.content or "")
                        conversation.append({"role": "assistant", "content": ai_response.content or ""})

            # Continue the conversation
            continue_message = (
                "Please continue our conversation, taking into account "
                "the availability information provided."
            )
            conversation.append({"role": "user", "content": continue_message})
            ai_response = get_response(conversation)

        display_ai_response(ai_response.content or "")
        conversation.append({"role": "assistant", "content": ai_response.content or ""})

    # Save the conversation to a JSON file
    if len(conversation) > 1:
        filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as json_file:
            json.dump(conversation, json_file, indent=4)
        console.print(f"[yellow]Your conversation has been saved to '{filename}'.")

    console.print("[yellow]Thank you for using the AI assistant. Goodbye!")

if __name__ == "__main__":
    main()