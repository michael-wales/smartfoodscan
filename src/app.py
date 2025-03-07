import streamlit as st
from barcode_decoder.barcode_reader import barcode_reader
from product_info.api_fetcher import get_product_info
from dietary_analysis.allergens import identify_allergens
from dietary_analysis.labels import check_labels
from nutrition_reader import extract_nutritional_info
import pandas as pd
import joblib
from chat_gpt.gpt import get_gpt_response
from PIL import Image
import requests
import plotly.graph_objects as go




st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600&display=swap');
        #MainMenu, header, footer {visibility: hidden; height: 0%;}
        html {filter: none;}
        .stRadio {display: flex; justify-content: center; margin-bottom: -100px;}
    </style>
    """,
    unsafe_allow_html=True)

#App logo and catch sentence
logo = Image.open('images/logo1.png')
st.image(logo, use_container_width=True)
st.markdown("<h2 style='text-align: center; margin-top: -50px; color: #37474F;'>Discover an easier way to make healthier food choices</h2>", unsafe_allow_html=True)

# User input (removed after product identified)
input_placeholder = st.empty()
with input_placeholder.container():
    st.markdown("<h3 style='text-align: center; color: #455A64;'>How would you like to search for a product?</h3>", unsafe_allow_html=True)
    option = st.radio("", ["📸 Take a picture of barcode", "📁 Upload barcode image from device"], horizontal=True,key="search_option")

    if option == "📸 Take a picture of barcode":
        st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
        camera_image = st.camera_input("")
        st.markdown('</div>', unsafe_allow_html=True)
        image = camera_image

    elif option == "📁 Upload barcode image from device":
        st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
        image = st.file_uploader("", type=["png", "jpg", "jpeg"])
        st.markdown('</div>', unsafe_allow_html=True)

# Barcode reader and product info fetching
if image:
    with st.spinner("🔍 Scanning barcode..."):
        barcode = barcode_reader(image)

    if barcode:
        input_placeholder.empty()
        with st.spinner("📡 Fetching product info..."):
            product_info = get_product_info(barcode)

        if isinstance(product_info, dict):
            st.success("✅ Product Found")
            labels = check_labels(product_info)
            suitable_allergens, unsuitable_allergens = identify_allergens(product_info)
            cols = st.columns(len(labels))
            for i, (label, label_value) in enumerate(labels.items()):
                if label_value is not None:
                    with cols[i]:
                        if label_value == 'yes':
                            st.image(f"images/{label}_yes.png", width=100)  # Adjust the width for larger images
                        elif label_value == 'no':
                            st.image(f"images/{label}_no.png", width=100)
                        elif label_value == 'maybe':
                            st.image(f"images/{label}_maybe.png", width=100)
            col1, col2= st.columns([1, 3])
            with col1:
                if "image_url" in product_info:
                    st.markdown(f'<img src="{product_info.get("image_url", "")}" height="350" style="display: block; margin-bottom: -10000px;"/>', unsafe_allow_html=True)
                else:
                    st.image(f"images/no-photo-available.jpg", width=200)
            with col2:
                st.markdown(f"""
                <div style="background-color: #f0f0f0; padding: 20px; border-radius: 10px; height: 350px;">
                    <h3 style="font-size: 18px; margin-bottom: -20px;"><span style="font-weight: bold;">Name:</span>{product_info.get('product_name', 'Unknown').title()}</h3>
                    <h4 style="font-size: 18px; margin-bottom: -20px;"><span style="font-weight: bold;">Barcode:</span> {barcode}</h4>
                    <h4 style="font-size: 18px; margin-bottom: -20px;"><span style="font-weight: bold;">Brand:</span> {product_info.get('brands', 'Unknown').split(',')[0].title()}</h4>
                    <h4 style="font-size: 18px; margin-bottom: -2px;"><span style="font-weight: bold;">Ingredients:</span> {product_info.get('ingredients_text', 'No ingredients listed.').title()}</h4>
                    <div style="margin-top: 10px;">
                        {f'<p style="font-weight: bold; color: grey;">✅ Suitable for allergies to: {", ".join(suitable_allergens)}</p>' if suitable_allergens else ''}
                        {f'<p style="font-weight: bold; color: grey;">🚫 Not suitable for allergies to: {", ".join(unsuitable_allergens)}</p>' if unsuitable_allergens else ''}
            </div>
                </div>
                """, unsafe_allow_html=True)

            # Healthiness score prediction
            if "nutriments" in product_info:
                nutriments = product_info["nutriments"]
                data = {
                    'energy-kcal_100g': nutriments.get('energy-kcal_100g', 0),
                    'saturated-fat_100g': nutriments.get('saturated-fat_100g', 0),
                    'trans-fat_100g': nutriments.get('trans-fat_100g', 0),
                    'cholesterol_100g': nutriments.get('cholesterol_100g', 0),
                    'sugars_100g': nutriments.get('sugars_100g', 0),
                    'fiber_100g': nutriments.get('fiber_100g', 0),
                    'proteins_100g': nutriments.get('proteins_100g', 0),
                    'sodium_100g': nutriments.get('sodium_100g', 0),
                    'calcium_100g': nutriments.get('calcium_100g', 0),
                    'iron_100g': nutriments.get('iron_100g', 0),
                    'other_carbohydrates_100g': nutriments.get('carbohydrates_100g', 0) - nutriments.get('sugars_100g', 0) - nutriments.get('fiber_100g', 0),
                    'other_fat_100g': nutriments.get('fat_100g', 0) - nutriments.get('saturated-fat_100g', 0) - nutriments.get('trans-fat_100g', 0)
                }
                url = "https://smartfoodscan-805490564375.europe-west1.run.app/predict"
                response = requests.post(url, json=data)
                prediction = response.json()['prediction']

            col1, col2= st.columns([1, 1])
            with col1:
                # Display healthiness score with a progress bar
                score_value = max(0, min(prediction[0], 100))
                score_value = 100 - score_value  # Invert the score

                # if score_value < 33.33:
                #     st.write(f"Healthiness Score: {score_value:.0f}/100 - Unhealthy 🚫")
                # elif score_value < 60:
                #     st.write(f"Healthiness Score: {score_value:.0f}/100 - Low Healthiness ⚠️")
                # elif score_value < 80:
                #     st.write(f"Healthiness Score: {score_value:.0f}/100 - Moderately Healthy ✅")
                # elif score_value < 93.33:
                #     st.write(f"Healthiness Score: {score_value:.0f}/100 - Healthy 🌿")
                # else:
                #     st.success(f"Healthiness Score: {score_value:.0f}/100 - Highly Healthy 🌟")

                value = int(score_value)
                bar_color = '#FF4B4B' if value <= 25 else '#FF6F6F' if value <= 50 else '#FFB74D' if value <= 75 else '#8C9A00'
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=value,
                    title={'text': "Healthiness Score",'font': {'size': 25}},
                    gauge={
                        'axis': {'visible': True, 'range': [0, 100],'tickwidth': 2, 'tickcolor': 'black'},
                        'bar': {'color': bar_color,'thickness': 1},
                        'steps': [],
                        'shape': 'angular',
                        'bordercolor': "black",
                        'borderwidth': 1,
                        'bgcolor': 'rgba(0,0,0,0)'}))
                st.markdown('<style>div.row-widget.stPlotlyChart {margin-top: -200px;}</style>', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)

            go_back = st.button("🔄 Scan Another Product")
            if go_back:
                st.session_state.product_info = None
                st.experimental_rerun()
            with col2:
                #Chat GPT details
                chatgpt_response = get_gpt_response(barcode)
                if chatgpt_response:
                    st.markdown("<h3 style='text-align: center;'>Here are some usefull insights about this product</h3>", unsafe_allow_html=True)
                    st.write(chatgpt_response)
        go_back = st.button("🔄 Scan Another Product")
        if go_back:
            st.session_state.product_info = None
            st.experimental_rerun()




        else:
            st.error("Failed to fetch product information. You can try with an image of the Nutritional Facts.")

            input_placeholder = st.empty()
            with input_placeholder.container():
                st.markdown("<h2 style='text-align: center; font-size: 30px; font-weight: bold; margin-top: 10px; margin-bottom: -70px;'>How would you like to search for a product?</p>", unsafe_allow_html=True)
                option = st.radio("", ["📸 Take a picture of nutritional facts", "📁 Upload nutritional facts image from device"], horizontal=True,key="search_option2")

                if option == "📸 Take a picture of nutritional facts":
                    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
                    camera_image = st.camera_input("")
                    st.markdown('</div>', unsafe_allow_html=True)
                    image = camera_image

                elif option == "📁 Upload nutritional facts image from device":
                    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
                    image = st.file_uploader("", type=["png", "jpg", "jpeg"], key= "nutritional-upload")
                    st.markdown('</div>', unsafe_allow_html=True)


            if image:
                input_placeholder.empty()
                with st.spinner("Fetching product info..."):
                    nutriments = extract_nutritional_info(image)

                    if isinstance(nutriments, dict):

                        # Nutritional information visualization
                        st.subheader("Nutritional Information")
                        if "nutriments" in nutriments:
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
                        st.subheader("⚕️ Healthiness Score")
                        data = {
                            'energy-kcal_100g': nutriments.get('energy-kcal_100g', 0),
                            'saturated-fat_100g': nutriments.get('saturated-fat_100g', 0),
                            'trans-fat_100g': nutriments.get('trans-fat_100g', 0),
                            'cholesterol_100g': nutriments.get('cholesterol_100g', 0),
                            'sugars_100g': nutriments.get('sugars_100g', 0),
                            'fiber_100g': nutriments.get('fiber_100g', 0),
                            'proteins_100g': nutriments.get('proteins_100g', 0),
                            'sodium_100g': nutriments.get('sodium_100g', 0),
                            'calcium_100g': nutriments.get('calcium_100g', 0),
                            'iron_100g': nutriments.get('iron_100g', 0),
                            'other_carbohydrates_100g': nutriments.get('carbohydrates_100g', 0) - nutriments.get('sugars_100g', 0) - nutriments.get('fiber_100g', 0),
                            'other_fat_100g': nutriments.get('fat_100g', 0) - nutriments.get('saturated-fat_100g', 0) - nutriments.get('trans-fat_100g', 0)
                        }
                        url = "https://smartfoodscan-805490564375.europe-west1.run.app/predict"

                        response = requests.post(url, json=data)

                        prediction = response.json()['prediction']

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

    else:
        st.error("Could not detect a barcode. Try another image.")
