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
        else:
            st.error("Product not found in OpenFoodFacts database.")
    else:
        st.error("Could not detect a barcode. Try another image.")
