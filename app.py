import streamlit as st
from PIL import Image
from io import BytesIO
from streamlit_drawable_canvas import st_canvas
import base64

# Fonction pour convertir une image PIL en URL base64
def pil_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Canvas avec image en arrière-plan",
    page_icon="🎨",
    layout="centered"
)

# Titre de l'application
st.title("🎨 Canvas avec image en arrière-plan")

# Chargement de l'image par l'utilisateur
uploaded_file = st.file_uploader("Veuillez charger une image :", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Chargement de l'image avec PIL
    image = Image.open(uploaded_file)
    
    # Convertir l'image en URL base64
    background_image_url = pil_to_base64(image)
    
    # Largeur et hauteur du canevas en fonction de l'image
    canvas_width = image.width
    canvas_height = image.height
    
    # Affichage du canevas avec l'image en arrière-plan
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Couleur de remplissage par défaut
        stroke_width=3,
        stroke_color="#000000",
        background_image=background_image_url,  # URL base64 comme fond
        width=canvas_width,
        height=canvas_height,
        drawing_mode="freedraw",  # Mode dessin libre
        key="canvas",
    )
    
    # Affichage des résultats du dessin
    if canvas_result.image_data is not None:
        st.image(canvas_result.image_data, caption="Résultat du canevas")

else:
    st.info("Veuillez charger une image pour commencer.")
