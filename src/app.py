import streamlit as st
from barcode_decoder.barcode_reader import barcode_reader
from product_info.api_fetcher import get_product_info
import pandas as pd
import joblib
<<<<<<< HEAD
from PIL import Image
=======
import time

# A little CSS code to make streamlit less ugly
hide_header_footer = """
                <style>
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """
st.markdown(hide_header_footer, unsafe_allow_html=True)
>>>>>>> origin

# Load the machine learning model with caching
@st.cache_data
def load_model():
    return joblib.load('models/vanilla_random_forest.pkl') # Change best_model as needed

model = load_model()

<<<<<<< HEAD
# App title
#st.title("SmartFoodScan 🛒")
logo = Image.open('images/logo1.png')
st.image(logo, caption='', use_container_width=True)

#header
#st.header("Discover an easier way to make healthier food choices with SmartFoodScan.")
# Center the text using markdown and HTML
st.markdown("<h2 style='text-align: center;'>Discover an easier way to make healthier food choices with SmartFoodScan.</h2>", unsafe_allow_html=True)

=======
# App title and sidebar
st.title("SmartFoodScan 🛒")
st.sidebar.title("Options")
st.sidebar.write("Customize your experience:")
>>>>>>> origin


# User Input
image = st.camera_input("Take a picture of the product barcode 📷")
if not image:
    image = st.file_uploader("Or upload a barcode image from your device 📁", type=["png", "jpg", "jpeg"])


# Barcode reader and product info fetching
if image:
    with st.spinner("Scanning barcode..."):
        barcode = barcode_reader(image)

    if barcode:
        st.success(f"Product barcode: {barcode}")
        with st.spinner("Fetching product info..."):
            product_info = get_product_info(barcode)

        if isinstance(product_info, dict):
            # Display basic product info
            st.subheader("Product Information")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Name:** {product_info.get('product_name', 'Unknown').title()}")
                st.write(f"**Brand:** {product_info.get('brands', 'Unknown').split(',')[0].title()}")
            with col2:
                if "image_url" in product_info:
                    st.image(product_info["image_url"], caption="Product Image", width=150)

            # Display ingredients
            st.subheader("Ingredients")
            ingredients = product_info.get('ingredients_text', 'No ingredients listed.')
            st.write(ingredients.title())

            # Check for allergens
            st.subheader("⚠️ Allergens")
            allergens = product_info.get("allergens_tags", [])
            common_allergens = ['milk', 'peanuts', 'fish', 'soybeans', 'gluten', 'molluscs', 'nuts', 'eggs', 'sesame-seeds']
            if allergens:
                allergens = allergens[0]
                unsuitable = [a for a in common_allergens if a in allergens]
                suitable = [a for a in common_allergens if a not in allergens]
                if suitable:
                    st.success(f"✅ Suitable for: {', '.join(suitable)}")
                if unsuitable:
                    st.error(f"🚫 Not suitable for: {', '.join(unsuitable)}")
            else:
                st.success(f"✅ Suitable for: {', '.join(common_allergens)}")

            # Nutritional information visualization
            st.subheader("Nutritional Information")
            if "nutriments" in product_info:
                nutriments = product_info["nutriments"]
                nutrients = {
                    "Energy (kcal)": nutriments.get('energy-kcal_100g', 0),
                    "Saturated Fat (g)": nutriments.get('saturated-fat_100g', 0),
                    "Sugars (g)": nutriments.get('sugars_100g', 0),
                    "Protein (g)": nutriments.get('proteins_100g', 0),
                    "Fiber (g)": nutriments.get('fiber_100g', 0),
                    "Sodium (mg)": nutriments.get('sodium_100g', 0),
                }
                st.bar_chart(nutrients)

            # Healthiness score prediction
            st.subheader("🏥 Healthiness Score")
            data = {
                'energy-kcal_100g': [nutriments.get('energy-kcal_100g', 0)],
                'saturated-fat_100g': [nutriments.get('saturated-fat_100g', 0)],
                'trans-fat_100g': [nutriments.get('trans-fat_100g', 0)],
                'cholesterol_100g': [nutriments.get('cholesterol_100g', 0)],
                'sugars_100g': [nutriments.get('sugars_100g', 0)],
                'fiber_100g': [nutriments.get('fiber_100g', 0)],
                'proteins_100g': [nutriments.get('proteins_100g', 0)],
                'sodium_100g': [nutriments.get('sodium_100g', 0)],
                'calcium_100g': [nutriments.get('calcium_100g', 0)],
                'iron_100g': [nutriments.get('iron_100g', 0)],
                'other_carbohydrates_100g': [nutriments.get('carbohydrates_100g', 0) - nutriments.get('sugars_100g', 0) - nutriments.get('fiber_100g', 0)],
                'other_fat_100g': [nutriments.get('fat_100g', 0) - nutriments.get('saturated-fat_100g', 0) - nutriments.get('trans-fat_100g', 0)],
            }
            input_data = pd.DataFrame.from_dict(data)
            prediction = model.predict(input_data)

            # Display healthiness score with a progress bar
            score_value = max(0, min(prediction[0], 100))
            score_value = 100 - score_value  # Invert the score
            st.progress(score_value / 100)
            if score_value < 33.33:
                st.error(f"Healthiness Score: {score_value:.0f}/100 - Unhealthy 🚫")
            elif score_value < 60:
                st.warning(f"Healthiness Score: {score_value:.0f}/100 - Low Healthiness ⚠️")
            elif score_value < 80:
                st.info(f"Healthiness Score: {score_value:.0f}/100 - Moderately Healthy ✅")
            elif score_value < 93.33:
                st.success(f"Healthiness Score: {score_value:.0f}/100 - Healthy 🌿")
            else:
                st.success(f"Healthiness Score: {score_value:.0f}/100 - Highly Healthy 🌟")
            # This whole thing needs to be reworked. The machine learning model really doesn't tell us anything. We can just use the API and describe the ingredients and their effect since the 'y' is just a linear combination of them.
        else:
            st.error("Failed to fetch product information. Please try again.")
    else:
        st.error("Could not detect a barcode. Try another image.")
