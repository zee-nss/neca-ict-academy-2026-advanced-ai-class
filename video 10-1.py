import PyPDF2
import pdfplumber
import json
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("setting completed")


# Level 1: Extract text from PDF
def extract_text_pypdf2(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n" 
    return text

def extract_text_pdfplumber(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Test it

print("Extracting text from PDF")
print('='*40)

pdf_path = 'sample_invoice.pdf'

text_pypdf2 = extract_text_pypdf2(pdf_path)
print('PyPDF2 extracted', len(text_pypdf2), 'characters')

text_pdfplumber = extract_text_pdfplumber(pdf_path)
print('pdfplumber extracted', len(text_pdfplumber), 'characters')

print()
print('Raw Text(first 500 characters):')
print('-'*40)
print(text_pdfplumber[:500])

# Level 2: AI Extraction

def extract_invoice_fields(document_text):
    response = client.chat.completions.create(model='openai/gpt-oss-120b', messages=[
        {"role": "system", "content": """Extract invoice field as JSON.
        Return Only valid JSON with this exact structure:{"invoice_number": "string or null",
        "invoice_date": "YYYY-MM-DD or null",
        "due_date": "YYYY-MM-DD or null",
        "vendor":{"name": "string", "address": "string"},
        "email": "string"},
        :bill_to":{"name": "string", "address": "string"},
        "line_items": [{"description": "string", "quantity": "number", "unit_price": "number", "total": "number"}],
        "subtotal": "number",
        "tax_rate": "number", "tax_amount": "number",
        "total": "number", "currency": "string", "payment_terms": "string",
        "confidence": "high/medium/low"
        }"""},
        {"role": "user", "content": "Extract from this invoice text: " + document_text[:4000]}
        ],
        response_format={"type":"json_object"}, temperature=0.1
        )
    return json.loads(response.choices[0].message.content)
print()
print("AI Extraction")
print('='*40)

result = extract_invoice_fields(text_pdfplumber)
print("extracted JSON:")
print(json.dumps(result, indent=2))

# Validate Extraction

print()
print("Validating Extraction")
print('='*40)

print("Invoice Number:", result.get("invoice_number"))
print("Invoice Date:", result.get("invoice_date"))
print("Due Date:", result.get("due_date"))
print("Vendor Name:", result.get("vendor", {}).get("name"))
print("Bill To:", result.get("bill_to", {}).get("name"))

print()

print("Line Items:")
for item in result.get("line_items", []):
    print("-", item.get("description"), 'x' + str(item.get('quantity')), "at $" + str(item.get('unit_price')),
           "$" + str(item.get('total')))
    print()
    print("subtotal: $" + str(result.get("subtotal")))
    print("Tax Rate: ",result.get("tax_rate"), "%")
    print("Total: $" + str(result.get("total")))
    print("Currency: ", result.get("currency"))
    print("Payment Terms: ", result.get("payment_terms"))
    print("Confidence: ", result.get("confidence"))