import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import os
import base64
from io import BytesIO
import tempfile

# Sauvegarder l'image dans un fichier temporaire
def pil_to_temp_file(image):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    image.save(temp_file.name, format="PNG")
    return temp_file.name

# Convertir l'image PIL en URL base64
def pil_to_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"

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
            
            # Convertir l'image en URL base64
            background_image_url = pil_to_base64(image)

            # Afficher le canevas avec l'image
            canvas_result = st_canvas(
                stroke_width=2,
                stroke_color="#FF4B4B",
                background_image=background_image_url,  # Passez l'URL base64 ici
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
