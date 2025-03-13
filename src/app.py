import streamlit as st
from barcode_decoder.barcode_reader import barcode_reader
from product_info.api_fetcher import get_product_info
from dietary_analysis.allergens import identify_allergens
from dietary_analysis.labels import check_labels
from nutrition_reader import extract_nutritional_info
from chat_gpt.gpt import get_gpt_response, get_gpt_response_without_barcode
from PIL import Image
import requests
import plotly.graph_objects as go
import base64
import pickle
import pandas as pd



st.markdown(
    """
    <style>
        .stApp {
            background: url('images/pear.png') repeat-y center fixed;
            background-size: contain;
        }
        .block-container {
            max-width: 60%;  /* Increase content width */
        }
        .stRadio {display: flex; justify-content: center; margin-bottom: -100px;
        }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Chewy&display=swap');
    </style>
""", unsafe_allow_html=True)

#Background image
background_image_path = "images/background.png"

def get_base64(img_path):
    with open(img_path, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()
    return encoded
bg_image_base64 = get_base64(background_image_path)

st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.5)), url("data:image/png;base64,{bg_image_base64}") no-repeat center center fixed;
        background-size: cover;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

#App logo and catch sentence
logo = Image.open('images/logo1.png')
st.image(logo, use_container_width=True)
st.markdown(
    "<h2 style='text-align: center; margin-top: -50px; white-space: nowrap; font-size: 2.75em; font-family: \"Chewy\", sans-serif;'>"
    "Discover an easier way to make healthier food choices</h2>",
    unsafe_allow_html=True
)

# User input (removed after product identified)
input_placeholder = st.empty()
with input_placeholder.container():
    col1, col2= st.columns([3, 1])
    with col1:
        st.markdown("<h3 style='text-align: center; margin-right: -150px;color: #455A64;'>How would you like to search for a product?</h3>", unsafe_allow_html=True)
    with col2:
        st.image(f"images/Apple.png", width=50)
    option = st.radio("", ["📸 Take a picture of barcode", "📁 Upload barcode image from device"], horizontal=True,key="search_option")

    if option == "📸 Take a picture of barcode":
        st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
        camera_image = st.camera_input("", key="mike_test")
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
            col1, col2= st.columns([2, 1])
            with col1:
                st.markdown("<h3 style='text-align: center;  font-family: \"Chewy\", sans-serif; margin-right: -300px; margin-top: 30px; '>Some product information</h3>", unsafe_allow_html=True)
            with col2:
                st.image(f"images/Carrot.png", width=50)
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
                    <h3 style="font-size: 18px; margin-bottom: -20px;"><span style="font-weight: bold;">Name: </span>{product_info.get('product_name', 'Unknown').title()}</h3>
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

                # Load the scaler
                with open("models/robust_scaler.pkl", "rb") as f:
                    robust_scaler = pickle.load(f)

                input_data = pd.DataFrame(data, index=[0])

                input_data_scaled = pd.DataFrame(robust_scaler.transform(input_data))
                input_data_scaled.columns = input_data.columns

                data = input_data_scaled.to_dict(orient='records')[0]

                url = "https://smartfoodscan-805490564375.europe-west1.run.app/predict"
                response = requests.post(url, json=data)

                prediction = response.json()['prediction']

                score_value = max(0, min(prediction[0], 100))
                score_value = 100 - score_value  # Invert the score
                # Fake the numbers
                score_value = 100 * (score_value / 100) ** 1.5

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
                    title={'text': "",'font': {'size': 30, 'color': '#37474F'}},
                    gauge={
                        'axis': {'visible': True, 'range': [0, 100],'tickwidth': 2, 'tickcolor': 'black'},
                        'bar': {'color': bar_color,'thickness': 1},
                        'steps': [],
                        'shape': 'angular',
                        'bordercolor': "black",
                        'borderwidth': 1,
                        'bgcolor': 'rgba(0,0,0,0)'},
                    ))
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=300,
                    margin=dict(l=0, r=0, t=0, b=0),
                    )
                col1, col2= st.columns([1, 1])
                with col1:
                    st.markdown("<h3 style='text-align: center;  font-family: \"Chewy\", sans-serif; margin-right: -275px; margin-top: 100px '>Healthiness Score</h3>", unsafe_allow_html=True)
                with col2:
                    st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)
                    st.image(f"images/F&V.png", width=150)


                st.markdown('<div style="height: 100px;margin-top:-100px;"></div>', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

                #Chat GPT details
                chatgpt_response = get_gpt_response(barcode)
                if chatgpt_response:
                    col1, col2= st.columns([3, 1])
                    with col1:
                        st.markdown("<h3 style='text-align: center; margin-top:50px ;margin-right: -150px;font-family: \"Chewy\", sans-serif;'>Here are some useful insights about this product</h3>", unsafe_allow_html=True)
                    with col2:
                        st.image(f"images/Pineapple.png", width=50)
                    st.write(chatgpt_response)

            st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

            with st.container():
                button_clicked = st.button("🔄 Scan Another Product", key="go_back", help="Click to scan another product", use_container_width=True)


            if button_clicked:
                st.rerun()



        else:
            st.error("Failed to fetch product information. You can try with an image of the Nutritional Facts.")

            input_placeholder = st.empty()
            with input_placeholder.container():
                st.markdown("<h3 style='text-align: center; margin-top: 10px; margin-bottom: -70px; color: #455A64'>How would you like to submit nutritional facts?</p>", unsafe_allow_html=True)
                option = st.radio("", ["📸 Take a picture of nutritional facts", "📁 Upload nutritional facts image from device"], horizontal=True,key="search_option2")

                if option == "📸 Take a picture of nutritional facts":
                    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
                    camera_image = st.camera_input("", key="mike_test2")
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
#### Undetermined conflict from Celeste's merge (March 10) - marked conflict free on pull request.
### The conflict starts here as HEAD (Current)

                        # # Nutritional information visualization
                        # st.subheader("Nutritional Information")
                        # # if "nutriments" in nutriments:
                        # nutrients = {
                        #     "Energy (kcal)": nutriments.get('energy-kcal_100g', 0),
                        #     "Saturated Fat (g)": nutriments.get('saturated-fat_100g', 0),
                        #     "Sugars (g)": nutriments.get('sugars_100g', 0),
                        #     "Protein (g)": nutriments.get('proteins_100g', 0),
                        #     "Fiber (g)": nutriments.get('fiber_100g', 0),
                        #     "Sodium (mg)": nutriments.get('sodium_100g', 0),
                        # }
                        # print("The nutrients are: ", nutrients)
                        # st.bar_chart(nutrients)

                        # # Healthiness score prediction
                        # st.subheader("⚕️ Healthiness Score")
### And ends here as Incoming
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

                        # Load the scaler
                        with open("models/robust_scaler.pkl", "rb") as f:
                            robust_scaler = pickle.load(f)

                        input_data = pd.DataFrame(data, index=[0])

                        input_data_scaled = pd.DataFrame(robust_scaler.transform(input_data))
                        input_data_scaled.columns = input_data.columns

                        data = input_data_scaled.to_dict(orient='records')[0]

                        url = "https://smartfoodscan-805490564375.europe-west1.run.app/predict"

                        response = requests.post(url, json=data)

                        prediction = response.json()['prediction']
                        score_value = max(0, min(prediction[0], 100))
                        score_value = 100 - score_value  # Invert the score
                        score_value = 100 * (score_value / 100) ** 1.5
                        value = int(score_value)
                        bar_color = '#FF4B4B' if value <= 25 else '#FF6F6F' if value <= 50 else '#FFB74D' if value <= 75 else '#8C9A00'
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=value,
                            title={'text': "",'font': {'size': 30, 'color': '#37474F'}},
                            gauge={
                                'axis': {'visible': True, 'range': [0, 100],'tickwidth': 2, 'tickcolor': 'black'},
                                'bar': {'color': bar_color,'thickness': 1},
                                'steps': [],
                                'shape': 'angular',
                                'bordercolor': "black",
                                'borderwidth': 1,
                                'bgcolor': 'rgba(0,0,0,0)'},
                            ))
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            height=300,
                            margin=dict(l=0, r=0, t=0, b=0),
                            )
                        col1, col2= st.columns([1, 1])
                        with col1:
                            st.markdown("<h3 style='text-align: center;  font-family: \"Chewy\", sans-serif; margin-right: -275px; margin-top: 100px '>Healthiness Score</h3>", unsafe_allow_html=True)
                        with col2:
                            st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)
                            st.image(f"images/F&V.png", width=150)


                        st.markdown('<div style="height: 100px;margin-top:-100px;"></div>', unsafe_allow_html=True)
                        st.plotly_chart(fig, use_container_width=True)

                        st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

                        #Chat GPT details
                        chatgpt_response = get_gpt_response_without_barcode(nutriments)
                        if chatgpt_response:
                            col1, col2= st.columns([3, 1])
                            with col1:
                                st.markdown("<h3 style='text-align: center; margin-top:50px ;margin-right: -150px;font-family: \"Chewy\", sans-serif;'>Here are some useful insights about this product</h3>", unsafe_allow_html=True)
                            with col2:
                                st.image(f"images/Pineapple.png", width=50)
                            st.write(chatgpt_response)

                        st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
                        with st.container():
                            button_clicked = st.button("🔄 Scan Another Product", key="go_back", help="Click to scan another product", use_container_width=True)

                        if button_clicked:
                            st.rerun()

    else:
        st.error("Could not detect a barcode. Try another image.")
