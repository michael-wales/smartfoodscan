from google.cloud import vision
import pandas as pd
import io
import re
import cv2
import numpy as np
import streamlit as st
import base64
import requests
import json


# client = vision.ImageAnnotatorClient(api_key=st.secrets['gcv_key'])

# def extract_text(image):
#     # with io.open(image, 'rb') as image_file:
#     #     content = image_file.read()

#     content = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR).tobytes()

#     image = vision.Image(content=content)
#     response = client.text_detection(image=image)
#     texts = response.text_annotations

#     return texts[0].description if texts else ""

# def extract_text(image):
#     API_KEY = st.secrets['gcv_key']
#     url = f'https://vision.googleapis.com/v1/images:annotate?key={API_KEY}'

# # Prepare the image you want to analyze (base64 encoded)
#     def encode_image(image_path):
#         with open(image_path, 'rb') as image_file:
#             return base64.b64encode(image_file.read()).decode('UTF-8')

# # # Example image path (replace with the path to your image)
# # image_path = '../images/nutrition_facts3.jpg'
# # image_path = '../images/yerba-mate2.png'

# # Base64 encode the image
#     encoded_image = encode_image(image)
#     content = cv2.imdecode(np.frombuffer(encode_image.read(), np.uint8), cv2.IMREAD_COLOR).tobytes()

# # Construct the request payload
#     payload = {
#         "requests": [
#             {
#                 "image": {
#                     "content": encoded_image
#                 },
#                 "features": [
#                     {
#                         "type": "TEXT_DETECTION",  # Change to another feature if needed (e.g., TEXT_DETECTION)
#                         "maxResults": 10
#                     }
#                 ]
#             }
#         ]
#     }

#     # Send the POST request
#     response = requests.post(url, json=payload)

# # Check the response
#     if response.status_code == 200:
#         print('Response:', response.json())  # Print the JSON response from the API
#     else:
#         print(f"Request failed with status code: {response.status_code}")
#         print(f"Error: {response.text}")

#     return response.json()["responses"][0]["textAnnotations"][0]["description"]


def analyze_image_with_vision_api(image_path, api_key, feature_type="TEXT_DETECTION", max_results=10):
    """
    Analyzes an image using Google Vision API.

    Args:
        image_path (str): Path to the image file.
        api_key (str): API key for accessing the Google Vision API.
        feature_type (str): The type of feature for image analysis (default is TEXT_DETECTION).
        max_results (int): Maximum number of results to return (default is 10).

    Returns:
        dict: The response from the Google Vision API, or None if the request fails.
        str: Extracted text from the image, or None if no text found.
    """
    # Helper function to encode the image to base64
    def encode_image(image_path):
        # with open(image_path, 'rb') as image_file:
        #     return base64.b64encode(image_file.read()).decode('UTF-8')
        image_content = image_path.read()
        return base64.b64encode(image_content).decode('UTF-8')

    # with io.open(image_path, 'rb') as image_file:
    #     content = image_file.read()

    # content = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR).tobytes()

    # Google Vision API endpoint
    url = f'https://vision.googleapis.com/v1/images:annotate?key={api_key}'

    # Base64 encode the image
    encoded_image = encode_image(image_path)

    # Construct the request payload
    payload = {
        "requests": [
            {
                "image": {
                    "content": encoded_image
                },
                "features": [
                    {
                        "type": feature_type,
                        "maxResults": max_results
                    }
                ]
            }
        ]
    }

    # Send the POST request
    response = requests.post(url, json=payload)

    # Check the response
    if response.status_code == 200:
        response_data = response.json()  # Get the JSON response

        # Extract the text from the response if available
        if "responses" in response_data and response_data["responses"]:
            text = response_data["responses"][0].get("textAnnotations", [])
            if text:
                # print('Response:', response_data)  # Print the JSON response from the API
                # print('Text:', text[0]["description"])  # Print the extracted text
                return response_data, text[0]["description"]  # Return both full response and extracted text
            else:
                return response_data, None  # No text annotations found
        else:
            return response_data, None  # No responses found in the API result
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(f"Error: {response.text}")
        return None, None


# Example usage
# API_KEY = st.secrets['gcv_key']
# image_path = '../images/yerba-mate2.png'

# response_data, extracted_text = analyze_image_with_vision_api(image_path, API_KEY)

# if response_data:
#     print("API Response:", json.dumps(response_data, indent=2))
#     if extracted_text:
#         print("\nExtracted Text:", extracted_text)
#     else:
#         print("\nNo text found in the image.")



features = ['energy-kcal_100g', 'saturated-fat_100g', 'trans-fat_100g', 'cholesterol_100g',
            'sugars_100g', 'fiber_100g', 'proteins_100g', 'sodium_100g', 'calcium_100g',
            'iron_100g', 'other_carbohydrates_100g', 'fat_100g', 'ingredients']

nutrition_dict = {feature: 0 for feature in features}

key_mapping = {
    'energy-kcal_100g': 'Calories',
    'saturated-fat_100g': 'Saturated',
    'trans-fat_100g': 'Trans',
    'cholesterol_100g': 'Cholesterol',
    'sugars_100g': 'Sugars',
    'fiber_100g': 'Fibre',
    'proteins_100g': 'Protein',
    'sodium_100g': 'Sodium',
    'calcium_100g': 'Calcium',
    'iron_100g': 'Iron',
    'other_carbohydrates_100g': 'Carbohydrate',
    'fat_100g': 'Fat',
    'ingredients': 'ingredients'
}

def extract_values(nutrition_dict, nutrition_list, key_mapping):

    features = ['energy-kcal_100g', 'saturated-fat_100g', 'trans-fat_100g', 'cholesterol_100g',
                'sugars_100g', 'fiber_100g', 'proteins_100g', 'sodium_100g', 'calcium_100g',
                'iron_100g', 'other_carbohydrates_100g', 'fat_100g', 'ingredients']

    nutrition_dict = {feature: 0 for feature in features}

    key_mapping = {
        'energy-kcal_100g': 'Calories',
        'saturated-fat_100g': 'Saturated',
        'trans-fat_100g': 'Trans',
        'cholesterol_100g': 'Cholesterol',
        'sugars_100g': 'Sugars',
        'fiber_100g': 'Fibre',
        'proteins_100g': 'Protein',
        'sodium_100g': 'Sodium',
        'calcium_100g': 'Calcium',
        'iron_100g': 'Iron',
        'other_carbohydrates_100g': 'Carbohydrate',
        'fat_100g': 'Fat',
        'ingredients': 'ingredients'
    }

    for key, search_term in key_mapping.items():
        for i, item in enumerate(nutrition_list):
            if search_term.lower() in item.lower():
                # If we find "Calories", we need to explicitly capture the next numeric value
                # if search_term.lower() == 'calories':
                #     if i + 1 < len(nutrition_list):
                #         match = re.search(r'(\d+\.?\d*)', nutrition_list[i + 1])
                #         if match:
                #             value = match.group(1)
                #             nutrition_dict[key] = float(value) if '.' in value else int(value)
                #     break
                # # Handle "Calcium" and "Iron" to capture next numeric values
                # elif search_term.lower() == 'calcium' or search_term.lower() == 'iron':
                #     if i + 1 < len(nutrition_list):
                #         match = re.search(r'(\d+)%?', nutrition_list[i + 1])
                #         if match:
                #             value = match.group(1)
                #             nutrition_dict[key] = float(value)/100 if '.' in value else int(value)/100
                #     break

                if search_term.lower() == 'ingredients':
                    match = re.search(r'ingredients[:\s]*([^$]+)', item, re.IGNORECASE)
                    if match:
                        ingredients_text = match.group(1).strip()
                        nutrition_dict[key] = ingredients_text
                    break

                else:
                    # For other terms, we just capture the numeric value
                    match = re.search(r'(\d+\.?\d*)\s?(g|mg|%)?', item)
                    if match:
                        value = match.group(1)
                        if value:
                            nutrition_dict[key] = float(value) if '.' in value else int(value)
                    break

    return nutrition_dict


def convert_mg_to_g(nutrition_dict):
    # Conversion factor: 1 mg = 0.001 g
    conversion_factor = 0.001
    keys_to_convert = ['cholesterol_100g', 'sodium_100g', 'calcium_100g', 'iron_100g']

    for key in keys_to_convert:
        if key in nutrition_dict:
            nutrition_dict[key] = nutrition_dict[key] * conversion_factor

    return nutrition_dict

def extract_serving_size(nutrition_list):
    for item in nutrition_list:
        match = re.search(r'\((\d+)', item)
        if match:
            return int(match.group(1))
    return None

def convert_to_100g(nutrition_dict, serving_size):
    nutrition_100g = {}
    for key, value in nutrition_dict.items():
        if isinstance(value, str):
            nutrition_100g[key] = value
        elif value != 0:
            nutrition_100g[key] = (value * 100) / serving_size
        else:
            nutrition_100g[key] = 0

    return nutrition_100g


def extract_nutritional_info(image):
    API_KEY = st.secrets['gcv_key']

    response_data, extracted_text = analyze_image_with_vision_api(image, API_KEY)
    # print(response_data, extracted_text)

    # if response_data:
    #     print("API Response:", json.dumps(response_data, indent=2))
    #     if extracted_text:
    #         print("\nExtracted Text:", extracted_text)
    #     else:
    #         print("\nNo text found in the image.")

    nutrition_list = extracted_text.split("\n")
    nutrition_list = [nutrient for nutrient in nutrition_list if nutrient]
    nutrition_dict = {feature: 0 for feature in features}
    nutrition_dict = extract_values(nutrition_dict, nutrition_list, key_mapping)
    nutrition_dict = convert_mg_to_g(nutrition_dict)
    serving_size = extract_serving_size(nutrition_list)
    nutrition_dict = convert_to_100g(nutrition_dict, serving_size)
    # print(nutrition_dict)
    return nutrition_dict
