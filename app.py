import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from streamlit_javascript import st_javascript
import csv
import os

# Fonction pour sauvegarder l'image dans un fichier temporaire (si nécessaire)
def save_image_to_temp_file(image):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    image.save(temp_file.name, format="PNG")
    return temp_file.name

def main():
    # Configurer les paramètres de la page
    st.set_page_config(
        page_title="Graph Digitizer", 
        layout="wide", 
        initial_sidebar_state="collapsed",
    )

    stss = st.session_state  # Gestion de l'état de la session
    st.title("Graph Digitizer")

    # Récupérer la largeur du navigateur
    browser_width = st_javascript("window.innerWidth")

    # Créer deux colonnes pour l'affichage
    ratios = [0.25, 0.75]
    _, col2_w = list(map(lambda x: x * browser_width, ratios))
    col1, col2 = st.columns(ratios)

    # Colonne 1 : Téléchargement de l'image
    with col1:
        st.subheader("Upload a graph to digitize", divider="rainbow")
        uploaded_file = st.file_uploader(
            "Upload a graph capture",
            type=["png", "jpg", "jpeg"],
            label_visibility="collapsed"
        )

    # Gestion des images (téléchargées ou par défaut)
    image = None
    if uploaded_file:
        try:
            image = Image.open(uploaded_file).convert("RGBA")
            st.success("Image téléchargée avec succès.")
        except Exception as e:
            st.error(f"Échec du téléchargement ou du traitement de l'image : {e}")
    else:
        default_image_path = "default_image.png"  # Remplacez par le chemin valide
        if os.path.exists(default_image_path):
            image = Image.open(default_image_path).convert("RGBA")
            st.info("Utilisation de l'image par défaut.")
        else:
            st.warning("Veuillez télécharger une image ou vérifier le chemin de l'image par défaut.")

    # Colonne 2 : Affichage du canevas et points sélectionnés
    if image:
        original_width, original_height = image.size
        resized_width = int(col2_w) - 10
        resized_height = int(resized_width * original_height / original_width)

        with col2:
            canvas_result = st_canvas(
                stroke_width=8,
                stroke_color="#FF4B4B",
                background_image=image,  # Image en objet PIL
                update_streamlit=True,
                height=resized_height,
                width=resized_width,
                drawing_mode="point",
                point_display_radius=4,
                key="canvas",
            )

        # Gestion des points sélectionnés
        if canvas_result.json_data:
            points = canvas_result.json_data["objects"]
            if stss.get("cal_OK") is None:  # Calibration
                with col1:
                    st.subheader("Calibration points", divider="rainbow")
                    if not points:
                        st.write("#### Select the origin")
                    elif len(points) == 1:
                        st.write("#### Select a point on X-axis")
                    elif len(points) == 2:
                        st.write("#### Select a point on Y-axis")
                    elif len(points) == 3:
                        st.write("#### Origin's absolute coordinates")
                        cola, colb = st.columns(2)
                        with cola:
                            origin_abs_x = st.number_input("X-axis absolute origin", value=0)
                        with colb:
                            origin_abs_y = st.number_input("Y-axis absolute origin", value=0)
                        stss["abs_origin"] = (origin_abs_x, origin_abs_y)
                        stss["rel_origin"] = (points[0]["left"], points[0]["top"])

                        st.write("#### X-axis point coordinates")
                        stss["abs_x_axis"] = st.number_input("X-axis absolute value", value=stss.get("abs_x_axis"))
                        stss["rel_x_axis"] = points[1]["left"]

                        st.write("#### Y-axis point coordinates")
                        stss["abs_y_axis"] = st.number_input("Y-axis absolute value", value=stss.get("abs_y_axis"))
                        stss["rel_y_axis"] = points[2]["top"]

                        if st.button("Validate"):
                            stss["pxl_width"] = stss["rel_x_axis"] - stss["rel_origin"][0]
                            stss["pxl_height"] = stss["rel_origin"][1] - stss["rel_y_axis"]
                            st.success("Calibration completed.")
                            stss["cal_OK"] = True
            else:
                with col1:
                    st.subheader("Graph data", divider="rainbow")
                    data_points = [(point["left"], point["top"]) for point in points[3:]]
                    abs_pt = []
                    for idx, point in enumerate(data_points):
                        real_x = stss["abs_origin"][0] + (stss["abs_x_axis"] - stss["abs_origin"][0]) * (point[0] - stss["rel_origin"][0]) / stss["pxl_width"]
                        real_y = stss["abs_origin"][1] + (stss["abs_y_axis"] - stss["abs_origin"][1]) * (stss["rel_origin"][1] - point[1]) / stss["pxl_height"]
                        abs_pt.append((real_x, real_y))
                        st.write(f"Point {idx + 1}: X={real_x:.2f}, Y={real_y:.2f}")

                    if st.button("Export data to CSV"):
                        csv_file = "extracted_data.csv"
                        with open(csv_file, "w", newline="") as file:
                            writer = csv.writer(file)
                            writer.writerow(["X", "Y"])
                            writer.writerows(abs_pt)
                        st.success(f"Data exported to {csv_file}")
    else:
        st.warning("Please upload a graph to digitize.")
        st.session_state["calibration_points"] = None

if __name__ == "__main__":
    main()
