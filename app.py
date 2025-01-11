import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import os

def main():
    st.set_page_config(page_title="Graph Digitizer", layout="wide")
    st.title("Graph Digitizer")

    # Téléchargement de l'image
    uploaded_file = st.file_uploader("Téléchargez une image", type=["png", "jpg", "jpeg"])
    
    # Charger une image par défaut pour tester
    default_image_path = "path/to/default/image.png"
    default_image = None
    if os.path.exists(default_image_path):
        default_image = Image.open(default_image_path).convert("RGB")

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Image téléchargée", use_column_width=True)
    elif default_image:
        image = default_image
        st.image(image, caption="Image par défaut", use_column_width=True)
    else:
        st.warning("Aucune image disponible.")
        return

    # Dimensions fixes pour le canevas
    resized_width, resized_height = 800, 600
    st.write(f"Dimensions du canevas : {resized_width} x {resized_height}")

    # Afficher le canevas avec l'image
    canvas_result = st_canvas(
        stroke_width=8,
        stroke_color="#FF4B4B",
        background_image=image,  # Passez l'objet PIL ici
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
