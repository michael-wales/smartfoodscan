import openai
import requests
from bs4 import BeautifulSoup


#barcode = "3017620422003"


#function to get the response from the model
def get_gpt_response(barcode):
    # Set your OpenAI API key
    openai.api_key="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"
    #openai.api_key = st.secrets["api_key"]

    # Get the product information from the OpenFoodFacts API
    url = f"https://world.openfoodfacts.org/product/{barcode}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()

    # Prompt the model with the product information
    prompt = f"analyse this product and  give me some specific and the best insights regarding the healthiness of the product, return just 3 specific bullet points:\n\n{text[:4000]}"

    # Get the response from the model
    response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a nutrition expert reviewing a product."},
        {"role": "user", "content": prompt},
    ],
    max_tokens=250

    )
    return response.choices[0].message.content

#print(get_gpt_response(barcode))
