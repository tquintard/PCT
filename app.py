# import streamlit as st
# from streamlit_drawable_canvas import st_canvas
# from PIL import Image
# import os

# # Charger une image par défaut
# default_image_path = "test/Untitled.png"  # Remplacez par le chemin de votre image
# if os.path.exists(default_image_path):
#     default_image = Image.open(default_image_path).convert("RGBA")
# else:
#     st.error("L'image par défaut est introuvable. Vérifiez le chemin.")

# # Dimensions fixes
# resized_width, resized_height = 800, 600

# # Afficher le canevas avec l'image
# if 'default_image' in locals():
#     canvas_result = st_canvas(
#         stroke_width=2,
#         stroke_color="#FF4B4B",
#         background_image=default_image,  # Passez directement l'objet PIL ici
#         update_streamlit=True,
#         height=resized_height,
#         width=resized_width,
#         drawing_mode="freedraw",
#         key="canvas_test",
#     )

#     # Vérifier les résultats
#     if canvas_result and canvas_result.json_data:
#         st.write("Points sélectionnés :", canvas_result.json_data["objects"])
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from streamlit_javascript import st_javascript
import csv


def main(): 

    # Configurer les paramètres de la page
    st.set_page_config(
        page_title="Graph Digitizer",  # Titre de la page
        layout="wide",  # Mode large
        initial_sidebar_state="collapsed",  # Barre latérale déployée
    )

    # Set generic command to get session_state 
    stss = st.session_state
    # Titre de l'application
    st.title("Graph Digitizer")

    # Récupérer la largeur du navigateur
    browser_width = st_javascript("window.innerWidth")

    # Créer deux colonnes
    ratios = [0.25, 0.75]
    _, col2_w = list(map(lambda x: x * browser_width, ratios))
    col1, col2 = st.columns(ratios)  # Ajuster les proportions des colonnes si nécessaire

        # Colonne 2 : Afficher les points sélectionnés
    with col1:
        # Téléchargement de l'image
        st.subheader("Upload a graph to digitize", divider= "rainbow")
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
                original_width, original_height = image.size
                # Calculer la nouvelle hauteur de l'image pour garder les proportions
                #resized_width = int(col2_w) - 10
                #resized_height = int(resized_width * original_height / original_width)
                resized_width, resized_height = 800, 600
    
                # Colonne 1 : Configurer le canevas interactif                          
                #with col2:
                    
    
                # Configurer le canevas interactif avec les dimensions recalculées
                canvas_result = st_canvas(
                    #fill_color="rgba(255, 165, 0, 0.3)",  # Couleur de remplissage
                    stroke_width=8,  # Épaisseur des lignes
                    stroke_color="#FF4B4B",  # Couleur des lignes
                    background_image=image,  # Image de fond
                    update_streamlit=True,
                    height=resized_height,
                    width=resized_width,
                    drawing_mode="point",  # Mode point
                    point_display_radius=4,  # Rayon des points
                    key="canvas",
                )
                
                # #with col1:
                #     if canvas_result.json_data is not None:
                #         points = canvas_result.json_data["objects"]
                #         if stss.get("cal_OK") is None: 
                #             st.subheader("Calibration points", divider= "rainbow")
                #             if not points:
                #                 st.write("#### Select the origin")
                #             elif len(points) == 1:
                #                     st.write("#### Select a point on X-axis")
                #                 # Demander les coordonnées relatives de l'origine
                #             elif len(points) == 2:
                #                 st.write("#### Select a point on Y-axis")
                #             elif len(points) == 3:
                #                 #Calibrate origin
                #                 st.write("#### Origin's absolute coordinates")
                #                 cola, colb = st.columns(2)
                #                 with cola:
                #                     origin_abs_x = st.number_input("X-axis absolute origin", min_value=-100_000_000, value=0)
                #                 with colb:
                #                     origin_abs_y = st.number_input("Y-axis absolute origin", min_value=-100_000_000, value=0,)
                #                 stss["abs_origin"] = origin_abs_x, origin_abs_y
                #                 stss["rel_origin"] = points[0]["left"], points[0]["top"]
    
                #                 #Calibrate X-axis
                #                 st.write("#### X-axis point coordinates")
                #                 stss["abs_x_axis"] = st.number_input("X-axis absolute value", min_value= -100_000_000, value=stss.get("abs_x_axis"), label_visibility="collapsed")
                #                 stss["rel_x_axis"] = points[1]["left"]
    
                #                 #Calibrate Y-axis
                #                 st.write("#### Y-axis point coordinates")
                #                 stss["abs_y_axis"] = st.number_input("Y-axis absolute value", min_value= -100_000_000, value=stss.get("abs_y_axis"), label_visibility="collapsed")
                #                 stss["rel_y_axis"] = points[2]["top"]
    
                #                 #Validate the calibration
                #                 if st.button("Validate"):
                #                     stss["pxl_width"] = stss["rel_x_axis"] - stss["rel_origin"][0]
                #                     stss["pxl_height"] = stss["rel_origin"][1] - stss["rel_y_axis"]  # Assuming the graph increases upwards
                #                     st.success("Calibration completed.")
                #                     stss["cal_OK"] = True
                #         else:
                #             st.subheader("Graph data", divider= "rainbow")
                #             data_points = [(point["left"], point["top"]) for point in canvas_result.json_data["objects"][3:]]
                #             abs_pt = list()
                #             for idx, point in enumerate(data_points):
                #                 real_x = stss["abs_origin"][0] + (stss["abs_x_axis"] - stss["abs_origin"][0]) * (point[0] - stss["rel_origin"][0]) / stss["pxl_width"]
                #                 real_y = stss["abs_origin"][1] + (stss["abs_y_axis"] - stss["abs_origin"][1]) * (stss["rel_origin"][1] - point[1]) / stss["pxl_height"]
                #                 abs_pt.append((real_x, real_y))
                #                 st.write(f"Point {idx + 1}: X={real_x:.2f}, Y={real_y:.2f}")
    
                #             # Exporter les données en CSV
                #             if st.button("Export data to CSV"):
                #                 csv_file = "extracted_data.csv"
                #                 with open(csv_file, "w", newline="") as file:
                #                     writer = csv.writer(file)
                #                     writer.writerow(["X", "Y"])
                #                     writer.writerows(data_points)
                #                 st.success(f"Data exported to {csv_file}")
                #     else:
                #         st.warning("Please upload a graph to digitize.")
                #         st.session_state["calibration_points"] = None
            except Exception as e:
                st.error(f"Une erreur s'est produite lors de l'affichage du canevas : {e}")

if __name__ == "__main__":
    main()
