from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("setting completed")

#Multi_step Pipeline

def process_customer_feedback(feedback_text):
    #Summarize
    print("Processing customer feedback")
    print('='*40)

    summary_response = client.chat.completions.create(model='openai/gpt-oss-120b', messages=[
        {"role": "system", "content": "Summarize this customer feedback in 2 sentences:" + feedback_text}],
        temperature = 0.3)
    summary = summary_response.choices[0].message.content
    print("Summary:", summary)
    print()

    # Classify Sentiment
    print("Classifying sentiment")
    sentiment_response = client.chat.completions.create(model='openai/gpt-oss-120b', messages=[
        {"role": "system", "content": "Classify sentiment. Return JSON with sentiment field as positive, negative, or neutral."}],
        temperature = 0.1, 
        response_format = {"type": "json_object"}
        )
    sentiment_json = json.loads(sentiment_response.choices[0].message.content)
    print("Sentiment:", sentiment_json.get('sentiment'))
    print()


    # Extract Action Items
    print("Extracting action items")
    action_response = client.chat.completions.create(model='openai/gpt-oss-120b', messages=[
        {"role": "system", "content": "Extract action items. Return JSON with actions as a list of strings."},
        {"role": "user", "content": feedback_text}
        ],
        temperature = 0.1,
        response_format = {"type": "json_object"}
        )
    action_json = json.loads(action_response.choices[0].message.content)
    print("Action Items:", action_json.get('actions'))
    print()

    # Draft Response
    print("Drafting response")
    response_text = None
    if sentiment_json.get('sentiment') == 'negative':
        print("Drafting response for negative feedback")
        response_result= client.chat.completions.create(model='openai/gpt-oss-120b', messages=[
            {"role": "system", "content": "You are a customer service manager. Draft a professional, empathetic response."},
            {"role": "user", "content": "Customer feedback summary: " + summary}
            ],
            temperature = 0.5
            )
        response_text = response_result.choices[0].message.content
        print("Drafted Response:", response_text)
    else:
        print("No response needed for non-negative feedback")
    print()
    print("Pipeline Complete")
    return {
        "summary": summary,
        "sentiment": sentiment_json.get('sentiment'),
        "actions": action_json.get('actions'),
        "draft_response": response_text
    }

#Test Pipeline

feedback = """I have been using your product for 3 months. The interphase is confusing, customer support took 5 days to respond, and i was overcharged last month.
However, when it works, it's great. Please fix the billing issue ASAP."""

print()
print("Feedback Text:")
print(feedback)
print()

result = process_customer_feedback(feedback)
print()
print("Final Result:")
print(json.dumps(result, indent=2, default=str))


positive_feedback = "Aboslutely love the new features! The interface is intuitive, so much cleaner and the support team was very responsive. Keep up the great work!"
print()
print("=" *50)
print("Positive Feedback Text:")
print("="*50)
print()

result2 = process_customer_feedback(positive_feedback)

print()
print("Final Result for Positive Feedback:")
print(json.dumps(result2, indent=2, default=str))