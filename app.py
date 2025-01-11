import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import os

# Charger une image par défaut
default_image_path = "test/Untitled.png"  # Remplacez par le chemin de votre image
if os.path.exists(default_image_path):
    default_image = Image.open(default_image_path).convert("RGBA")
else:
    st.error("L'image par défaut est introuvable. Vérifiez le chemin.")

# Dimensions fixes
resized_width, resized_height = 800, 600

# Afficher le canevas avec l'image
if 'default_image' in locals():
    canvas_result = st_canvas(
        stroke_width=2,
        stroke_color="#FF4B4B",
        background_image=default_image,  # Passez directement l'objet PIL ici
        update_streamlit=True,
        height=resized_height,
        width=resized_width,
        drawing_mode="freedraw",
        key="canvas_test",
    )

    # Vérifier les résultats
    if canvas_result and canvas_result.json_data:
        st.write("Points sélectionnés :", canvas_result.json_data["objects"])
