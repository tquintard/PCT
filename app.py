import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import os
import base64
from io import BytesIO

# Convert PIL image to base64
def pil_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode()
    return f"data:image/png;base64,{img_base64}"

def pil_to_data_url(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    img_bytes = buffer.read()
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
    return f"data:image/png;base64,{img_base64}"
    
def main():
    st.set_page_config(page_title="Graph Digitizer", layout="wide")
    st.title("Graph Digitizer")

    # Téléchargement de l'image
    uploaded_file = st.file_uploader("Téléchargez une image", type=["png", "jpg", "jpeg"])
    
    # Charger une image par défaut pour tester
    default_image_path = "path/to/default/image.png"
    default_image = None
    if os.path.exists(default_image_path):
        default_image = Image.open(default_image_path).convert("RGBA")

    if uploaded_file:
        try:
            image = Image.open(uploaded_file).convert("RGBA")
            st.write(f"Type of background_image: {type(image)}")
            # Convert image to base64 URL
            background_image_url = pil_to_base64(image)
            st.write(f"Type of background_image: {type(background_image_url)}")
            st.success("Image successfully converted to RGBA format.")
        except Exception as e:
            st.error(f"Image conversion failed: {e}")
            background_image_url = pil_to_data_url(image)

        # Dimensions fixes pour le canevas
        resized_width, resized_height = 800, 600
        st.write(f"Dimensions du canevas : {resized_width} x {resized_height}")
    
        # Afficher le canevas avec l'image
        canvas_result = st_canvas(
            stroke_width=8,
            stroke_color="#FF4B4B",
            background_image=background_image_url,  # Passez l'objet PIL ici
            update_streamlit=True,
            height=resized_height,
            width=resized_width,
            drawing_mode="point",
            key="canvas_test",
        )

        # Résultats
        if canvas_result and canvas_result.json_data:
            st.write("Points sélectionnés :", canvas_result.json_data["objects"])

if __name__ == "__main__":
    main()
