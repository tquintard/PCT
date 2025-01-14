import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from streamlit_javascript import st_javascript
from typing import List
import pandas as pd

from collections import defaultdict

TABS = ["Upload", "Calibration", "Curve points"]
VAR_TO_CLEAR = ["cal_OK", "cal_pts"]

@st.cache_data
def load_n_resize_image(uploaded_file, width):
    # Charger l'image et récupérer ses dimensions
    image = Image.open(uploaded_file).convert('L') # ouvrir l'image dans un format compresse
    original_width, original_height = image.size
    # Calculer la nouvelle hauteur de l'image pour garder les proportions
    resized_width = int(width) - 10
    resized_height = int(resized_width * original_height / original_width)
    return image.resize((resized_width, resized_height))

def clear_stss(variables:List[str]):
    for var in variables:
        if st.session_state.get(var):
            del st.session_state[var]

def reset_cal():
    st.session_state["cal_OK"] = False

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
    ratios = [0.3, 0.7]
    st.session_state["col_width"] = list(map(lambda x: x * browser_width, ratios))
    st.session_state["columns"] = st.columns(ratios)  # Ajuster les proportions des colonnes si nécessaire

def update_canva(image):
    return st_canvas(
        stroke_width=10,
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
    stss = st.session_state
    col1, col2 = stss["columns"]
    _, col2_w = stss["col_width"]
    
    
    with col2:
        st.subheader("Graph", divider='rainbow')  
    with col1:
        
        # Téléchargement de l'image
        st.subheader("Upload", divider='rainbow')
        uploaded_file = st.file_uploader("Upload a graph to digitize", type=["png", "jpg", "jpeg"], label_visibility = "collapsed")
        if uploaded_file:
            image = load_n_resize_image(uploaded_file, col2_w)
            with col2:
                cv_res = update_canva(image)

            st.subheader("Calibration", divider='rainbow')
            if cv_res.json_data == None :
                stss["cal_OK"] = False
            elif len(cv_res.json_data['objects']) < 3:
                stss["cal_OK"] = False

            if not stss.get("cal_pts"):
                stss["cal_pts"] = {"origin": {"abs": [0, 0], "rel": [0, 0]}, "axis": {"abs": [0, 0], "rel": [None, None]}}
                stss["pxl"] = []
            rel_origin, rel_axis = stss["cal_pts"]['origin']['rel'], stss["cal_pts"]['axis']['rel']

            #Calibrate origin
            st.write("###### Origin's absolute coordinates")
            cola, colb = st.columns(2)
            with cola:
                rel_origin[0] = st.number_input("X-axis absolute origin", min_value=-100_000_000, value=rel_origin[0], key="rel_origin_x",on_change= lambda: reset_cal())
            with colb:
                rel_origin[1] = st.number_input("Y-axis absolute origin", min_value=-100_000_000, value=rel_origin[1], key="rel_origin_y",on_change= lambda: reset_cal())           
            
            #Calibrate Axis
            st.write("###### Axis absolute coordinates")
            cola, colb = st.columns(2)
            with cola:
                rel_axis[0] = st.number_input("X-axis absolute value", min_value=-100_000_000, value=rel_axis[0], key="rel_axis_x",on_change= lambda: reset_cal())
            with colb:
                rel_axis[1] = st.number_input("Y-axis absolute value", min_value=-100_000_000, value=rel_axis[1], key="rel_axis_y",on_change= lambda: reset_cal())
            stss["cal_pts"]['origin']['rel'], stss["cal_pts"]['axis']['rel'] = rel_origin, rel_axis
            
            if not stss.get("cal_OK"):
                points = cv_res.json_data['objects'][:3] if cv_res.json_data != None else []
                if len(points) == 3:
                    if None in (rel_origin + rel_axis):
                        st.error("At least one calibration point is not filled")
                    else:
                        abs_origin = (points[0]['left'], points[0]['top'])
                        abs_axis = (points[1]['left'], points[2]['top'])
                        stss["cal_pts"]['origin']['abs'], stss["cal_pts"]['axis']['abs'] = abs_origin, abs_axis
                        pxl = abs_axis[0] - abs_origin[0], abs_origin[1] - abs_axis[1]
                        if pxl[0]*pxl[1] == 0:
                            st.error("Please select point on X-axis and Y-axis different from origin")
                        else:
                            stss["pxl"] = pxl
                            stss["cal_OK"] = True
                            st.success("Calibration completed.")
                elif len(points) < 3:
                    st.warning(f"""
                            Please select in this order:
                            - The origin of the graph
                            - A point on the X-axis
                            - A point on the Y-axis
                            """)

        else:
            clear_stss(VAR_TO_CLEAR)
            with col2:
                st.warning("Please upload a graph to digitize.")

        
        if stss.get("cal_OK"):
            st.subheader("Curve points", divider='rainbow')
            rel_origin, rel_axis = stss["cal_pts"]['origin']['rel'], stss["cal_pts"]['axis']['rel']
            abs_origin, abs_axis, pxl = stss["cal_pts"]['origin']['abs'], stss["cal_pts"]['axis']['abs'], stss["pxl"]
            data_points = [(point["left"], point["top"]) for point in cv_res.json_data["objects"][3:]]
            if data_points == []:
                st.write("#### Select curve points on graph")
            else:
                subcol1, subcol2 = st.columns(2, vertical_alignment = 'center')
                with subcol1:
                    sign_fig = st.slider("Number of significant digits", min_value=0, max_value=5, value=0, step=1)
                    
                with subcol2:
                    if st.button("Export data"):
                        st.write("Hello")
                    

                calibrated_points=defaultdict(list)
                for idx, point in enumerate(data_points):
                    real_x = rel_origin[0] + (rel_axis[0] - rel_origin[0]) * (point[0] - abs_origin[0]) / pxl[0]
                    real_y = rel_origin[1] + (rel_axis[1] - rel_origin[1]) * (abs_origin[1] - point[1]) / pxl[1]
                    calibrated_points[f'Pt {idx+1}'] = [real_x, real_y]               
                
                
                df = pd.DataFrame(calibrated_points, index=["X", "Y"])

                df_styled = df.style.format(f"{{:.{sign_fig}f}}", subset=df.select_dtypes(include="number").columns)

                st.dataframe(df_styled, use_container_width = True) 

if __name__ == "__main__":
    init_page()
    main()
