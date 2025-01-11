import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import os

def main():
    st.set_page_config(page_title="Graph Digitizer", layout="wide")
    st.title("Graph Digitizer")

    # Téléchargement de l'image
    uploaded_file = st.file_uploader("Téléchargez une image", type=["png", "jpg", "jpeg"])
    image = None
    if uploaded_file:
        try:
            image = Image.open(uploaded_file).convert("RGBA")
            st.success("Image téléchargée avec succès.")
        except Exception as e:
            st.error(f"Échec du téléchargement ou du traitement de l'image : {e}")
    else:
        st.warning("Veuillez télécharger une image ou vérifier le chemin de l'image par défaut.")

    if image:
        try:
            # Dimensions fixes pour le canevas
            resized_width, resized_height = 800, 600
            st.write(f"Dimensions du canevas : {resized_width} x {resized_height}")

            # Afficher le canevas avec l'image
            canvas_result = st_canvas(
                stroke_width=2,
                stroke_color="#FF4B4B",
                background_image=image,  # Passez directement l'objet PIL ici
                update_streamlit=True,
                height=resized_height,
                width=resized_width,
                drawing_mode="freedraw",
                key="canvas_test",
            )

            # Résultats
            if canvas_result and canvas_result.json_data:
                st.write("Points sélectionnés :", canvas_result.json_data["objects"])
        except Exception as e:
            st.error(f"Une erreur s'est produite lors de l'affichage du canevas : {e}")

if __name__ == "__main__":
    main()
