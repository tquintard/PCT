import time
from collections import defaultdict
from typing import List, Tuple

import pandas as pd
import streamlit as st
from PIL import Image
from streamlit.runtime.uploaded_file_manager import UploadedFile
from streamlit_drawable_canvas import st_canvas
from streamlit_javascript import st_javascript

TABS = ["Upload", "Calibration", "Curve points"]
VAR_TO_CLEAR = ["cal_OK", "cal_pts"]
DEBUG_MODE = True  # Tu peux le mettre à False aussi pour faire disparaitre


def show_execution_time(debug_mode=True):
    """
    A decorator to measure and optionally display the execution time of the decorated function.

    Parameters:
    -----------
    debug_mode : bool, optional
        If True, prints the execution time of the function (default is True).

    Returns:
    --------
    Callable
        A decorator that wraps the original function and measures its execution time.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            if not debug_mode:
                pass
            else:
                st.write(
                    f"⏲ **Execution time** of `{func.__name__}`: {execution_time:.3f} seconds"
                )
            return result

        return wrapper

    return decorator


@show_execution_time(debug_mode=DEBUG_MODE)
@st.cache_data
def load_n_resize_image(uploaded_file: UploadedFile, width: float) -> Image.Image:
    # Charger l'image et récupérer ses dimensions
    image = Image.open(uploaded_file).convert(
        "L"
    )  # ouvrir l'image dans un format compresse
    original_width, original_height = image.size
    # Calculer la nouvelle hauteur de l'image pour garder les proportions
    resized_width = int(width) - 10
    resized_height = int(resized_width * original_height / original_width)
    return image.resize((resized_width, resized_height))


@show_execution_time(debug_mode=DEBUG_MODE)
@st.cache_data
def do_cal(points: List[dict]) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    abs_origin = (points[0]["left"], points[0]["top"])
    abs_axis = (points[1]["left"], points[2]["top"])
    pxl = abs_axis[0] - abs_origin[0], abs_origin[1] - abs_axis[1]
    return abs_origin, pxl


@show_execution_time(debug_mode=DEBUG_MODE)
def create_columns(col2_ratio: float) -> Tuple:
    col2_width = st_javascript("window.innerWidth") * col2_ratio
    col1, col2 = st.columns([1 - col2_ratio, col2_ratio])
    return col1, col2, col2_width


@show_execution_time(debug_mode=DEBUG_MODE)
def reset_cal(cv_res=None) -> None:
    # cases where calibration is reset
    if cv_res is None:
        # if no image is uploaded
        st.session_state["cal_OK"] = False
    elif len(cv_res["objects"]) < 3:
        # if no points are drawn on canvas
        st.session_state["cal_OK"] = False


@show_execution_time(debug_mode=DEBUG_MODE)
def init_page():
    # Configurer les paramètres de la page
    st.set_page_config(
        page_title="Graph Digitiser",  # Titre de la page
        layout="wide",  # Mode large
        initial_sidebar_state="collapsed",  # Barre latérale déployée
        page_icon="📈",
    )

    # App title
    st.title(":material/show_chart: :blue-background[Graph Digitiser]")


@show_execution_time(debug_mode=DEBUG_MODE)
def update_canva(image):
    return st_canvas(
        stroke_width=10,
        stroke_color="#FF4B4B",
        background_image=image,
        update_streamlit=False,  # Désactiver les mises à jour automatiques
        height=image.height,
        width=image.width,
        drawing_mode="freedraw",
        # key="set_canvas",
    )


@show_execution_time(debug_mode=DEBUG_MODE)
def def_cal_pts(sign_fig: int = 0) -> List[Tuple[float, float]]:
    cal_pts = list()
    for point in ["origin", "axis"]:
        # st.write(f"###### {point.title()} absolute coordinates")
        cola, colb = st.columns(2)
        with cola:
            x = st.number_input(
                f"X absolute {point}",
                format=f"%0.{sign_fig}f",
                on_change=lambda: reset_cal(),
            )
        with colb:
            y = st.number_input(
                f"Y absolute {point}",
                format=f"%0.{sign_fig}f",
                on_change=lambda: reset_cal(),
            )
        cal_pts.append((x, y))
    return cal_pts


@show_execution_time(debug_mode=DEBUG_MODE)
def main():
    # Variable initialisation
    stss = st.session_state
    # Columns creation
    col1, col2, col2_w = create_columns(col2_ratio=0.7)

    with col2:
        st.subheader("Graph", divider="rainbow")
    with col1:
        ## File upload ##
        st.subheader("Upload", divider="rainbow")
        uploaded_file = st.file_uploader(
            "Upload a graph to digitize",
            type=["png", "jpg", "jpeg"],
            label_visibility="collapsed",
        )
        if uploaded_file:
            with col2:

                image = load_n_resize_image(uploaded_file, col2_w)
                cv_res = update_canva(image).json_data

            ## Calibration ##
            st.subheader("Calibration", divider="rainbow")
            # check if the canva needs to be reseted
            reset_cal(cv_res)

            # Show the relative calibration points to be filled by the user
            sign_fig = st.slider(
                "Number of significant digits",
                min_value=0,
                max_value=5,
                value=0,
                step=1,
            )
            rel_origin, rel_axis = def_cal_pts(sign_fig)

            if not stss.get("cal_OK"):
                points = cv_res["objects"][:3] if cv_res is not None else []
                if len(points) == 3:
                    if None in (rel_origin + rel_axis):
                        st.error("At least one calibration point is not filled")
                    else:
                        stss["abs_origin"], stss["pxl"] = do_cal(points)
                        if any(pxl for pxl in stss["pxl"]) == 0:
                            st.error(
                                "Please select point on X-axis and Y-axis different from origin"
                            )
                        else:
                            stss["cal_OK"] = True
                            st.success("Calibration completed.")
                elif len(points) < 3:
                    st.warning("""
                            Please selsect in this order:
                            - The origin of the graph
                            - A point on the X-axis
                            - A point on the Y-axis
                            """)
            if stss.get("cal_OK"):
                ## Curve point ##
                st.subheader("Curve points", divider="rainbow")
                abs_origin, pxl = stss["abs_origin"], stss["pxl"]
                data_points = [
                    (point["left"], point["top"]) for point in cv_res["objects"][3:]
                ]
                if data_points == []:
                    st.write("#### Select curve points on graph")
                else:
                    calibrated_points = defaultdict(Tuple[float, float])
                    for idx, point in enumerate(data_points):
                        real_x = (
                            rel_origin[0]
                            + (rel_axis[0] - rel_origin[0])
                            * (point[0] - abs_origin[0])
                            / pxl[0]
                        )
                        real_y = (
                            rel_origin[1]
                            + (rel_axis[1] - rel_origin[1])
                            * (abs_origin[1] - point[1])
                            / pxl[1]
                        )
                        calibrated_points[f"Pt {idx + 1}"] = real_x, real_y

                    df = pd.DataFrame(calibrated_points, index=["X", "Y"])

                    df_styled = df.style.format(
                        f"{{:.{sign_fig}f}}",
                        subset=df.select_dtypes(include="number").columns,
                    )

                    st.dataframe(df_styled, use_container_width=True)
                    if st.button("Export data"):
                        st.write("")
        else:

            reset_cal()
            with col2:
                st.warning("Please upload a graph to be digitised")


if __name__ == "__main__":
    init_page()
    main()
