from google.cloud import vision
import pandas as pd
import io
import re
import cv2
import numpy as np
import streamlit as st

client = vision.ImageAnnotatorClient()
st.secrets['gcv_key']

def extract_text(image):
    # with io.open(image, 'rb') as image_file:
    #     content = image_file.read()

    content = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR).tobytes()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    return texts[0].description if texts else ""

features = ['energy-kcal_100g', 'saturated-fat_100g', 'trans-fat_100g', 'cholesterol_100g',
            'sugars_100g', 'fiber_100g', 'proteins_100g', 'sodium_100g', 'calcium_100g',
            'iron_100g', 'other_carbohydrates_100g', 'fat_100g', 'ingredients']

nutrition_dict = {feature: 0 for feature in features}

key_mapping = {
        'energy-kcal_100g': 'Calories',
        'saturated-fat_100g': 'Saturated Fat',
        'trans-fat_100g': 'Trans Fat',
        'cholesterol_100g': 'Cholesterol',
        'sugars_100g': 'Sugars',
        'fiber_100g': 'Dietary Fiber',
        'proteins_100g': 'Protein',
        'sodium_100g': 'Sodium',
        'calcium_100g': 'Calcium',
        'iron_100g': 'Iron',
        'other_carbohydrates_100g': 'Carbohydrate',
        'fat_100g': 'total Fat',
        'ingredients': 'ingredients'
}


def extract_values(nutrition_dict, nutrition_list, key_mapping):

    features = ['energy-kcal_100g', 'saturated-fat_100g', 'trans-fat_100g', 'cholesterol_100g',
            'sugars_100g', 'fiber_100g', 'proteins_100g', 'sodium_100g', 'calcium_100g',
            'iron_100g', 'other_carbohydrates_100g', 'fat_100g', 'ingredients']

    nutrition_dict = {feature: 0 for feature in features}

    key_mapping = {
        'energy-kcal_100g': 'Calories',
        'saturated-fat_100g': 'Saturated Fat',
        'trans-fat_100g': 'Trans Fat',
        'cholesterol_100g': 'Cholesterol',
        'sugars_100g': 'Sugars',
        'fiber_100g': 'Dietary Fiber',
        'proteins_100g': 'Protein',
        'sodium_100g': 'Sodium',
        'calcium_100g': 'Calcium',
        'iron_100g': 'Iron',
        'other_carbohydrates_100g': 'Carbohydrate',
        'fat_100g': 'total Fat',
        'ingredients': 'ingredients'
    }

    for key, search_term in key_mapping.items():
        for i, item in enumerate(nutrition_list):
            if search_term.lower() in item.lower():
                # If we find "Calories", we need to explicitly capture the next numeric value
                if search_term.lower() == 'calories':
                    if i + 1 < len(nutrition_list):
                        match = re.search(r'(\d+\.?\d*)', nutrition_list[i + 1])
                        if match:
                            value = match.group(1)
                            nutrition_dict[key] = float(value) if '.' in value else int(value)
                    break
                # Handle "Calcium" and "Iron" to capture next numeric values
                elif search_term.lower() == 'calcium' or search_term.lower() == 'iron':
                    if i + 1 < len(nutrition_list):
                        match = re.search(r'(\d+)%?', nutrition_list[i + 1])
                        if match:
                            value = match.group(1)
                            nutrition_dict[key] = float(value)/100 if '.' in value else int(value)/100
                    break

                elif search_term.lower() == 'ingredients':
                    match = re.search(r'ingredients[:\s]*([^$]+)', item, re.IGNORECASE)
                    if match:
                        ingredients_text = match.group(1).strip()  # Capture the text after "Ingredients:"
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
    keys_to_convert = ['cholesterol_100g', 'sodium_100g']

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
    text = extract_text(image)
    nutrition_list = text.split("\n")
    nutrition_list = [nutrient for nutrient in nutrition_list if nutrient]
    nutrition_dict = {feature: 0 for feature in features}
    nutrition_dict = extract_values(nutrition_dict, nutrition_list, key_mapping)
    nutrition_dict = convert_mg_to_g(nutrition_dict)
    serving_size = extract_serving_size(nutrition_list)
    nutrition_dict = convert_to_100g(nutrition_dict, serving_size)  # Convert to per 100g

    return nutrition_dict
