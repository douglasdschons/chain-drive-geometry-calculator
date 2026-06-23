from __future__ import annotations

from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, Optional
import csv
import math

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib.patches import Circle
from scipy.optimize import brentq


# =============================================================================
# PROJECT PATHS
# =============================================================================

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
DOCS_DIR = PROJECT_ROOT / "docs"
FIGURES_DIR = DOCS_DIR / "figures"


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

GITHUB_REPOSITORY_URL = (
    "https://github.com/douglasdschons/chain-drive-geometry-calculator"
)
AUTHOR_LINKEDIN_URL = "https://www.linkedin.com/in/douglasdschons"
DOCUMENTATION_PDF_PATH = DOCS_DIR / "complete_mathematical_formulation_en.pdf"
CHAIN_DIMENSION_IMAGE_PATH = ASSETS_DIR / "enco_asa_dimensions.png"

PRESENTATION_IMAGE_CANDIDATES = [
    ASSETS_DIR / "instructions.png",
    FIGURES_DIR / "instructions.png",
]


# =============================================================================
# ASA CATALOG
# =============================================================================

ASA_CHAIN_CATALOG = [
    {
        "asa_size": "25",
        "pitch_text": "1/4 in",
        "pitch_mm": 6.35,
        "inner_width_E_mm": 3.18,
        "roller_diameter_R_mm": 3.30,
        "plate_height_H_mm": 6.00,
        "pin_diameter_G_mm": 2.31,
        "overall_width_L_mm": 7.90,
        "plate_thickness_T_mm": 0.80,
        "breaking_load_kgf": 350,
        "weight_kg_per_m": 0.15,
    },
    {
        "asa_size": "35",
        "pitch_text": "3/8 in",
        "pitch_mm": 9.53,
        "inner_width_E_mm": 4.77,
        "roller_diameter_R_mm": 5.08,
        "plate_height_H_mm": 8.70,
        "pin_diameter_G_mm": 3.58,
        "overall_width_L_mm": 12.30,
        "plate_thickness_T_mm": 1.30,
        "breaking_load_kgf": 790,
        "weight_kg_per_m": 0.33,
    },
    {
        "asa_size": "41",
        "pitch_text": "1/2 in",
        "pitch_mm": 12.70,
        "inner_width_E_mm": 6.25,
        "roller_diameter_R_mm": 7.77,
        "plate_height_H_mm": 9.91,
        "pin_diameter_G_mm": 3.58,
        "overall_width_L_mm": 13.75,
        "plate_thickness_T_mm": 1.30,
        "breaking_load_kgf": 1284,
        "weight_kg_per_m": 0.41,
    },
    {
        "asa_size": "40",
        "pitch_text": "1/2 in",
        "pitch_mm": 12.70,
        "inner_width_E_mm": 7.85,
        "roller_diameter_R_mm": 7.95,
        "plate_height_H_mm": 12.00,
        "pin_diameter_G_mm": 3.96,
        "overall_width_L_mm": 16.60,
        "plate_thickness_T_mm": 1.50,
        "breaking_load_kgf": 1410,
        "weight_kg_per_m": 0.62,
    },
    {
        "asa_size": "50",
        "pitch_text": "5/8 in",
        "pitch_mm": 15.87,
        "inner_width_E_mm": 9.40,
        "roller_diameter_R_mm": 10.16,
        "plate_height_H_mm": 15.09,
        "pin_diameter_G_mm": 5.08,
        "overall_width_L_mm": 20.70,
        "plate_thickness_T_mm": 2.03,
        "breaking_load_kgf": 2220,
        "weight_kg_per_m": 1.02,
    },
    {
        "asa_size": "60",
        "pitch_text": "3/4 in",
        "pitch_mm": 19.05,
        "inner_width_E_mm": 12.57,
        "roller_diameter_R_mm": 11.91,
        "plate_height_H_mm": 18.00,
        "pin_diameter_G_mm": 5.94,
        "overall_width_L_mm": 25.90,
        "plate_thickness_T_mm": 2.42,
        "breaking_load_kgf": 3180,
        "weight_kg_per_m": 1.50,
    },
    {
        "asa_size": "80",
        "pitch_text": "1 in",
        "pitch_mm": 25.40,
        "inner_width_E_mm": 15.75,
        "roller_diameter_R_mm": 15.88,
        "plate_height_H_mm": 24.00,
        "pin_diameter_G_mm": 7.92,
        "overall_width_L_mm": 32.70,
        "plate_thickness_T_mm": 3.25,
        "breaking_load_kgf": 5670,
        "weight_kg_per_m": 2.60,
    },
    {
        "asa_size": "100",
        "pitch_text": "1-1/4 in",
        "pitch_mm": 31.75,
        "inner_width_E_mm": 18.90,
        "roller_diameter_R_mm": 19.05,
        "plate_height_H_mm": 30.00,
        "pin_diameter_G_mm": 9.53,
        "overall_width_L_mm": 40.40,
        "plate_thickness_T_mm": 4.00,
        "breaking_load_kgf": 8850,
        "weight_kg_per_m": 3.91,
    },
    {
        "asa_size": "120",
        "pitch_text": "1-1/2 in",
        "pitch_mm": 38.10,
        "inner_width_E_mm": 25.22,
        "roller_diameter_R_mm": 22.23,
        "plate_height_H_mm": 35.70,
        "pin_diameter_G_mm": 11.10,
        "overall_width_L_mm": 50.30,
        "plate_thickness_T_mm": 4.80,
        "breaking_load_kgf": 12700,
        "weight_kg_per_m": 5.62,
    },
    {
        "asa_size": "140",
        "pitch_text": "1-3/4 in",
        "pitch_mm": 44.45,
        "inner_width_E_mm": 25.22,
        "roller_diameter_R_mm": 25.40,
        "plate_height_H_mm": 41.00,
        "pin_diameter_G_mm": 12.70,
        "overall_width_L_mm": 54.40,
        "plate_thickness_T_mm": 5.60,
        "breaking_load_kgf": 17240,
        "weight_kg_per_m": 7.70,
    },
    {
        "asa_size": "160",
        "pitch_text": "2 in",
        "pitch_mm": 50.80,
        "inner_width_E_mm": 31.55,
        "roller_diameter_R_mm": 28.58,
        "plate_height_H_mm": 47.80,
        "pin_diameter_G_mm": 14.27,
        "overall_width_L_mm": 64.80,
        "plate_thickness_T_mm": 6.40,
        "breaking_load_kgf": 22680,
        "weight_kg_per_m": 10.10,
    },
    {
        "asa_size": "180",
        "pitch_text": "2-1/4 in",
        "pitch_mm": 57.15,
        "inner_width_E_mm": 35.50,
        "roller_diameter_R_mm": 35.71,
        "plate_height_H_mm": 53.60,
        "pin_diameter_G_mm": 17.46,
        "overall_width_L_mm": 72.80,
        "plate_thickness_T_mm": 7.20,
        "breaking_load_kgf": 34000,
        "weight_kg_per_m": 13.50,
    },
    {
        "asa_size": "200",
        "pitch_text": "2-1/2 in",
        "pitch_mm": 63.50,
        "inner_width_E_mm": 37.85,
        "roller_diameter_R_mm": 39.68,
        "plate_height_H_mm": 60.00,
        "pin_diameter_G_mm": 19.85,
        "overall_width_L_mm": 80.30,
        "plate_thickness_T_mm": 8.00,
        "breaking_load_kgf": 35380,
        "weight_kg_per_m": 16.15,
    },
    {
        "asa_size": "240",
        "pitch_text": "3 in",
        "pitch_mm": 76.20,
        "inner_width_E_mm": 47.35,
        "roller_diameter_R_mm": 47.63,
        "plate_height_H_mm": 72.39,
        "pin_diameter_G_mm": 23.81,
        "overall_width_L_mm": 95.50,
        "plate_thickness_T_mm": 9.50,
        "breaking_load_kgf": 51030,
        "weight_kg_per_m": 23.20,
    },
]


# =============================================================================
# ENCO SPROCKET TEETH OPTIONS
# =============================================================================

SPROCKET_TEETH_OPTIONS_CSV = """35-80;100;120;140;160
9;11;11;11;11
10;12;12;12;12
11;13;13;13;13
12;14;14;14;14
13;15;15;15;15
14;16;16;16;16
15;17;17;17;17
16;18;18;18;18
17;19;19;19;19
18;20;20;20;20
19;21;21;21;21
20;22;22;22;22
21;23;23;23;23
22;24;24;24;24
23;25;25;25;25
24;28;28;30;30
25;30;30;35;35
26;35;35;38;38
27;38;38;40;40
28;40;40;45;45
30;45;45;48;57
35;48;48;54;76
38;54;54;57;95
40;57;57;76;114
45;76;60;95;
48;;76;114;
54;;95;;
57;;114;;
60;;;;
76;;;;
95;;;;
;;;;
"""

SPROCKET_TEETH_GROUPS = {
    "35-80": {"35", "40", "41", "50", "60", "80"},
    "100": {"100"},
    "120": {"120"},
    "140": {"140"},
    "160": {"160"},
}


def parse_sprocket_teeth_options() -> dict[str, list[int]]:
    reader = csv.DictReader(StringIO(SPROCKET_TEETH_OPTIONS_CSV), delimiter=";")

    if reader.fieldnames is None:
        raise ValueError("Invalid ENCO sprocket tooth table.")

    group_options: dict[str, list[int]] = {
        group_name: []
        for group_name in reader.fieldnames
    }

    for row in reader:
        for group_name, raw_value in row.items():
            value_text = (raw_value or "").strip()
            if value_text:
                group_options[group_name].append(int(value_text))

    options_by_asa_size: dict[str, list[int]] = {}

    for group_name, asa_sizes in SPROCKET_TEETH_GROUPS.items():
        options = sorted(set(group_options.get(group_name, [])))
        for asa_size in asa_sizes:
            options_by_asa_size[asa_size] = options

    return options_by_asa_size


SPROCKET_TEETH_OPTIONS_BY_ASA_SIZE = parse_sprocket_teeth_options()


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass(frozen=True)
class ChainInput:
    pitch: float
    small_teeth: int
    large_teeth: int
    selected_links: int
    desired_center_distance: float


@dataclass(frozen=True)
class SolverConfig:
    contact_roller_span: int = 4
    run_span: int = 5
    tolerance: float = 1e-7
    max_pitch_error: float = 1e-6


@dataclass(frozen=True)
class SymmetricTopology:
    small_contact_rollers: int
    upper_run_intervals: int
    large_contact_rollers: int
    lower_run_intervals: int

    @property
    def small_arc_intervals(self) -> int:
        return self.small_contact_rollers - 1

    @property
    def large_arc_intervals(self) -> int:
        return self.large_contact_rollers - 1

    def interval_label(self) -> str:
        return (
            f"{self.small_arc_intervals}/"
            f"{self.upper_run_intervals}/"
            f"{self.large_arc_intervals}/"
            f"{self.lower_run_intervals}"
        )

    def roller_label(self) -> str:
        return (
            f"{self.small_contact_rollers}/"
            f"{self.upper_run_intervals}/"
            f"{self.large_contact_rollers}/"
            f"{self.lower_run_intervals}"
        )


@dataclass
class ChainSolution:
    center_distance: float
    topology: SymmetricTopology
    points: np.ndarray
    small_top_angle_rad: float
    small_bottom_angle_rad: float
    large_top_angle_rad: float
    large_bottom_angle_rad: float
    center_reference: float
    continuous_estimates: tuple[float, float, float]
    topology_error: float
    max_link_error: float
    mean_link_error: float
    self_intersections: int

    @property
    def large_phase_angle_rad(self) -> float:
        return self.large_top_angle_rad

    @property
    def large_phase_angle_deg(self) -> float:
        return math.degrees(self.large_phase_angle_rad)

    @property
    def center_reference_error(self) -> float:
        return self.center_distance - self.center_reference


# =============================================================================
# BASIC CATALOG AND GEOMETRY HELPERS
# =============================================================================

def normalize_chain_size(chain_size: str) -> str:
    normalized = str(chain_size).upper().strip()

    for token in ["ASA", "RS", "#", " ", "-", "_"]:
        normalized = normalized.replace(token, "")

    if normalized.startswith("A"):
        normalized = normalized[1:]

    return normalized


def get_chain_data(chain_size: str) -> dict[str, Any]:
    normalized = normalize_chain_size(chain_size)

    for row in ASA_CHAIN_CATALOG:
        if row["asa_size"] == normalized:
            return row

    available = " | ".join(row["asa_size"] for row in ASA_CHAIN_CATALOG)
    raise ValueError(
        f"ASA chain size {chain_size} was not found. Available options: {available}"
    )


def get_sprocket_teeth_options(chain_size: str) -> list[int]:
    normalized = normalize_chain_size(chain_size)

    if normalized not in SPROCKET_TEETH_OPTIONS_BY_ASA_SIZE:
        available = " | ".join(sorted(SPROCKET_TEETH_OPTIONS_BY_ASA_SIZE))
        raise ValueError(
            f"No sprocket tooth table is available for ASA {chain_size}. "
            f"Available chain sizes with tooth tables: {available}"
        )

    return SPROCKET_TEETH_OPTIONS_BY_ASA_SIZE[normalized]


def get_available_chain_sizes() -> list[str]:
    available_sizes = []

    for row in ASA_CHAIN_CATALOG:
        asa_size = row["asa_size"]
        if asa_size in SPROCKET_TEETH_OPTIONS_BY_ASA_SIZE:
            available_sizes.append(asa_size)

    return available_sizes


def round_half_up(value: float) -> int:
    return int(math.floor(value + 0.5))


def pitch_radius(pitch: float, teeth: int) -> float:
    return pitch / (2.0 * math.sin(math.pi / teeth))


def pitch_diameter(pitch_mm: float, teeth: int) -> float:
    if teeth <= 2:
        raise ValueError("The number of teeth must be greater than 2.")

    return pitch_mm / math.sin(math.pi / teeth)


def sprocket_outer_diameter_max(
    pitch_mm: float,
    roller_diameter_mm: float,
    teeth: int,
) -> float:
    nominal_diameter_mm = pitch_diameter(pitch_mm, teeth)
    return nominal_diameter_mm + 1.25 * pitch_mm - roller_diameter_mm


def minimum_center_distance_by_outer_diameter(
    pitch_mm: float,
    roller_diameter_mm: float,
    z1: int,
    z2: int,
    clearance_mm: float = 5.0,
) -> float:
    outer_diameter_1 = sprocket_outer_diameter_max(
        pitch_mm=pitch_mm,
        roller_diameter_mm=roller_diameter_mm,
        teeth=z1,
    )
    outer_diameter_2 = sprocket_outer_diameter_max(
        pitch_mm=pitch_mm,
        roller_diameter_mm=roller_diameter_mm,
        teeth=z2,
    )

    return 0.5 * (outer_diameter_1 + outer_diameter_2) + clearance_mm


def point_on_circle(center: np.ndarray, radius: float, angle_rad: float) -> np.ndarray:
    return center + radius * np.array(
        [math.cos(angle_rad), math.sin(angle_rad)],
        dtype=float,
    )


def exact_continuous_chain_length(
    pitch_mm: float,
    z1: int,
    z2: int,
    center_distance_mm: float,
) -> float:
    r1 = pitch_radius(pitch_mm, z1)
    r2 = pitch_radius(pitch_mm, z2)
    radius_delta = r2 - r1

    if center_distance_mm <= abs(radius_delta):
        raise ValueError("Invalid center distance for sprocket geometry.")

    alpha = math.asin(radius_delta / center_distance_mm)
    tangent_length = math.sqrt(center_distance_mm**2 - radius_delta**2)

    small_contact_angle = math.pi - 2.0 * alpha
    large_contact_angle = math.pi + 2.0 * alpha

    return (
        r1 * small_contact_angle
        + r2 * large_contact_angle
        + 2.0 * tangent_length
    )


def exact_continuous_link_count(
    pitch_mm: float,
    z1: int,
    z2: int,
    center_distance_mm: float,
) -> float:
    return exact_continuous_chain_length(
        pitch_mm=pitch_mm,
        z1=z1,
        z2=z2,
        center_distance_mm=center_distance_mm,
    ) / pitch_mm


def continuous_center_distance_for_links(
    pitch_mm: float,
    z1: int,
    z2: int,
    selected_links: int,
    desired_center_distance_mm: float,
) -> float:
    target_length = selected_links * pitch_mm
    r1 = pitch_radius(pitch_mm, z1)
    r2 = pitch_radius(pitch_mm, z2)

    lower = abs(r2 - r1) + 1e-6
    upper = max(
        desired_center_distance_mm * 2.0,
        target_length,
        r1 + r2 + pitch_mm,
    )

    def residual(center_distance_mm: float) -> float:
        return exact_continuous_chain_length(
            pitch_mm=pitch_mm,
            z1=z1,
            z2=z2,
            center_distance_mm=center_distance_mm,
        ) - target_length

    while residual(upper) < 0.0:
        upper *= 2.0

    return float(brentq(residual, lower, upper, xtol=1e-12))


def continuous_topology_estimates(
    pitch_mm: float,
    z1: int,
    z2: int,
    center_distance_mm: float,
) -> tuple[float, float, float]:
    r1 = pitch_radius(pitch_mm, z1)
    r2 = pitch_radius(pitch_mm, z2)
    delta1 = 2.0 * math.pi / z1
    delta2 = 2.0 * math.pi / z2
    radius_delta = r2 - r1

    alpha = math.asin(radius_delta / center_distance_mm)
    tangent_length = math.sqrt(center_distance_mm**2 - radius_delta**2)

    small_contact_angle = math.pi - 2.0 * alpha
    large_contact_angle = math.pi + 2.0 * alpha

    small_arc_intervals_estimate = small_contact_angle / delta1
    large_arc_intervals_estimate = large_contact_angle / delta2
    straight_run_intervals_estimate = tangent_length / pitch_mm

    return (
        small_arc_intervals_estimate,
        large_arc_intervals_estimate,
        straight_run_intervals_estimate,
    )


# =============================================================================
# SELF-INTERSECTION CHECK
# =============================================================================

def orientation(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    return float(
        (b[0] - a[0]) * (c[1] - a[1])
        - (b[1] - a[1]) * (c[0] - a[0])
    )


def on_segment(
    a: np.ndarray,
    b: np.ndarray,
    c: np.ndarray,
    tolerance: float = 1e-9,
) -> bool:
    return (
        min(a[0], c[0]) - tolerance <= b[0] <= max(a[0], c[0]) + tolerance
        and min(a[1], c[1]) - tolerance <= b[1] <= max(a[1], c[1]) + tolerance
    )


def segments_intersect(
    a: np.ndarray,
    b: np.ndarray,
    c: np.ndarray,
    d: np.ndarray,
    tolerance: float = 1e-9,
) -> bool:
    o1 = orientation(a, b, c)
    o2 = orientation(a, b, d)
    o3 = orientation(c, d, a)
    o4 = orientation(c, d, b)

    if o1 * o2 < -tolerance and o3 * o4 < -tolerance:
        return True

    if abs(o1) <= tolerance and on_segment(a, c, b, tolerance):
        return True

    if abs(o2) <= tolerance and on_segment(a, d, b, tolerance):
        return True

    if abs(o3) <= tolerance and on_segment(c, a, d, tolerance):
        return True

    if abs(o4) <= tolerance and on_segment(c, b, d, tolerance):
        return True

    return False


def count_self_intersections(points: np.ndarray) -> int:
    n = len(points)
    intersections = 0

    for i in range(n):
        a = points[i]
        b = points[(i + 1) % n]

        for j in range(i + 1, n):
            if abs(i - j) <= 1:
                continue

            if i == 0 and j == n - 1:
                continue

            c = points[j]
            d = points[(j + 1) % n]

            if segments_intersect(a, b, c, d):
                intersections += 1

    return intersections


# =============================================================================
# SYMMETRIC POLYGONAL SOLVER
# =============================================================================

class SymmetricPolygonalChainSolver:
    """Symmetric polygonal chain solver for ASA roller chain drives."""

    def __init__(self, data: ChainInput, config: SolverConfig = SolverConfig()):
        self.data = data
        self.config = config

        self.pitch = data.pitch
        self.z1 = data.small_teeth
        self.z2 = data.large_teeth
        self.N = data.selected_links
        self.C_desired = data.desired_center_distance

        self.r1 = pitch_radius(self.pitch, self.z1)
        self.r2 = pitch_radius(self.pitch, self.z2)

        self.delta1 = 2.0 * math.pi / self.z1
        self.delta2 = 2.0 * math.pi / self.z2

        self.O1 = np.array([0.0, 0.0], dtype=float)

        self.C_reference = continuous_center_distance_for_links(
            pitch_mm=self.pitch,
            z1=self.z1,
            z2=self.z2,
            selected_links=self.N,
            desired_center_distance_mm=self.C_desired,
        )

        self.estimates = continuous_topology_estimates(
            pitch_mm=self.pitch,
            z1=self.z1,
            z2=self.z2,
            center_distance_mm=self.C_reference,
        )

    def contact_angles(
        self,
        topology: SymmetricTopology,
    ) -> tuple[float, float, float, float]:
        q1 = (topology.small_contact_rollers - 1) / 2.0
        q2 = (topology.large_contact_rollers - 1) / 2.0

        small_top_angle = math.pi - q1 * self.delta1
        small_bottom_angle = math.pi + q1 * self.delta1

        large_top_angle = q2 * self.delta2
        large_bottom_angle = -q2 * self.delta2

        return (
            small_top_angle,
            small_bottom_angle,
            large_top_angle,
            large_bottom_angle,
        )

    def generate_topologies(self) -> list[SymmetricTopology]:
        small_arc_estimate, large_arc_estimate, run_estimate = self.estimates

        small_centers = {
            round_half_up(small_arc_estimate),
            round_half_up(small_arc_estimate + 1.0),
        }
        large_centers = {
            round_half_up(large_arc_estimate),
            round_half_up(large_arc_estimate + 1.0),
        }

        small_candidates: set[int] = set()
        large_candidates: set[int] = set()

        for center in small_centers:
            for M1 in range(
                center - self.config.contact_roller_span,
                center + self.config.contact_roller_span + 1,
            ):
                if 2 <= M1 <= self.z1 + 1:
                    small_candidates.add(M1)

        for center in large_centers:
            for M2 in range(
                center - self.config.contact_roller_span,
                center + self.config.contact_roller_span + 1,
            ):
                if 2 <= M2 <= self.z2 + 1:
                    large_candidates.add(M2)

        topologies: list[SymmetricTopology] = []
        seen: set[tuple[int, int, int, int]] = set()

        for M1 in sorted(small_candidates):
            for M2 in sorted(large_candidates):
                remaining = self.N - (M1 - 1) - (M2 - 1)

                if remaining <= 0 or remaining % 2 != 0:
                    continue

                S = remaining // 2
                R = S

                if S <= 0:
                    continue

                if abs(S - run_estimate) > self.config.run_span:
                    continue

                topology = SymmetricTopology(
                    small_contact_rollers=M1,
                    upper_run_intervals=S,
                    large_contact_rollers=M2,
                    lower_run_intervals=R,
                )

                key = (M1, S, M2, R)
                if key not in seen:
                    seen.add(key)
                    topologies.append(topology)

        return topologies

    def center_distance_from_topology(
        self,
        topology: SymmetricTopology,
    ) -> Optional[float]:
        (
            small_top_angle,
            _small_bottom_angle,
            large_top_angle,
            _large_bottom_angle,
        ) = self.contact_angles(topology)

        A_top = point_on_circle(self.O1, self.r1, small_top_angle)
        target_length = topology.upper_run_intervals * self.pitch

        vertical_difference = self.r2 * math.sin(large_top_angle) - A_top[1]
        radicand = target_length**2 - vertical_difference**2

        if radicand < -self.config.tolerance:
            return None

        horizontal_projection = math.sqrt(max(0.0, radicand))

        center_distance = (
            A_top[0]
            - self.r2 * math.cos(large_top_angle)
            + horizontal_projection
        )

        if center_distance <= abs(self.r2 - self.r1):
            return None

        return float(center_distance)

    def build_points(
        self,
        topology: SymmetricTopology,
        center_distance: float,
    ) -> np.ndarray:
        (
            small_top_angle,
            small_bottom_angle,
            large_top_angle,
            large_bottom_angle,
        ) = self.contact_angles(topology)

        O2 = np.array([center_distance, 0.0], dtype=float)

        A_top = point_on_circle(self.O1, self.r1, small_top_angle)
        A_bottom = point_on_circle(self.O1, self.r1, small_bottom_angle)
        B_top = point_on_circle(O2, self.r2, large_top_angle)
        B_bottom = point_on_circle(O2, self.r2, large_bottom_angle)

        points: list[np.ndarray] = [A_top]

        for step in range(1, topology.upper_run_intervals + 1):
            fraction = step / topology.upper_run_intervals
            points.append(A_top + fraction * (B_top - A_top))

        for step in range(1, topology.large_arc_intervals + 1):
            angle = large_top_angle - step * self.delta2
            points.append(point_on_circle(O2, self.r2, angle))

        for step in range(1, topology.lower_run_intervals + 1):
            fraction = step / topology.lower_run_intervals
            points.append(B_bottom + fraction * (A_bottom - B_bottom))

        for step in range(1, topology.small_arc_intervals):
            angle = small_bottom_angle - step * self.delta1
            points.append(point_on_circle(self.O1, self.r1, angle))

        return np.vstack(points)

    def topology_error(self, topology: SymmetricTopology) -> float:
        small_arc_estimate, large_arc_estimate, run_estimate = self.estimates

        return float(
            abs(topology.small_contact_rollers - small_arc_estimate)
            + abs(topology.large_contact_rollers - large_arc_estimate)
            + abs(topology.upper_run_intervals - run_estimate)
            + abs(topology.lower_run_intervals - run_estimate)
        )

    def build_solution(self, topology: SymmetricTopology) -> Optional[ChainSolution]:
        center_distance = self.center_distance_from_topology(topology)

        if center_distance is None:
            return None

        points = self.build_points(topology, center_distance)

        if len(points) != self.N:
            return None

        closed_points = np.vstack([points, points[0]])
        link_lengths = np.linalg.norm(np.diff(closed_points, axis=0), axis=1)
        link_errors = np.abs(link_lengths - self.pitch)

        max_link_error = float(np.max(link_errors))
        mean_link_error = float(np.mean(link_errors))

        if max_link_error > self.config.max_pitch_error:
            return None

        self_intersections = count_self_intersections(points)

        if self_intersections != 0:
            return None

        (
            small_top_angle,
            small_bottom_angle,
            large_top_angle,
            large_bottom_angle,
        ) = self.contact_angles(topology)

        return ChainSolution(
            center_distance=center_distance,
            topology=topology,
            points=points,
            small_top_angle_rad=small_top_angle,
            small_bottom_angle_rad=small_bottom_angle,
            large_top_angle_rad=large_top_angle,
            large_bottom_angle_rad=large_bottom_angle,
            center_reference=self.C_reference,
            continuous_estimates=self.estimates,
            topology_error=self.topology_error(topology),
            max_link_error=max_link_error,
            mean_link_error=mean_link_error,
            self_intersections=self_intersections,
        )

    def solve(self) -> list[ChainSolution]:
        solutions: list[ChainSolution] = []

        for topology in self.generate_topologies():
            solution = self.build_solution(topology)
            if solution is not None:
                solutions.append(solution)

        solutions.sort(
            key=lambda solution: (
                solution.topology_error,
                abs(solution.center_reference_error),
                abs(solution.center_distance - self.C_desired),
                solution.max_link_error,
            )
        )

        return solutions


# =============================================================================
# PUBLIC SOLVER WRAPPER
# =============================================================================

def solve_symmetric_polygonal_center_distance(
    pitch_mm: float,
    z1: int,
    z2: int,
    desired_center_distance_mm: float,
    selected_links: int,
) -> dict[str, Any]:
    data = ChainInput(
        pitch=pitch_mm,
        small_teeth=z1,
        large_teeth=z2,
        selected_links=selected_links,
        desired_center_distance=desired_center_distance_mm,
    )

    solver = SymmetricPolygonalChainSolver(data)
    solutions = solver.solve()

    if not solutions:
        raise RuntimeError("No valid symmetric polygonal solution was found.")

    best = solutions[0]
    topology = best.topology

    return {
        "pitch_mm": pitch_mm,
        "z1": z1,
        "z2": z2,
        "selected_links": selected_links,
        "desired_center_distance_mm": desired_center_distance_mm,
        "reference_center_distance_mm": best.center_reference,
        "real_center_distance_mm": best.center_distance,
        "center_correction_vs_desired_mm": (
            best.center_distance - desired_center_distance_mm
        ),
        "center_correction_vs_reference_mm": best.center_reference_error,
        "offset_link_required": selected_links % 2 != 0,
        "small_pitch_diameter_mm": 2.0 * pitch_radius(pitch_mm, z1),
        "large_pitch_diameter_mm": 2.0 * pitch_radius(pitch_mm, z2),
        "chain_length_mm": selected_links * pitch_mm,
        "topology": topology,
        "candidate_count": len(solutions),
        "continuous_estimates": best.continuous_estimates,
        "topology_error": best.topology_error,
        "max_edge_error_mm": best.max_link_error,
        "mean_edge_error_mm": best.mean_link_error,
        "self_intersections": best.self_intersections,
        "large_phase_angle_rad": best.large_phase_angle_rad,
        "large_phase_angle_deg": best.large_phase_angle_deg,
        "small_top_angle_deg": math.degrees(best.small_top_angle_rad),
        "small_bottom_angle_deg": math.degrees(best.small_bottom_angle_rad),
        "large_top_angle_deg": math.degrees(best.large_top_angle_rad),
        "large_bottom_angle_deg": math.degrees(best.large_bottom_angle_rad),
        "points": best.points,
    }


# =============================================================================
# RENDERING HELPERS
# =============================================================================

def find_first_existing_path(paths: list[Path]) -> Optional[Path]:
    for path in paths:
        if path.exists():
            return path

    return None


def create_polygonal_layout_figure(result: dict[str, Any], chain_data: dict[str, Any]) -> plt.Figure:
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


def render_chain_data_table(chain_data: dict[str, Any]) -> None:
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


def render_project_links() -> None:
    st.divider()
    st.subheader("Project links")

    col_1, col_2, col_3 = st.columns(3)

    with col_1:
        st.link_button(
            "GitHub repository",
            GITHUB_REPOSITORY_URL,
            use_container_width=True,
        )

    with col_2:
        st.link_button(
            "Mathematical formulation PDF",
            f"{GITHUB_REPOSITORY_URL}/blob/main/docs/complete_mathematical_formulation_en.pdf",
            use_container_width=True,
        )

    with col_3:
        st.link_button(
            "Author LinkedIn",
            AUTHOR_LINKEDIN_URL,
            use_container_width=True,
        )

    st.caption(
        "Developed by Douglas Delorenzi Schons. "
        "This app is a CAD-oriented geometric calculator for ASA roller chain drives."
    )


# =============================================================================
# SIDEBAR INPUTS
# =============================================================================

available_chain_sizes = get_available_chain_sizes()

chain_data: Optional[dict[str, Any]] = None
pitch_mm: Optional[float] = None
roller_diameter_mm: Optional[float] = None
tooth_options: list[int] = []
z1: Optional[int] = None
z2: Optional[int] = None
minimum_center_distance_mm: Optional[float] = None
desired_center_distance_mm: Optional[float] = None
continuous_links: Optional[float] = None
selected_links: Optional[int] = None
run_calculation = False

with st.sidebar:
    st.header("Input data")

    selected_chain_size = st.selectbox(
        "ASA chain size",
        options=available_chain_sizes,
        index=None,
        placeholder="Choose an ASA chain size",
    )

    if selected_chain_size is None:
        st.info("Choose an ASA chain size to start.")
    else:
        chain_data = get_chain_data(selected_chain_size)
        pitch_mm = float(chain_data["pitch_mm"])
        roller_diameter_mm = float(chain_data["roller_diameter_R_mm"])
        tooth_options = get_sprocket_teeth_options(selected_chain_size)

        st.caption(
            "Available sprocket teeth: "
            + " | ".join(str(value) for value in tooth_options)
        )

        z1 = st.selectbox(
            "Smaller sprocket teeth z1",
            options=tooth_options,
            index=None,
            placeholder="Select z1",
        )

        if z1 is None:
            st.info("Select the smaller sprocket tooth count.")
        else:
            z2_options = [value for value in tooth_options if value >= int(z1)]

            z2 = st.selectbox(
                "Larger sprocket teeth z2",
                options=z2_options,
                index=None,
                placeholder="Select z2",
            )

            if z2 is None:
                st.info("Select the larger sprocket tooth count.")
            else:
                minimum_center_distance_mm = minimum_center_distance_by_outer_diameter(
                    pitch_mm=float(pitch_mm),
                    roller_diameter_mm=float(roller_diameter_mm),
                    z1=int(z1),
                    z2=int(z2),
                    clearance_mm=5.0,
                )

                st.metric(
                    "Minimum center distance",
                    f"{minimum_center_distance_mm:.3f} mm",
                )

                desired_center_distance_mm = st.number_input(
                    "Desired center distance [mm]",
                    min_value=float(round(minimum_center_distance_mm, 3)),
                    value=None,
                    step=1.0,
                    format="%.3f",
                    placeholder="Enter center distance",
                )

                if desired_center_distance_mm is None:
                    st.info(
                        "Enter a desired center distance greater than or equal "
                        "to the minimum center distance."
                    )
                else:
                    continuous_links = exact_continuous_link_count(
                        pitch_mm=float(pitch_mm),
                        z1=int(z1),
                        z2=int(z2),
                        center_distance_mm=float(desired_center_distance_mm),
                    )
                    selected_links = round_half_up(continuous_links)

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

presentation_image_path = find_first_existing_path(PRESENTATION_IMAGE_CANDIDATES)

if presentation_image_path is not None:
    st.image(
        str(presentation_image_path),
        caption="Chain drive geometric model",
        use_container_width=True,
    )
else:
    st.warning(
        "Presentation image not found. Expected `assets/instructions.png` "
        "or `docs/figures/instructions.png`."
    )

st.markdown(
    """
This app calculates the geometric layout of an ASA roller chain drive using a
**discrete polygonal roller-center model**. The final geometry is based on an
integer number of chain links and a valid contact topology around the sprockets.
"""
)

if not run_calculation:
    st.info(
        "Use the sidebar to choose the ASA chain size, sprocket tooth counts, "
        "and desired center distance."
    )
    render_project_links()
    st.stop()

if (
    chain_data is None
    or pitch_mm is None
    or z1 is None
    or z2 is None
    or minimum_center_distance_mm is None
    or desired_center_distance_mm is None
    or continuous_links is None
    or selected_links is None
):
    st.error("The input data is incomplete. Check the sidebar selections.")
    render_project_links()
    st.stop()

try:
    result = solve_symmetric_polygonal_center_distance(
        pitch_mm=float(pitch_mm),
        z1=int(z1),
        z2=int(z2),
        desired_center_distance_mm=float(desired_center_distance_mm),
        selected_links=int(selected_links),
    )
except Exception as error:
    st.error(f"Calculation failed: {error}")
    render_project_links()
    st.stop()

topology = result["topology"]

summary_col_1, summary_col_2, summary_col_3 = st.columns(3)
summary_col_1.metric("Selected chain", f"ASA {chain_data['asa_size']}")
summary_col_2.metric("Pitch", f"{pitch_mm:.3f} mm")
summary_col_3.metric(
    "Minimum center distance",
    f"{minimum_center_distance_mm:.2f} mm",
)

st.divider()

result_col_1, result_col_2, result_col_3 = st.columns(3)

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
        {
            "Parameter": "Desired center distance",
            "Value": f"{result['desired_center_distance_mm']:.6f} mm",
        },
        {
            "Parameter": "Reference continuous center distance",
            "Value": f"{result['reference_center_distance_mm']:.6f} mm",
        },
        {
            "Parameter": "Real center distance",
            "Value": f"{result['real_center_distance_mm']:.6f} mm",
        },
        {
            "Parameter": "Center correction vs desired",
            "Value": f"{result['center_correction_vs_desired_mm']:+.6f} mm",
        },
        {
            "Parameter": "Center correction vs reference",
            "Value": f"{result['center_correction_vs_reference_mm']:+.6f} mm",
        },
        {
            "Parameter": "Continuous link estimate",
            "Value": f"{continuous_links:.6f}",
        },
        {
            "Parameter": "Selected link count",
            "Value": f"{result['selected_links']}",
        },
        {
            "Parameter": "Offset link required",
            "Value": "Yes" if result["offset_link_required"] else "No",
        },
        {
            "Parameter": "Small sprocket pitch diameter",
            "Value": f"{result['small_pitch_diameter_mm']:.6f} mm",
        },
        {
            "Parameter": "Large sprocket pitch diameter",
            "Value": f"{result['large_pitch_diameter_mm']:.6f} mm",
        },
        {
            "Parameter": "Chain length",
            "Value": f"{result['chain_length_mm']:.6f} mm",
        },
        {
            "Parameter": "Topology by contact rollers",
            "Value": topology.roller_label(),
        },
        {
            "Parameter": "Topology by pitch intervals",
            "Value": topology.interval_label(),
        },
        {
            "Parameter": "Maximum pitch error",
            "Value": f"{result['max_edge_error_mm']:.3e} mm",
        },
        {
            "Parameter": "Mean pitch error",
            "Value": f"{result['mean_edge_error_mm']:.3e} mm",
        },
        {
            "Parameter": "Self-intersections",
            "Value": f"{result['self_intersections']}",
        },
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
polygonal model, the topology equation, CAD validation, limitations, and future
development.
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
