from groq import Groq
import os
import json
import numpy as np
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

print("API client ready")

# --------------------------------------------------------
# STRUCTURED OUTPUT
# --------------------------------------------------------

def extract_with_json_mode(text):
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": """Extract the following from the text.
Return ONLY valid JSON with this exact structure:
{
  "order_id": "string or null",
  "customer_name": "string or null",
  "items": [{"name": "string", "quantity": "number", "price": "number"}],
  "total": "number or null",
  "status": "string or null",
  "confidence": "high/medium/low"
}"""
            },
            {"role": "user", "content": text}
        ],
        response_format={"type": "json_object"},
        temperature=0.1
    )
    
    return json.loads(response.choices[0].message.content)

text = "Order #ORD-98765 for Jane Smith: 2x Wireless Mouse ($29.99 each) and 1x Keyboard ($89.99). Total: $149.97. Status: Processing."

print("INPUT TEXT:")
print(text)
print()

result = extract_with_json_mode(text)

print("STRUCTURED RESULT:")
print(json.dumps(result, indent=2))

# --------------------------------------------------------
# FUNCTION CALLING
# --------------------------------------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "create_support_ticket",
            "description": "Create a support ticket in the system",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_email": {"type": "string"},
                    "category": {
                        "type": "string",
                        "enum": ["billing", "technical", "account", "general"]
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"]
                    },
                    "subject": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["customer_email", "category", "priority", "subject"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_customer",
            "description": "Look up customer by email",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"}
                },
                "required": ["email"]
            }
        }
    }
]

# --------------------------------------------------------
# ACTUAL FUNCTIONS
# --------------------------------------------------------

def create_support_ticket(customer_email, category, priority, subject, description=""):
    ticket_id = "TKT-" + str(np.random.randint(10000, 99999))
    return json.dumps({
        "ticket_id": ticket_id,
        "status": "created",
        "assigned_to": "Tier 1 Support",
        "estimated_response": "1 hour" if priority == "critical" else "4 hours"
    })

def lookup_customer(email):
    customers = {
        "john@email.com": {"name": "John Doe", "plan": "Pro", "tenure": "3 years"},
        "jane@email.com": {"name": "Jane Smith", "plan": "Enterprise", "tenure": "5 years"}
    }
    if email in customers:
        return json.dumps(customers[email])
    return json.dumps({"error": "Customer not found"})

available_functions = {
    "create_support_ticket": create_support_ticket,
    "lookup_customer": lookup_customer
}

# --------------------------------------------------------
# HANDLE TOOL CALLS
# --------------------------------------------------------

def handle_tool_calls(user_message):
    messages = [
        {"role": "system", "content": "You are a customer service AI. Use the available functions to help customers."},
        {"role": "user", "content": user_message}
    ]
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    msg = response.choices[0].message
    
    if msg.tool_calls:
        print("AI wants to call", len(msg.tool_calls), "function(s):")
        for tool_call in msg.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)
            print("  ->", func_name, "(" + json.dumps(func_args) + ")")
    else:
        print("AI response:", msg.content)
    
    return msg

print()
print("TEST 1: Customer with account issue")
handle_tool_calls("My account has been hacked. I'm john@email.com")

print()
print("TEST 2: Simple question")
handle_tool_calls("What is your return policy?")

# --------------------------------------------------------
# COMPLETE AGENT LOOP
# --------------------------------------------------------

def run_agent(user_message):
    messages = [
        {"role": "system", "content": "You are a helpful customer service AI. Use tools when needed."},
        {"role": "user", "content": user_message}
    ]
    
    max_iterations = 5
    
    for i in range(max_iterations):
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        msg = response.choices[0].message
        
        if msg.tool_calls:
            messages.append(msg)
            
            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                
                print("Step", i+1, ": Calling", func_name, "(" + json.dumps(func_args) + ")")
                
                result = available_functions[func_name](**func_args)
                print("  Result:", result)
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": result
                })
        else:
            print()
            print("Final response:", msg.content)
            return msg.content
    
    return "I'm sorry, I couldn't resolve your request."

print()
print("TESTING COMPLETE AGENT LOOP")
print("=" * 40)

run_agent("Hi, I'm john@email.com and I can't access my account. I think it's been hacked.")