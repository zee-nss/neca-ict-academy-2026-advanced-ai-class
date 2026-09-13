from groq import Groq
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
print("Setting complete")


# Defining the tools


def search_web(query=None, **kwargs):
    query = query or "general search"
    return json.dumps({
        "results": [
            {
                "title": "Result for '" + query + "'",
                "snippet": "This is a simulated search result. Replace with a real search API in production."
            }
        ]
    })

def calculate(expression=None, **kwargs):
    if not expression:
        return json.dumps({"error": "No expression provided"})
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return json.dumps({"expression": expression, "result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})

def get_current_datetime(**kwargs):
    now = datetime.now()
    return json.dumps({
        'iso': now.isoformat(),
        'date': now.strftime('%Y-%m-%d'),
        'time': now.strftime('%H:%M:%S'),
        'day': now.strftime('%A')
    })

def send_email(to=None, subject=None, body=None, **kwargs):
    return json.dumps({
        "status": "sent",
        "to": to or "unknown",
        "subject": subject or "no subject",
        "timestamp": datetime.now().isoformat()
    })

print("Tools defined")
print("1. Search Web")
print("2. Calculate")
print("3. Get Current DateTime")
print("4. Send Email")


# Tool Schema


agent_tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the internet for information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform a mathematical calculation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "The math expression to evaluate"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Get the current date and time.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email to a recipient.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body content"}
                },
                "required": ["to", "subject", "body"]
            }
        }
    }
]

available_tools = {
    'search_web': search_web,
    'calculate': calculate,
    'get_current_datetime': get_current_datetime,
    'send_email': send_email
}

print()
print("Tool schemas defined for the agent")


# Agent Execution


def agent_execute(user_request):
    messages = [
        {"role": "system", "content": "You are an AI Assistant with access to tools. Use them to help the user. Plan your approach before acting. Call tools as needed."},
        {"role": "user", "content": user_request}
    ]
    
    print()
    print("User Request:", user_request)
    print("=" * 40)
    
    for iteration in range(5):
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=agent_tools,
            tool_choice="auto"
        )
        
        msg = response.choices[0].message
        
        if msg.tool_calls:
            messages.append(msg)
            
            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                
                try:
                    func_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    func_args = {}
                
                print("Step", iteration + 1, ": Calling", func_name, "(" + json.dumps(func_args) + ")")
                
                try:
                    result = available_tools[func_name](**func_args)
                except TypeError as e:
                    print("  Type error. Retrying with no arguments.")
                    result = available_tools[func_name]()
                except Exception as e:
                    result = json.dumps({"error": str(e)})
                
                print("Result:", result)
                print()
                
                messages.append({
                    'role': 'tool',
                    'tool_call_id': tool_call.id,
                    'name': func_name,
                    'content': result
                })
        else:
            print("Final response:", msg.content)
            return msg.content
    
    return "Task could not be completed."


# Test Agent


print()
print("Test 1: Date and calculation")
print('=' * 40)

agent_execute("What day is today? Also calculate a 15% tip on an $85 meal.")

print()
print()
print("Test 2: Email task")
print('=' * 40)

agent_execute("Send an email to john@email.com with subject Meeting Reminder and body don't forget our meeting tomorrow at 2 PM.")

# Multi-step request
print()
print("Test 3: Multi-step request")
print('='*40)

agent_execute("Calculate the total cost of 3 items at $24.99 each, then send an email to accounting@email.com with the total.")