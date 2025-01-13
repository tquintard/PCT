import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from streamlit_javascript import st_javascript
import csv
import random
from typing import List
import streamlit.components.v1 as components  # Correct module import

from collections import defaultdict

TABS = ["Upload", "Calibration", "Curve points"]
VAR_TO_CLEAR = ["image", "cv_res", "cal_OK", "cal_pts"]

def load_n_resize_image(uploaded_file, width):
    # Charger l'image et récupérer ses dimensions
    image = Image.open(uploaded_file)
    original_width, original_height = image.size
    # Calculer la nouvelle hauteur de l'image pour garder les proportions
    resized_width = int(width) - 10
    resized_height = int(resized_width * original_height / original_width)
    return image.resize((resized_width, resized_height))

def clear_stss(variables:List[str]):
    for var in variables:
        if st.session_state.get(var):
            del st.session_state[var]


def init_page ():
    # Configurer les paramètres de la page
    st.set_page_config(
        page_title="Graph Digitizer",  # Titre de la page
        layout="wide",  # Mode large
        initial_sidebar_state="collapsed",  # Barre latérale déployée
    )
    
    # Titre de l'application
    st.title("Graph Digitizer")  
    # Récupérer la largeur du navigateur
    browser_width = st_javascript("window.innerWidth")
    
    # Créer deux colonnes
    ratios = [0.25, 0.75]
    st.session_state["col_width"] = list(map(lambda x: x * browser_width, ratios))
    st.session_state["columns"] = st.columns(ratios)  # Ajuster les proportions des colonnes si nécessaire

def update_canva():
    if st.session_state.get("image"):
        image = st.session_state.get("image")
        return st_canvas(
            stroke_width=16,
            stroke_color="#FF4B4B",
            background_image=image,
            update_streamlit=False,  # Désactiver les mises à jour automatiques
            height=image.height,
            width=image.width,
            drawing_mode="freedraw",
            key="set_canvas",
        )

def main():
    #Variable initialisation
    col1, col2 = st.session_state["columns"]
    _, col2_w = st.session_state["col_width"]
    stss = st.session_state
    

    # Colonne 2 : Afficher les points sélectionnés
    with col2:
        st.write(random.randint(1, 1000))
        canvas_result = update_canva() 

    with col1:
        tabs = st.tabs(TABS)
        with tabs[0]:
            # Téléchargement de l'image
            uploaded_file = st.file_uploader("Upload a graph to digitize", type=["png", "jpg", "jpeg"])
            if uploaded_file:
                if not stss.get("image"):
                    stss["image"] = load_n_resize_image(uploaded_file, col2_w)
                    with col2:
                        canvas_result = update_canva()
            else:
                #clear the session state
                clear_stss(VAR_TO_CLEAR)
                st.warning("Please upload a graph to digitize.")

        with tabs[1]:
            if not stss.get("cal_pts"):
                stss["cal_pts"] = {"origin": {"abs": [0, 0], "rel": [0, 0]}, "axis": {"abs": [0, 0], "rel": [None, None]}}
                stss["pxl"] = []
            rel_origin, rel_axis = stss["cal_pts"]['origin']['rel'], stss["cal_pts"]['axis']['rel']

            #Calibrate origin
            st.write("#### Origin's absolute coordinates")
            cola, colb = st.columns(2)
            with cola:
                rel_origin[0] = st.number_input("X-axis absolute origin", min_value=-100_000_000, value=rel_origin[0])
            with colb:
                rel_origin[1] = st.number_input("Y-axis absolute origin", min_value=-100_000_000, value=rel_origin[1])           
            
            #Calibrate Axis
            st.write("#### Axis absolute coordinates")
            cola, colb = st.columns(2)
            with cola:
                rel_axis[0] = st.number_input("X-axis absolute value", min_value=-100_000_000, value=rel_axis[0])
            with colb:
                rel_axis[1] = st.number_input("Y-axis absolute value", min_value=-100_000_000, value=rel_axis[1])
            stss["cal_pts"]['origin']['rel'], stss["cal_pts"]['axis']['rel'] = rel_origin, rel_axis
            
            # Bouton pour capturer les données JSON
            if st.button("Calibrate"):
                points = canvas_result.json_data['objects'][:3]
                if len(points) == 3:
                    abs_origin = (points[0]['left'], points[0]['top'])
                    abs_axis = (points[1]['left'], points[2]['top'])
                    stss["cal_pts"]['origin']['abs'], stss["cal_pts"]['axis']['abs'] = abs_origin, abs_axis
                    pxl = abs_axis[0] - abs_origin[0], abs_origin[1] - abs_axis[1]
                    stss["pxl"] = pxl
                    stss["cal_OK"] = True
                    st.success("Calibration completed.")
            abs_origin, abs_axis, pxl = stss["cal_pts"]['origin']['abs'], stss["cal_pts"]['axis']['abs'], stss["pxl"]

        with tabs[2]:
            if stss.get("cal_OK"):
                st.write("#### Select curve points")
                if st.button("Get points"):
                    data_points = [(point["left"], point["top"]) for point in canvas_result.json_data["objects"][3:]]
                    for idx, point in enumerate(data_points):
                        real_x = rel_origin[0] + (rel_axis[0] - rel_origin[0]) * (point[0] - abs_origin[0]) / pxl[0]
                        real_y = rel_origin[1] + (rel_axis[1] - rel_origin[1]) * (abs_origin[1] - point[1]) / pxl[1]
                        st.write(f"Point {idx + 1}: X={real_x:.0f}, Y={real_y:.0f}")
                    
    
        
                #st.write(stss["cal_pts"])
                #st.write(stss["pxl"])

        #print(2)

if __name__ == "__main__":
    init_page()
    main()
