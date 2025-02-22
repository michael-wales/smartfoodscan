import streamlit as st
from barcode_decoder.barcode_reader import barcode_reader
from product_info.api_fetcher import get_product_info
import pandas as pd
import joblib



model = joblib.load('models/vanilla_random_forest.pkl')

# App title
st.title("SmartFoodScan 🛒")

# User Input
# 📷 Priority: camara
image = st.camera_input("Take a picture of the product barcode 📷")

# 🖼️ Secondary option: upload picture from device
if not image:
    image = st.file_uploader("Or upload a barcode image from your device 📁", type=["png", "jpg", "jpeg"])

# Barcode reader
if image:
    barcode = barcode_reader(image)

    if barcode:
        st.success(f"Product barcode: {barcode}")
        #Fetch product info from Open Food Facts API
        product_info = get_product_info(barcode)

        if isinstance(product_info, dict):
            # Display basic product info
            name = product_info.get('product_name', 'Unknown')
            brand = product_info.get('brands', 'Unknown').split(',')[0]
            ingredients = product_info.get('ingredients_text', 'Unknown')
            st.subheader("Product Name")
            st.write(f"{name.title()}")
            st.subheader("Product Brand")
            st.write(f"{brand.title()}")
            st.subheader("Product Ingredients")
            st.write(f"{ingredients.title()}")

            # Display image if available
            if "image_url" in product_info:
                st.subheader("Product Image")
                st.image(product_info.get("image_url", None), caption="")

            # Check for allergens and siplay results
            st.subheader("Allergens")
            allergens = product_info.get("allergens_tags", None)
            common_allergens = ['milk','peanuts','fish','soybeans','gluten','molluscs','nuts','eggs','sesame-seeds']
            if allergens:
                allergens = allergens[0]
                unsuitable = [a for a in common_allergens if a in allergens]
                suitable = [a for a in common_allergens if a not in allergens]
                if suitable:
                    st.success(f"✅ Suitable for: {', '.join(suitable)}")
                if unsuitable:
                    st.error(f"⚠️ Not suitable for: {', '.join(unsuitable)}")
            else:
                st.success(f"✅ Suitable for: {', '.join(common_allergens)}")

            # Model implementation to be abstracted into code
            #########

            data = {'energy-kcal_100g': [product_info['nutriments'].get('energy-kcal_100g', 0)],
                    'saturated-fat_100g': [product_info['nutriments'].get('saturated-fat_100g', 0)],
                    'trans-fat_100g':  [product_info['nutriments'].get('trans-fat_100g', 0)],
                    'cholesterol_100g': [product_info['nutriments'].get('cholesterol_100g', 0)],
                    'sugars_100g': [product_info['nutriments'].get('sugars_100g', 0)],
                    'fiber_100g': [product_info['nutriments'].get('fiber_100g', 0)],
                    'proteins_100g': [product_info['nutriments'].get('proteins_100g', 0)],
                    'sodium_100g': [product_info['nutriments'].get('sodium_100g', 0)],
                    'calcium_100g': [product_info['nutriments'].get('calcium_100g', 0)],
                    'iron_100g': [product_info['nutriments'].get('iron_100g', 0)],
                    'other_carbohydrates_100g': [product_info['nutriments'].get('carbohydrates_100g', 0) - product_info['nutriments'].get('sugars_100g', 0) - product_info['nutriments'].get('fiber_100g', 0)],
                    'other_fat_100g': [product_info['nutriments'].get('fat_100g', 0) - product_info['nutriments'].get('saturated-fat_100g', 0) - product_info['nutriments'].get('trans-fat_100g', 0)]}

            input_data = pd.DataFrame.from_dict(data)

            prediction = model.predict(input_data)

            # We need to choose a scale. How about[:
            def score(value):

                # Clamp value between 0 and 100
                value = max(0, min(int(value), 100))

                # Invert the score (higher input = lower score)
                value = 100 - value

                if value < 20:
                    category = "Not healthy!"
                elif value < 40:
                    category = "Not very healthy!"
                elif value < 60:
                    category = "OK"
                elif value < 80:
                    category = "Healthy"
                else:
                    category = "Very healthy!"

                return f"Healthiness score: {value}/100 - {category}"

            st.write(score(prediction[0]))
            #########

        else:
            st.error(product_info)
    else:
        st.error("Could not detect a barcode. Try another image.")
