from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

print("API client ready")

# --------------------------------------------------------
# MAKE AN API CALL
# --------------------------------------------------------

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello in exactly 3 words."}
    ],
    temperature=0.3,
    max_tokens=50
)

# --------------------------------------------------------
# INSPECT THE FULL RESPONSE
# --------------------------------------------------------

print("FULL RESPONSE OBJECT:")
print("  ID:", response.id)
print("  Model:", response.model)
print("  Created:", response.created)

message = response.choices[0].message
print()
print("MESSAGE:")
print("  Role:", message.role)
print("  Content:", message.content)

# --------------------------------------------------------
# TOKEN USAGE
# --------------------------------------------------------

usage = response.usage
print()
print("TOKEN USAGE:")
print("  Prompt tokens:", usage.prompt_tokens)
print("  Completion tokens:", usage.completion_tokens)
print("  Total tokens:", usage.total_tokens)

print()
print("COST: FREE (Groq free tier)")

# --------------------------------------------------------
# TEMPERATURE COMPARISON
# --------------------------------------------------------

prompt = "Write a 2-sentence product description for wireless headphones."

print()
print("TEMPERATURE COMPARISON")
print("=" * 50)

for temp in [0.0, 0.3, 0.7, 1.0]:
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=temp,
        max_tokens=100
    )
    
    print()
    print("Temperature:", temp)
    print("Response:", response.choices[0].message.content)