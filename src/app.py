import streamlit as st
from barcode_decoder.barcode_reader import barcode_reader
from product_info.api_fetcher import get_product_info

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

        if product_info:
            #Display product info
            name = product_info.get('product_name', 'Unknown')
            brand = product_info.get('brands', 'Unknown').split(',')[0]
            ingredients = product_info.get('ingredients_text', 'Unknown')
            st.subheader("Product Information")
            st.write(f"**Name:** {name}")
            st.write(f"**Brand:** {brand}")
            st.write(f"**Ingredients:** {ingredients}")

            # Display image if available
            if "image_url" in product_info:
                st.image(product_info["image_url"], caption="Product Image")

            # Check for allergy suitability
            allergens = product_info.get("allergens_from_ingredients", "").lower()
            #st.write(f"**Allergens:** {allergens}")
            common_allergens = ["gluten", "almond", "lactose", "egg"]
            unsuitable = [a for a in common_allergens if a in allergens]

            if unsuitable:
                st.error(f"⚠️ Not suitable for: {', '.join(unsuitable)}")

            else:
                st.success("✅ Suitable for common allergies!")
        else:
            st.error("Product not found in OpenFoodFacts database.")
    else:
        st.error("Could not detect a barcode. Try another image.")
