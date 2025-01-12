import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from streamlit_javascript import st_javascript
import csv
import random
from typing import List

def load_n_resize_image(uploaded_file, width):
    # Charger l'image et récupérer ses dimensions
    image = Image.open(uploaded_file)
    original_width, original_height = image.size
    # Calculer la nouvelle hauteur de l'image pour garder les proportions
    resized_width = int(width) - 10
    resized_height = int(resized_width * original_height / original_width)
    return image.resize((resized_width, resized_height))

def set_canvas(image):
    return  st_canvas(
                #fill_color="rgba(255, 165, 0, 0.3)",  # Couleur de remplissage
                stroke_width=16,  # Épaisseur des lignes
                stroke_color="#FF4B4B",  # Couleur des lignes
                background_image=image,  # Image de fond 
                update_streamlit=True,
                height=image.height,
                width=image.width,
                drawing_mode="freedraw",  # Mode point
                #point_display_radius=4,  # Rayon des points
                key="canvas",
            )

def clear_stss(stss, variables:List[str]):
    for var in variables:
        if stss.get(var):
            del stss[var]

def pixel_to_real(point, pxl_width, pxl_height, rel_x_axis, rel_y_axis, origin):   
    real_x = origin[0] + (rel_x_axis - origin[0]) * (point[0] - origin[0]) / pxl_width
    real_y = origin[1] + (rel_y_axis - origin[1]) * (origin[1] - point[1]) / pxl_height
    return real_x, real_y

def main(): 

    # Configurer les paramètres de la page
    st.set_page_config(
        page_title="Graph Digitizer",  # Titre de la page
        layout="wide",  # Mode large
        initial_sidebar_state="collapsed",  # Barre latérale déployée
    )

    # Initialisation of variable
    
    # Set generic command to get session_state 
    stss = st.session_state

    # Titre de l'application
    st.title(f"Graph Digitizer {random.randint(1, 100)}")

    # Récupérer la largeur du navigateur
    if not stss.get("browser_width"):
        stss["browser_width"] = st_javascript("window.innerWidth")

    # Créer deux colonnes
    ratios = [0.25, 0.75]
    _, col2_w = list(map(lambda x: x * stss["browser_width"], ratios))
    col1, col2 = st.columns(ratios)  # Ajuster les proportions des colonnes si nécessaire

    # Colonne 2 : Afficher les points sélectionnés
    with col1:
        # Téléchargement de l'image
        st.subheader("Upload a graph to digitize", divider= "rainbow")
        uploaded_file = st.file_uploader("_", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        try:
            if uploaded_file:
                if not stss.get("image"):
                    stss["image"] = load_n_resize_image(uploaded_file, col2_w)
            else:
                #clear the session state
                var_to_clr = ["image", "cv_res", "cal_OK"]
                clear_stss(stss, var_to_clr)
                st.warning("Please upload a graph to digitize.")
        except Exception as e:
            st.error(f"Error: {e}")
                
    if stss.get("image"):
        # Colonne 1 : Configurer le canevas interactif                          
        with col2:  
            # Configurer le canevas interactif avec les dimensions recalculées
            stss["cv_res"] = set_canvas(stss["image"])

        with col1:
            if stss["cv_res"].json_data is not None:
                points = stss["cv_res"].json_data["objects"]
                
                if stss.get("cal_OK") is None: 
                    st.subheader("Calibration points", divider= "rainbow")
                    if not points:
                        st.write("#### Select the origin")
                    elif len(points) == 1:
                        st.write("#### Select a point on X-axis")
                    elif len(points) == 2:
                        st.write("#### Select a point on Y-axis")
                    elif len(points) == 3:
                        #Calibrate origin
                        st.write("#### Origin's absolute coordinates")
                        cola, colb = st.columns(2)
                        with cola:
                            origin_abs_x = st.number_input("X-axis absolute origin", min_value=-100_000_000, value=0)
                        with colb:
                            origin_abs_y = st.number_input("Y-axis absolute origin", min_value=-100_000_000, value=0,)
                        
                        
                        
                        
                        stss["abs_origin"] = origin_abs_x, origin_abs_y
                        stss["rel_origin"] = points[0]["left"], points[0]["top"]

                        #Calibrate X-axis
                        st.write("#### X-axis point coordinates")
                        stss["abs_x_axis"] = st.number_input("X-axis absolute value", min_value= -100_000_000, value=stss.get("abs_x_axis"), label_visibility="collapsed")
                        stss["rel_x_axis"] = points[1]["left"]

                        #Calibrate Y-axis
                        st.write("#### Y-axis point coordinates")
                        stss["abs_y_axis"] = st.number_input("Y-axis absolute value", min_value= -100_000_000, value=stss.get("abs_y_axis"), label_visibility="collapsed")
                        stss["rel_y_axis"] = points[2]["top"]

                        #Validate the calibration
                        if st.button("Validate"):
                            stss["pxl_width"] = stss["rel_x_axis"] - stss["rel_origin"][0]
                            stss["pxl_height"] = stss["rel_origin"][1] - stss["rel_y_axis"]  # Assuming the graph increases upwards
                            st.success("Calibration completed.")
                            stss["cal_OK"] = True
                else:
                    st.subheader("Graph data", divider= "rainbow")
                    data_points = [(point["left"], point["top"]) for point in stss["cv_res"].json_data["objects"][3:]]
                    abs_pt = list()
                    for idx, point in enumerate(data_points):
                        real_x = stss["abs_origin"][0] + (stss["abs_x_axis"] - stss["abs_origin"][0]) * (point[0] - stss["rel_origin"][0]) / stss["pxl_width"]
                        real_y = stss["abs_origin"][1] + (stss["abs_y_axis"] - stss["abs_origin"][1]) * (stss["rel_origin"][1] - point[1]) / stss["pxl_height"]
                        abs_pt.append((real_x, real_y))
                        st.write(f"Point {idx + 1}: X={real_x:.0f}, Y={real_y:.0f}")

                    # Exporter les données en CSV
                    if st.button("Export data to CSV"):
                        csv_file = "extracted_data.csv"
                        with open(csv_file, "w", newline="") as file:
                            writer = csv.writer(file)
                            writer.writerow(["X", "Y"])
                            writer.writerows(data_points)
                        st.success(f"Data exported to {csv_file}")




if __name__ == "__main__":
    main()
