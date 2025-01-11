import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import os
import tempfile

# Sauvegarder l'image dans un fichier temporaire
def pil_to_temp_file(image):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    image.save(temp_file.name, format="PNG")
    return temp_file.name

def main():
    st.set_page_config(page_title="Graph Digitizer", layout="wide")
    st.title("Graph Digitizer")

    # Téléchargement de l'image
    uploaded_file = st.file_uploader("Téléchargez une image", type=["png", "jpg", "jpeg"])
    
    # Charger une image par défaut pour tester
    default_image_path = "default_image.png"  # Remplacez par un chemin valide
    default_image = None
    if os.path.exists(default_image_path):
        default_image = Image.open(default_image_path).convert("RGBA")

    image = None
    if uploaded_file:
        try:
            image = Image.open(uploaded_file).convert("RGBA")
            st.success("Image téléchargée avec succès.")
        except Exception as e:
            st.error(f"Échec du téléchargement ou du traitement de l'image : {e}")
    elif default_image:
        st.info("Aucune image téléchargée. Utilisation de l'image par défaut.")
        image = default_image
    else:
        st.warning("Veuillez télécharger une image pour continuer.")

    if image:
        try:
            # Dimensions fixes pour le canevas
            resized_width, resized_height = 800, 600
            st.write(f"Dimensions du canevas : {resized_width} x {resized_height}")

            # Sauvegarder l'image dans un fichier temporaire
            temp_file_path = pil_to_temp_file(image)

            # Charger l'image temporaire comme arrière-plan du canevas
            canvas_result = st_canvas(
                stroke_width=2,
                stroke_color="#FF4B4B",
                background_image=Image.open(temp_file_path),  # Charger l'image temporaire ici
                update_streamlit=True,
                height=resized_height,
                width=resized_width,
                drawing_mode="point",
                key="canvas_test",
            )

            # Résultats
            if canvas_result and canvas_result.json_data:
                st.write("Points sélectionnés :", canvas_result.json_data["objects"])
        except Exception as e:
            st.error(f"Une erreur s'est produite lors de l'affichage du canevas : {e}")

if __name__ == "__main__":
    main()
