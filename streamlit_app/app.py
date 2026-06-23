from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib.patches import Circle


# =============================================================================
# PROJECT PATHS
# =============================================================================

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
ASSETS_DIR = PROJECT_ROOT / "assets"
DOCS_DIR = PROJECT_ROOT / "docs"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from chain_drive_geometry_calculator import (  # noqa: E402
    ASA_CHAIN_CATALOG,
    exact_continuous_link_count,
    get_chain_data,
    get_sprocket_teeth_options,
    minimum_center_distance_by_outer_diameter,
    pitch_radius,
    round_half_up,
    solve_symmetric_polygonal_center_distance,
    sprocket_outer_diameter_max,
)


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Chain Drive Geometry Calculator",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# CONSTANTS
# =============================================================================

GITHUB_REPOSITORY_URL = "https://github.com/douglasdschons/chain-drive-geometry-calculator"
AUTHOR_GITHUB_URL = "https://github.com/douglasdschons"
DOCUMENTATION_PDF_PATH = DOCS_DIR / "complete_mathematical_formulation_en.pdf"
PRESENTATION_IMAGE_PATH = ASSETS_DIR / "instructions.png"
CHAIN_DIMENSION_IMAGE_PATH = ASSETS_DIR / "enco_asa_dimensions.png"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_available_chain_sizes() -> list[str]:
    """Return ASA chain sizes that have available sprocket tooth options."""
    available_sizes = []

    for row in ASA_CHAIN_CATALOG:
        asa_size = row["asa_size"]

        try:
            get_sprocket_teeth_options(asa_size)
        except ValueError:
            continue

        available_sizes.append(asa_size)

    return available_sizes


def create_polygonal_layout_figure(result: dict, chain_data: dict) -> plt.Figure:
    """Create a Matplotlib figure for the polygonal roller-center layout."""
    points = result["points"]
    closed_points = np.vstack([points, points[0]])

    pitch_mm = float(result["pitch_mm"])
    z1 = int(result["z1"])
    z2 = int(result["z2"])
    center_distance = float(result["real_center_distance_mm"])

    radius_1 = pitch_radius(pitch_mm, z1)
    radius_2 = pitch_radius(pitch_mm, z2)

    pitch_diameter_1 = 2.0 * radius_1
    pitch_diameter_2 = 2.0 * radius_2

    fig, ax = plt.subplots(figsize=(11, 6))

    ax.plot(
        closed_points[:, 0],
        closed_points[:, 1],
        "-o",
        linewidth=1.6,
        markersize=5,
        label="Polygon of roller centers",
    )

    ax.add_patch(
        Circle(
            (0.0, 0.0),
            radius_1,
            fill=False,
            linestyle="--",
            label=f"Pitch circle 1 (Øp1 = {pitch_diameter_1:.2f} mm)",
        )
    )

    ax.add_patch(
        Circle(
            (center_distance, 0.0),
            radius_2,
            fill=False,
            linestyle="--",
            label=f"Pitch circle 2 (Øp2 = {pitch_diameter_2:.2f} mm)",
        )
    )

    ax.scatter(
        [0.0, center_distance],
        [0.0, 0.0],
        marker="x",
        s=90,
        label="Sprocket centers",
    )

    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.3)
    ax.set_xlabel("x [mm]")
    ax.set_ylabel("y [mm]")
    ax.set_title(
        f"ASA {chain_data['asa_size']} | "
        f"z1={result['z1']}, z2={result['z2']} | "
        f"C={center_distance:.2f} mm | N={result['selected_links']}"
    )
    ax.legend(loc="best")

    fig.tight_layout()
    return fig


def render_project_links() -> None:
    """Render the project links block at the bottom of the app."""
    st.divider()
    st.subheader("Project links")

    col_1, col_2, col_3 = st.columns(3)

    with col_1:
        st.link_button("GitHub repository", GITHUB_REPOSITORY_URL, use_container_width=True)

    with col_2:
        if DOCUMENTATION_PDF_PATH.exists():
            st.link_button(
                "Mathematical formulation PDF",
                f"{GITHUB_REPOSITORY_URL}/blob/main/docs/complete_mathematical_formulation_en.pdf",
                use_container_width=True,
            )
        else:
            st.button("Mathematical formulation PDF", disabled=True, use_container_width=True)

    with col_3:
        st.link_button("Author GitHub", AUTHOR_GITHUB_URL, use_container_width=True)

    st.caption(
        "Developed by Douglas Delorenzi Schons. "
        "This app is a CAD-oriented geometric calculator for ASA roller chain drives."
    )


def render_chain_data_table(chain_data: dict) -> None:
    """Render selected chain catalog dimensions."""
    rows = [
        {"Property": "ASA size", "Value": f"ASA {chain_data['asa_size']}"},
        {"Property": "Pitch", "Value": f"{chain_data['pitch_mm']:.3f} mm"},
        {"Property": "Inner width E", "Value": f"{chain_data['inner_width_E_mm']:.3f} mm"},
        {"Property": "Roller diameter R", "Value": f"{chain_data['roller_diameter_R_mm']:.3f} mm"},
        {"Property": "Plate height H", "Value": f"{chain_data['plate_height_H_mm']:.3f} mm"},
        {"Property": "Pin diameter G", "Value": f"{chain_data['pin_diameter_G_mm']:.3f} mm"},
        {"Property": "Overall width L", "Value": f"{chain_data['overall_width_L_mm']:.3f} mm"},
        {"Property": "Plate thickness T", "Value": f"{chain_data['plate_thickness_T_mm']:.3f} mm"},
        {"Property": "Breaking load", "Value": f"{chain_data['breaking_load_kgf']:.0f} kgf"},
        {"Property": "Weight", "Value": f"{chain_data['weight_kg_per_m']:.3f} kg/m"},
    ]

    st.table(rows)


# =============================================================================
# SIDEBAR INPUTS
# =============================================================================

available_chain_sizes = get_available_chain_sizes()

with st.sidebar:
    st.header("Input data")

    selected_chain_size = st.selectbox(
        "ASA chain size",
        options=available_chain_sizes,
        index=available_chain_sizes.index("80") if "80" in available_chain_sizes else 0,
    )

    chain_data = get_chain_data(selected_chain_size)
    pitch_mm = float(chain_data["pitch_mm"])
    roller_diameter_mm = float(chain_data["roller_diameter_R_mm"])

    tooth_options = get_sprocket_teeth_options(selected_chain_size)

    default_z1 = 11 if 11 in tooth_options else tooth_options[0]
    default_z2 = 20 if 20 in tooth_options else tooth_options[min(len(tooth_options) - 1, 5)]

    z1 = st.selectbox(
        "Smaller sprocket teeth z1",
        options=tooth_options,
        index=tooth_options.index(default_z1),
    )

    z2_options = [value for value in tooth_options if value >= z1]
    z2 = st.selectbox(
        "Larger sprocket teeth z2",
        options=z2_options,
        index=z2_options.index(default_z2) if default_z2 in z2_options else 0,
    )

    minimum_center_distance_mm = minimum_center_distance_by_outer_diameter(
        pitch_mm=pitch_mm,
        roller_diameter_mm=roller_diameter_mm,
        z1=z1,
        z2=z2,
        clearance_mm=5.0,
    )

    default_center_distance = max(
        minimum_center_distance_mm + 20.0,
        8.0 * pitch_mm,
    )

    desired_center_distance_mm = st.number_input(
        "Desired center distance [mm]",
        min_value=float(round(minimum_center_distance_mm, 3)),
        value=float(round(default_center_distance, 3)),
        step=1.0,
        format="%.3f",
    )

    continuous_links = exact_continuous_link_count(
        pitch_mm=pitch_mm,
        z1=z1,
        z2=z2,
        center_distance_mm=desired_center_distance_mm,
    )

    automatically_round_links = st.checkbox(
        "Automatically round link count",
        value=True,
    )

    rounded_links = round_half_up(continuous_links)

    if automatically_round_links:
        selected_links = rounded_links
        st.caption(f"Selected link count: {selected_links}")
    else:
        selected_links = st.number_input(
            "Manual link count",
            min_value=3,
            value=int(rounded_links),
            step=1,
        )

    run_calculation = st.button(
        "Calculate geometry",
        type="primary",
        use_container_width=True,
    )


# =============================================================================
# MAIN PAGE
# =============================================================================

st.title("Chain Drive Geometry Calculator")
st.caption("Discrete polygonal roller-center model for ASA roller chain drives")

if PRESENTATION_IMAGE_PATH.exists():
    st.image(
        str(PRESENTATION_IMAGE_PATH),
        caption="Chain drive geometric model",
        use_container_width=True,
    )
else:
    st.info(
        "Presentation image not found. "
        "Add `assets/chain_drive_presentation.png` to display a project image here."
    )

st.markdown(
    """
This app calculates the geometric layout of an ASA roller chain drive using a
discrete polygonal roller-center model. The final geometry is based on an integer
number of chain links and a valid contact topology around the sprockets.
"""
)

summary_col_1, summary_col_2, summary_col_3 = st.columns(3)
summary_col_1.metric("Selected chain", f"ASA {chain_data['asa_size']}")
summary_col_2.metric("Pitch", f"{pitch_mm:.3f} mm")
summary_col_3.metric("Minimum center distance", f"{minimum_center_distance_mm:.2f} mm")

st.divider()

try:
    result = solve_symmetric_polygonal_center_distance(
        pitch_mm=pitch_mm,
        z1=int(z1),
        z2=int(z2),
        desired_center_distance_mm=float(desired_center_distance_mm),
        selected_links=int(selected_links),
    )

except Exception as error:
    st.error(f"Calculation failed: {error}")
    st.stop()


topology = result["topology"]

if run_calculation:
    st.success("Calculation completed.")

result_col_1, result_col_2, result_col_3, result_col_4 = st.columns(4)

result_col_1.metric(
    "Real center distance",
    f"{result['real_center_distance_mm']:.2f} mm",
    delta=f"{result['center_correction_vs_desired_mm']:+.2f} mm",
)

result_col_2.metric(
    "Selected links",
    f"{result['selected_links']}",
    delta="Offset link" if result["offset_link_required"] else "Standard",
)

result_col_3.metric(
    "Topology M1/S/M2/R",
    topology.roller_label(),
)

result_col_4.metric(
    "Valid candidates",
    f"{result['candidate_count']}",
)

tabs = st.tabs(
    [
        "Geometry",
        "Results",
        "Chain dimensions",
        "Documentation",
    ]
)

with tabs[0]:
    st.subheader("Polygonal roller-center layout")
    figure = create_polygonal_layout_figure(result, chain_data)
    st.pyplot(figure)
    plt.close(figure)

with tabs[1]:
    st.subheader("Calculation results")

    results_table = [
        {"Parameter": "Desired center distance", "Value": f"{result['desired_center_distance_mm']:.6f} mm"},
        {"Parameter": "Reference continuous center distance", "Value": f"{result['reference_center_distance_mm']:.6f} mm"},
        {"Parameter": "Real center distance", "Value": f"{result['real_center_distance_mm']:.6f} mm"},
        {"Parameter": "Center correction vs desired", "Value": f"{result['center_correction_vs_desired_mm']:+.6f} mm"},
        {"Parameter": "Center correction vs reference", "Value": f"{result['center_correction_vs_reference_mm']:+.6f} mm"},
        {"Parameter": "Continuous link estimate", "Value": f"{continuous_links:.6f}"},
        {"Parameter": "Selected link count", "Value": f"{result['selected_links']}"},
        {"Parameter": "Offset link required", "Value": "Yes" if result["offset_link_required"] else "No"},
        {"Parameter": "Small sprocket pitch diameter", "Value": f"{result['small_pitch_diameter_mm']:.6f} mm"},
        {"Parameter": "Large sprocket pitch diameter", "Value": f"{result['large_pitch_diameter_mm']:.6f} mm"},
        {"Parameter": "Chain length", "Value": f"{result['chain_length_mm']:.6f} mm"},
        {"Parameter": "Topology by contact rollers", "Value": topology.roller_label()},
        {"Parameter": "Topology by pitch intervals", "Value": topology.interval_label()},
        {"Parameter": "Maximum pitch error", "Value": f"{result['max_edge_error_mm']:.3e} mm"},
        {"Parameter": "Mean pitch error", "Value": f"{result['mean_edge_error_mm']:.3e} mm"},
        {"Parameter": "Self-intersections", "Value": f"{result['self_intersections']}"},
    ]

    st.table(results_table)

with tabs[2]:
    st.subheader("Selected chain dimensions")
    render_chain_data_table(chain_data)

    if CHAIN_DIMENSION_IMAGE_PATH.exists():
        st.image(
            str(CHAIN_DIMENSION_IMAGE_PATH),
            caption="ASA roller chain dimension reference",
            use_container_width=True,
        )
    else:
        st.warning("Chain dimension image not found at `assets/enco_asa_dimensions.png`.")

with tabs[3]:
    st.subheader("Technical documentation")

    st.markdown(
        """
The complete mathematical formulation is included in the repository under:

```text
docs/complete_mathematical_formulation_en.pdf
docs/complete_mathematical_formulation_en.tex
```

The documentation covers the continuous reference formulation, the discrete
polygonal model, the topology equation, CAD validation, limitations, and
future development.
"""
    )

    if DOCUMENTATION_PDF_PATH.exists():
        with open(DOCUMENTATION_PDF_PATH, "rb") as pdf_file:
            st.download_button(
                label="Download mathematical formulation PDF",
                data=pdf_file,
                file_name="complete_mathematical_formulation_en.pdf",
                mime="application/pdf",
            )
    else:
        st.warning("Documentation PDF not found in the local repository.")

render_project_links()
