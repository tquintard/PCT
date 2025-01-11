import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas

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
    
    # Afficher l'image chargée
    st.image(image, caption="Image chargée", use_column_width=True)
    
    st.write("Utilisez le canevas ci-dessous pour dessiner ou annoter.")
    
    # Largeur et hauteur du canevas en fonction de l'image
    canvas_width = image.width
    canvas_height = image.height
    
    # Affichage du canevas avec l'image en arrière-plan
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Couleur de remplissage par défaut
        stroke_width=3,
        stroke_color="#000000",
        background_image=image,
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
