import openai
import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import json
import re


barcode = "4890008100309"


#function to get the response from the model
def get_gpt_response(barcode):
    # Set your OpenAI API key
    
    openai.api_key = st.secrets["api_key"]
    

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

def get_gpt_response2(barcode):
    # Set your OpenAI API key
    
    openai.api_key = st.secrets["api_key"]

    # Get the product information from the OpenFoodFacts API
    url = f"https://world.openfoodfacts.org/product/{barcode}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()

    # Prompt the model with the product information
    #prompt = f'analyse this product and specifically suggest me 2 healthier options of similar products that are in openfoodfacts.org and give me a quick summary of the healthiness of the product. go straight to the two products you are suggesting, dont mention anything else \n\n{text[:4000]}' 
    prompt = f'analyse this product and specifically suggest me 2 healthier options of similar products that are in openfoodfacts.org and give me just the barcodes as a list. convert it into a dictionary, dont give any additional information I just need the barcode number. ["3270190122371", "3068320115483"]\n\n{text[:4000]}' 
    #prompt = f"generate a dictionary with the barcode and the product name of the 3 products  that could be healthier options than the product analyzed. the format has to be:  'Product Name': product name, 'Barcode':Barcode . analyse this product and specifically suggest me 3 healthier options of similar products that are in openfoodfacts.org and generate a dictionary with the barcode and the product name of the 3 products: \n\n{text[:4000]}"
    

    response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a nutrition expert reviewing a product."},
        {"role": "user", "content": prompt},
    ],
    max_tokens=400
    

    )
    return response.choices[0].message.content
    '''try:
        product_dict = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        print("Error: wasn't able to convert the response into a dictionary.")
        return None

    return product_dict'''

def healthier_options(barcode):
    products_dict = get_gpt_response2(barcode)
    #products_dict = products_dict.replace("`", "'")
    #products_dict = products_dict.replace("'''python", "").strip()
    #products_dict = products_dict.replace("healthier_options =", "").strip()
    #products_dict = products_dict.replace("'''", "")
    #healthier_products = json.loads(products_dict)
    
    candidates = re.findall(r'"(.*?)"', products_dict)
    barcodes = [c for c in candidates if c.isdigit() and 12 <= len(c) <= 13]
    #barcodes = [product["barcode"] for product in healthier_products]
    barcode1 = barcodes[0]
    barcode2 = barcodes[1]
    return barcode1, barcode2






#print(get_gpt_response2(barcode))
print(healthier_options(barcode))

