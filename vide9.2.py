from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

print("API client ready")

# --------------------------------------------------------
# BAD PROMPT — Unreliable
# --------------------------------------------------------

bad_prompt = """
Summarize this support ticket and suggest a response.
"""

ticket = "My billing shows $499 but my plan is $299. This is the third time this year."

print("BAD PROMPT RESULT:")
print("=" * 40)

bad_result = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "user", "content": bad_prompt + ticket}
    ],
    temperature=0.7
)

print(bad_result.choices[0].message.content)

# --------------------------------------------------------
# GOOD PROMPT — Reliable, Structured, Automation-Ready
# --------------------------------------------------------

good_prompt = """
You are a Tier 2 customer support specialist at TechCorp, 
a B2B SaaS company. You handle escalated technical and billing issues.

TASK: Analyze the support ticket below and generate a structured response.

CONTEXT:
- Our SLA for critical issues is 4 hours
- We offer refunds only for outages exceeding 24 hours
- Escalation path: Tier 1 → Tier 2 → Engineering → CTO
- Billing errors should be flagged for the finance team

CONSTRAINTS:
- Be empathetic but professional
- If data loss is mentioned, flag as CRITICAL
- Never promise specific resolution times
- Include relevant knowledge base article IDs if applicable

OUTPUT FORMAT (strict JSON):
{
  "category": "billing/technical/account/feature_request/other",
  "priority": "low/medium/high/critical",
  "sentiment": "positive/neutral/negative/furious",
  "needs_engineering": true/false,
  "suggested_response": "draft email reply",
  "kb_articles": ["article_ids"],
  "auto_respond": true/false
}

EXAMPLE:
Input: "Your system deleted all my data. I have been a customer for 5 years."
Output: {
  "category": "technical",
  "priority": "critical",
  "sentiment": "furious",
  "needs_engineering": true,
  "suggested_response": "I understand how distressing data loss is. I have escalated this to our engineering team immediately.",
  "kb_articles": ["KB-401", "KB-502"],
  "auto_respond": false
}
"""

print()
print("GOOD PROMPT RESULT:")
print("=" * 40)

good_result = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "system", "content": good_prompt},
        {"role": "user", "content": ticket}
    ],
    temperature=0.2,
    response_format={"type": "json_object"}
)

parsed = json.loads(good_result.choices[0].message.content)
print(json.dumps(parsed, indent=2))

print()
print("STRUCTURE VERIFICATION:")
print("  Category:", parsed.get('category'))
print("  Priority:", parsed.get('priority'))
print("  Sentiment:", parsed.get('sentiment'))
print("  Auto respond:", parsed.get('auto_respond'))

# --------------------------------------------------------
# CONSISTENCY TEST
# --------------------------------------------------------

print()
print("CONSISTENCY TEST — Running good prompt 3 times")
print("=" * 40)

for i in range(3):
    result = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": good_prompt},
            {"role": "user", "content": ticket}
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    
    parsed = json.loads(result.choices[0].message.content)
    print()
    print("Run", i+1)
    print("  Category:", parsed.get('category'))
    print("  Priority:", parsed.get('priority'))
    print("  Sentiment:", parsed.get('sentiment'))