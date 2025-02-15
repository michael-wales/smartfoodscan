import streamlit as st
from barcode_decoder.barcode_reader import barcode_reader
from product_info.api_fetcher import get_product_info

# App title
st.title("SmartFoodScan 🍏")

# Ask user to upload an image
uploaded_file = st.file_uploader("Upload a barcode image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Extract barcode from image
    barcode = barcode_reader(uploaded_file)

    if barcode:
        # Show user the barcode
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
                st.image(product_info["image_url"], caption="Product Image", use_column_width=True)

            # Check for allergy suitability
            allergens = product_info.get("allergens", "").lower()
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
