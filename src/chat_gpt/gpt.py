import openai 
import requests
import json
from bs4 import BeautifulSoup


barcode = "0815074022915"
url = f"https://world.openfoodfacts.org/product/{barcode}"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
text = soup.get_text()

# Set your OpenAI API key
openai.api_key='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'



#prompt to be sent to the model

prompt = f"analyse this product and  give me some specific and the best insights regarding the healthiness of the product, return just 3 specific bullet points:\n\n{text[:4000]}"

#function to get the response from the model
def get_gpt_response(prompt):
    response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a nutrition expert reviewing a product."},
        {"role": "user", "content": prompt},
    ],
    max_tokens=200
    )
    return response.choices[0].message.content

print(get_gpt_response(prompt))
