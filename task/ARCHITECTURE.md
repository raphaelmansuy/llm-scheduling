
## 1. Sequence Diagram

This diagram shows the interaction between the user, the main program, OpenAI API, and the mock doctor availability function.

```mermaid
sequenceDiagram
    participant User
    participant Main Program
    participant OpenAI API
    participant Mock Doctor Availability

    User->>Main Program: Start conversation
    Main Program->>User: Display welcome message
    loop Conversation
        User->>Main Program: Input message
        Main Program->>OpenAI API: Send conversation history
        OpenAI API->>Main Program: Return AI response
        alt Doctor availability requested
            Main Program->>Mock Doctor Availability: Get availabilities
            Mock Doctor Availability->>Main Program: Return mock data
        end
        Main Program->>User: Display AI response
    end
    User->>Main Program: Exit conversation
    Main Program->>User: Save conversation to JSON
```

## 2. Flowchart

This flowchart illustrates the main program's logic and decision-making process.

```mermaid
graph TD
    A[Start] --> B[Load system prompt]
    B --> C[Display welcome message]
    C --> D{User input}
    D -->|Exit/Quit| E[Save conversation]
    E --> F[End]
    D -->|History| G[Display conversation history]
    G --> D
    D -->|Clear| H[Clear conversation history]
    H --> D
    D -->|Other input| I[Process user input]
    I --> J[Send to OpenAI API]
    J --> K{Tool call?}
    K -->|Yes| L[Execute tool function]
    L --> M[Display result]
    M --> D
    K -->|No| N[Display AI response]
    N --> D
```

## 3. Class Diagram

This class diagram shows the main components and their relationships in the system.

```mermaid
classDiagram
    class Main {
        -conversation: list
        -client: OpenAI
        +main()
        -display_welcome_message()
        -print_conversation_history()
        -display_ai_response()
        -display_json()
    }
    class OpenAI {
        +chat.completions.create()
    }
    class ChatCompletionMessage {
        +role: string
        +content: string
        +tool_calls: list
    }
    class ToolFunction {
        +get_appointment_json()
        +get_doctor_availabilities()
    }
    class MockDoctorAvailability {
        +mock_doctor_availabilities()
    }

    Main --> OpenAI : uses
    Main --> ChatCompletionMessage : processes
    Main --> ToolFunction : calls
    Main --> MockDoctorAvailability : uses
    OpenAI --> ChatCompletionMessage : returns
    ChatCompletionMessage --> ToolFunction : triggers
```

## 3. State Diagram
```mermaid
stateDiagram-v2
    [*] --> Initializing
    state Initializing {
        [*] --> LoadingPrompt
        LoadingPrompt --> LoadingSpecialties
        LoadingSpecialties --> [*]
    }
    Initializing --> WaitingForUserInput: Display Welcome Message
    
    state WaitingForUserInput {
        [*] --> ReadingInput
        ReadingInput --> ProcessingCommand
        ProcessingCommand --> [*]: Not a command
        ProcessingCommand --> DisplayingHistory: 'history'
        ProcessingCommand --> ClearingHistory: 'clear'
        ProcessingCommand --> ExitingProgram: 'exit' or 'quit'
    }
    
    WaitingForUserInput --> ProcessingInput: User Enters Input
    
    state ProcessingInput {
        [*] --> PreparingAPIRequest
        PreparingAPIRequest --> SendingToOpenAI
        SendingToOpenAI --> ReceivingAPIResponse
        ReceivingAPIResponse --> [*]
    }
    
    ProcessingInput --> AnalyzingResponse
    
    state AnalyzingResponse {
        [*] --> CheckingToolCalls
        CheckingToolCalls --> ExecutingToolFunction: Tool Call Required
        CheckingToolCalls --> PreparingDisplayResponse: No Tool Call
        
        state ExecutingToolFunction {
            [*] --> GetAppointmentJSON
            [*] --> GetDoctorAvailabilities
            GetAppointmentJSON --> DisplayingJSON
            GetDoctorAvailabilities --> MockingAvailabilities
            MockingAvailabilities --> DisplayingJSON
            DisplayingJSON --> InjectingFunctionResponse
            InjectingFunctionResponse --> [*]
        }
        
        ExecutingToolFunction --> PreparingDisplayResponse
        PreparingDisplayResponse --> [*]
    }
    
    AnalyzingResponse --> DisplayingResponse
    DisplayingResponse --> WaitingForUserInput: Display AI Response
    
    state ExitingProgram {
        [*] --> SavingConversation
        SavingConversation --> DisplayingGoodbye
        DisplayingGoodbye --> [*]
    }
    
    ExitingProgram --> [*]: End Program

    note right of Initializing
        Load system prompt, current date/time,
        and doctor specialties
    end note

    note right of WaitingForUserInput
        Handle user input and special commands
    end note

    note right of ProcessingInput
        Prepare and send request to OpenAI API
    end note

    note right of AnalyzingResponse
        Handle tool calls and prepare response
    end note

    note right of ExecutingToolFunction
        Handle appointment JSON and 
        doctor availability requests
    end note

    note right of ExitingProgram
        Save conversation and exit
    end note
```


