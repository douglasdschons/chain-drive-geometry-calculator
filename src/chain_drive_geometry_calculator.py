from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass
from typing import Any, Optional
from io import StringIO
from matplotlib.patches import Circle
import csv
import math
import matplotlib.image as mpimg

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import brentq


# =============================================================================
# ASA CATALOG
# =============================================================================

ASA_CHAIN_CATALOG = [
    {"asa_size": "25", "pitch_text": "1/4 in", "pitch_mm": 6.35, "inner_width_E_mm": 3.18, "roller_diameter_R_mm": 3.30, "plate_height_H_mm": 6.00, "pin_diameter_G_mm": 2.31, "overall_width_L_mm": 7.90, "plate_thickness_T_mm": 0.80, "breaking_load_kgf": 350, "weight_kg_per_m": 0.15},
    {"asa_size": "35", "pitch_text": "3/8 in", "pitch_mm": 9.53, "inner_width_E_mm": 4.77, "roller_diameter_R_mm": 5.08, "plate_height_H_mm": 8.70, "pin_diameter_G_mm": 3.58, "overall_width_L_mm": 12.30, "plate_thickness_T_mm": 1.30, "breaking_load_kgf": 790, "weight_kg_per_m": 0.33},
    {"asa_size": "41", "pitch_text": "1/2 in", "pitch_mm": 12.70, "inner_width_E_mm": 6.25, "roller_diameter_R_mm": 7.77, "plate_height_H_mm": 9.91, "pin_diameter_G_mm": 3.58, "overall_width_L_mm": 13.75, "plate_thickness_T_mm": 1.30, "breaking_load_kgf": 1284, "weight_kg_per_m": 0.41},
    {"asa_size": "40", "pitch_text": "1/2 in", "pitch_mm": 12.70, "inner_width_E_mm": 7.85, "roller_diameter_R_mm": 7.95, "plate_height_H_mm": 12.00, "pin_diameter_G_mm": 3.96, "overall_width_L_mm": 16.60, "plate_thickness_T_mm": 1.50, "breaking_load_kgf": 1410, "weight_kg_per_m": 0.62},
    {"asa_size": "50", "pitch_text": "5/8 in", "pitch_mm": 15.87, "inner_width_E_mm": 9.40, "roller_diameter_R_mm": 10.16, "plate_height_H_mm": 15.09, "pin_diameter_G_mm": 5.08, "overall_width_L_mm": 20.70, "plate_thickness_T_mm": 2.03, "breaking_load_kgf": 2220, "weight_kg_per_m": 1.02},
    {"asa_size": "60", "pitch_text": "3/4 in", "pitch_mm": 19.05, "inner_width_E_mm": 12.57, "roller_diameter_R_mm": 11.91, "plate_height_H_mm": 18.00, "pin_diameter_G_mm": 5.94, "overall_width_L_mm": 25.90, "plate_thickness_T_mm": 2.42, "breaking_load_kgf": 3180, "weight_kg_per_m": 1.50},
    {"asa_size": "80", "pitch_text": "1 in", "pitch_mm": 25.40, "inner_width_E_mm": 15.75, "roller_diameter_R_mm": 15.88, "plate_height_H_mm": 24.00, "pin_diameter_G_mm": 7.92, "overall_width_L_mm": 32.70, "plate_thickness_T_mm": 3.25, "breaking_load_kgf": 5670, "weight_kg_per_m": 2.60},
    {"asa_size": "100", "pitch_text": "1-1/4 in", "pitch_mm": 31.75, "inner_width_E_mm": 18.90, "roller_diameter_R_mm": 19.05, "plate_height_H_mm": 30.00, "pin_diameter_G_mm": 9.53, "overall_width_L_mm": 40.40, "plate_thickness_T_mm": 4.00, "breaking_load_kgf": 8850, "weight_kg_per_m": 3.91},
    {"asa_size": "120", "pitch_text": "1-1/2 in", "pitch_mm": 38.10, "inner_width_E_mm": 25.22, "roller_diameter_R_mm": 22.23, "plate_height_H_mm": 35.70, "pin_diameter_G_mm": 11.10, "overall_width_L_mm": 50.30, "plate_thickness_T_mm": 4.80, "breaking_load_kgf": 12700, "weight_kg_per_m": 5.62},
    {"asa_size": "140", "pitch_text": "1-3/4 in", "pitch_mm": 44.45, "inner_width_E_mm": 25.22, "roller_diameter_R_mm": 25.40, "plate_height_H_mm": 41.00, "pin_diameter_G_mm": 12.70, "overall_width_L_mm": 54.40, "plate_thickness_T_mm": 5.60, "breaking_load_kgf": 17240, "weight_kg_per_m": 7.70},
    {"asa_size": "160", "pitch_text": "2 in", "pitch_mm": 50.80, "inner_width_E_mm": 31.55, "roller_diameter_R_mm": 28.58, "plate_height_H_mm": 47.80, "pin_diameter_G_mm": 14.27, "overall_width_L_mm": 64.80, "plate_thickness_T_mm": 6.40, "breaking_load_kgf": 22680, "weight_kg_per_m": 10.10},
    {"asa_size": "180", "pitch_text": "2-1/4 in", "pitch_mm": 57.15, "inner_width_E_mm": 35.50, "roller_diameter_R_mm": 35.71, "plate_height_H_mm": 53.60, "pin_diameter_G_mm": 17.46, "overall_width_L_mm": 72.80, "plate_thickness_T_mm": 7.20, "breaking_load_kgf": 34000, "weight_kg_per_m": 13.50},
    {"asa_size": "200", "pitch_text": "2-1/2 in", "pitch_mm": 63.50, "inner_width_E_mm": 37.85, "roller_diameter_R_mm": 39.68, "plate_height_H_mm": 60.00, "pin_diameter_G_mm": 19.85, "overall_width_L_mm": 80.30, "plate_thickness_T_mm": 8.00, "breaking_load_kgf": 35380, "weight_kg_per_m": 16.15},
    {"asa_size": "240", "pitch_text": "3 in", "pitch_mm": 76.20, "inner_width_E_mm": 47.35, "roller_diameter_R_mm": 47.63, "plate_height_H_mm": 72.39, "pin_diameter_G_mm": 23.81, "overall_width_L_mm": 95.50, "plate_thickness_T_mm": 9.50, "breaking_load_kgf": 51030, "weight_kg_per_m": 23.20},
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
    reader = csv.DictReader(
        StringIO(SPROCKET_TEETH_OPTIONS_CSV),
        delimiter=";",
    )

    if reader.fieldnames is None:
        raise ValueError("Invalid ENCO sprocket tooth table.")

    group_options: dict[str, list[int]] = {
        group_name: []
        for group_name in reader.fieldnames
    }

    for row in reader:
        for group_name, raw_value in row.items():
            value_text = (raw_value or "").strip()

            if not value_text:
                continue

            group_options[group_name].append(int(value_text))

    options_by_asa_size: dict[str, list[int]] = {}

    for group_name, asa_sizes in SPROCKET_TEETH_GROUPS.items():
        if group_name not in group_options:
            continue

        options = sorted(set(group_options[group_name]))

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
# INPUT HELPERS
# =============================================================================

def normalize_chain_size(chain_size: str) -> str:
    normalized = chain_size.upper().strip()

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
    raise ValueError(f"ASA chain size {chain_size} was not found. Available options: {available}")


def ask_chain_size() -> dict[str, Any]:
    supported_catalog_rows = [
        row
        for row in ASA_CHAIN_CATALOG
        if row["asa_size"] in SPROCKET_TEETH_OPTIONS_BY_ASA_SIZE
    ]

    available = " | ".join(row["asa_size"] for row in supported_catalog_rows)

    while True:
        print()
        print(f"Available ASA chain sizes with ENCO sprocket tooth tables: {available}")
        raw = input("Select the ASA chain size: ").strip()

        try:
            chain_data = get_chain_data(raw)
        except ValueError as error:
            print(error)
            continue

        if chain_data["asa_size"] not in SPROCKET_TEETH_OPTIONS_BY_ASA_SIZE:
            print(
                f"ASA chain size {chain_data['asa_size']} does not have "
                "registered sprocket tooth options in the ENCO table used by this program."
            )
            continue

        return chain_data

def get_sprocket_teeth_options(chain_size: str) -> list[int]:
    normalized = normalize_chain_size(chain_size)

    if normalized not in SPROCKET_TEETH_OPTIONS_BY_ASA_SIZE:
        available = " | ".join(sorted(SPROCKET_TEETH_OPTIONS_BY_ASA_SIZE))
        raise ValueError(
            f"No sprocket tooth table is available for ASA {chain_size}. "
            f"Available chain sizes with tooth tables: {available}"
        )

    return SPROCKET_TEETH_OPTIONS_BY_ASA_SIZE[normalized]


def ask_sprocket_teeth(prompt: str, chain_data: dict[str, Any]) -> int:
    options = get_sprocket_teeth_options(chain_data["asa_size"])
    options_text = " | ".join(str(value) for value in options)

    while True:
        print()
        print(f"Available sprocket tooth options for ASA {chain_data['asa_size']}:")
        print(options_text)

        raw = input(f"{prompt}: ").strip()

        try:
            value = int(raw)
        except ValueError:
            print("Enter an integer value.")
            continue

        if value not in options:
            print(
                f"Tooth count {value} is not available for "
                f"ASA {chain_data['asa_size']} in the ENCO table."
            )
            continue

        return value

def ask_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()

        try:
            value = int(raw)
        except ValueError:
            print("Enter an integer value.")
            continue

        if value <= 2:
            print("The number of teeth must be greater than 2.")
            continue

        return value


def ask_float(prompt: str) -> float:
    while True:
        raw = input(prompt).strip().replace(",", ".")

        try:
            value = float(raw)
        except ValueError:
            print("Enter a valid numeric value.")
            continue

        if value <= 0:
            print("The value must be greater than zero.")
            continue

        return value


def ask_center_distance(prompt: str, minimum_center_distance: float) -> float:
    while True:
        raw = input(prompt).strip().replace(",", ".")

        try:
            value = float(raw)
        except ValueError:
            print("Enter a valid numeric value.")
            continue

        if value <= 0:
            print("The value must be greater than zero.")
            continue

        if value < minimum_center_distance:
            print()
            print("Invalid center distance for this sprocket combination.")
            print(f"Minimum allowed center distance: {minimum_center_distance:.3f} mm")
            print(f"Entered value: {value:.3f} mm")
            print("Enter a value greater than or equal to the minimum.")
            continue

        return value



# =============================================================================
# BASIC GEOMETRY
# =============================================================================

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


def sprocket_outer_diameter_min(
    pitch_mm: float,
    roller_diameter_mm: float,
    teeth: int,
) -> float:
    nominal_diameter_mm = pitch_diameter(pitch_mm, teeth)

    return (
        nominal_diameter_mm
        + (1.0 - 1.6 / teeth) * pitch_mm
        - roller_diameter_mm
    )


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
        raise ValueError("Invalid center distance for the sprocket geometry.")

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
        pitch_mm,
        z1,
        z2,
        center_distance_mm,
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
            pitch_mm,
            z1,
            z2,
            center_distance_mm,
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
    return float((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))


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
# SYMMETRIC POLYGONAL SOLVER V4
# =============================================================================

class SymmetricPolygonalChainSolver:
    """Symmetric polygonal chain solver.

    V4 correction:
    - Sprocket contact is counted by rollers, not links.
    - If M is odd, a roller lies on the symmetry axis.
    - If M is even, the symmetry axis lies halfway between two rollers.
    - Contact endpoints are computed with q = (M - 1) / 2, which may be integer
      or half-integer.
    """

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
            self.pitch,
            self.z1,
            self.z2,
            self.N,
            self.C_desired,
        )

        self.estimates = continuous_topology_estimates(
            self.pitch,
            self.z1,
            self.z2,
            self.C_reference,
        )

    def contact_angles(self, topology: SymmetricTopology) -> tuple[float, float, float, float]:
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

        # Estimates are arc intervals. Candidate contact rollers are near
        # both arc_estimate and arc_estimate + 1 because real contact is counted
        # by rollers, while length is counted by intervals.
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

                # Symmetric direct mode requires S = R, therefore remaining
                # intervals in straight runs must be even.
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

        vertical_difference = (
            self.r2 * math.sin(large_top_angle)
            - A_top[1]
        )

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

        # Upper straight run: A_top -> B_top
        for step in range(1, topology.upper_run_intervals + 1):
            fraction = step / topology.upper_run_intervals
            points.append(A_top + fraction * (B_top - A_top))

        # Large sprocket contact: B_top -> B_bottom, clockwise.
        for step in range(1, topology.large_arc_intervals + 1):
            angle = large_top_angle - step * self.delta2
            points.append(point_on_circle(O2, self.r2, angle))

        # Lower straight run: B_bottom -> A_bottom
        for step in range(1, topology.lower_run_intervals + 1):
            fraction = step / topology.lower_run_intervals
            points.append(B_bottom + fraction * (A_bottom - B_bottom))

        # Small sprocket contact: A_bottom -> A_top, counter-clockwise in traversal
        # represented by decreasing angle from bottom to top.
        for step in range(1, topology.small_arc_intervals):
            angle = small_bottom_angle - step * self.delta1
            points.append(point_on_circle(self.O1, self.r1, angle))

        return np.vstack(points)

    def topology_error(self, topology: SymmetricTopology) -> float:
        small_arc_estimate, large_arc_estimate, run_estimate = self.estimates

        # V4 selection uses CONTACT ROLLERS on sprockets.
        # The continuous estimates are not exact roller counts, but they are useful
        # as topology proxies. Comparing M1/M2 directly to those estimates avoids
        # the V3 error of overvaluing interval counts on the sprockets.
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

        (
            small_top_angle,
            small_bottom_angle,
            large_top_angle,
            large_bottom_angle,
        ) = self.contact_angles(topology)

        if self_intersections != 0:
            return None

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
# PUBLIC WRAPPER
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
        "center_correction_vs_desired_mm": best.center_distance - desired_center_distance_mm,
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
# OUTPUT
# =============================================================================

def print_results(
    result: dict[str, Any],
    chain_data: dict[str, Any],
    continuous_links: float,
) -> None:
    topology = result["topology"]
    small_arc_estimate, large_arc_estimate, run_estimate = result["continuous_estimates"]

    print()
    print("=" * 72)
    print("RESULTS - SYMMETRIC POLYGONAL MODEL")
    print("=" * 72)
    print(f"Selected chain: ASA {chain_data['asa_size']}")
    print(f"Catalog pitch: {result['pitch_mm']:.3f} mm")
    print(f"Smaller sprocket teeth z1: {result['z1']}")
    print(f"Larger sprocket teeth z2: {result['z2']}")
    print(f"Desired center distance: {result['desired_center_distance_mm']:.3f} mm")
    print()
    print(f"Estimated continuous link count: {continuous_links:.6f}")
    print(f"Adopted integer link count: {result['selected_links']}")
    print(f"Offset link required: {'YES' if result['offset_link_required'] else 'NO'}")
    print()
    print(f"Continuous reference center distance for N: {result['reference_center_distance_mm']:.6f} mm")
    print(f"Calculated real center distance: {result['real_center_distance_mm']:.6f} mm")
    print(f"Engineering center distance: {result['real_center_distance_mm']:.2f} mm")
    print(f"Correction relative to desired center distance: {result['center_correction_vs_desired_mm']:+.6f} mm")
    print(f"Correction relative to continuous reference: {result['center_correction_vs_reference_mm']:+.6f} mm")
    print()
    print(f"Smaller sprocket pitch diameter: {result['small_pitch_diameter_mm']:.6f} mm")
    print(f"Larger sprocket pitch diameter: {result['large_pitch_diameter_mm']:.6f} mm")
    print(f"Chain length: {result['chain_length_mm']:.6f} mm")
    print()
    print("Topology by contact rollers:")
    print(f"  M1/S/M2/R = {topology.roller_label()}")
    print("Topology by pitch intervals:")
    print(f"  intervals = {topology.interval_label()}")
    print()
    print("Contact angles calculated by symmetry:")
    print(f"  smaller sprocket top: {result['small_top_angle_deg']:.6f}°")
    print(f"  smaller sprocket bottom: {result['small_bottom_angle_deg']:.6f}°")
    print(f"  larger sprocket top: {result['large_top_angle_deg']:.6f}°")
    print(f"  larger sprocket bottom: {result['large_bottom_angle_deg']:.6f}°")
    print(f"  larger sprocket phase angle: {result['large_phase_angle_deg']:.6f}°")
    print()
    print("Continuous estimates used for topology prioritization:")
    print(f"  small arc intervals estimate: {small_arc_estimate:.6f}")
    print(f"  large arc intervals estimate: {large_arc_estimate:.6f}")
    print(f"  straight run intervals estimate: {run_estimate:.6f}")
    print(f"  topology error: {result['topology_error']:.6f}")
    print()
    print(f"Valid candidates found: {result['candidate_count']}")
    print(f"Maximum link length error: {result['max_edge_error_mm']:.3e} mm")
    print(f"Mean link length error: {result['mean_edge_error_mm']:.3e} mm")
    print(f"Detected self-intersections: {result['self_intersections']}")
    print()
    print("Catalog data:")
    print(f"  Inner width E: {chain_data['inner_width_E_mm']:.3f} mm")
    print(f"  Roller diameter R: {chain_data['roller_diameter_R_mm']:.3f} mm")
    print(f"  Plate height H: {chain_data['plate_height_H_mm']:.3f} mm")
    print(f"  Pin diameter G: {chain_data['pin_diameter_G_mm']:.3f} mm")
    print(f"  Overall width L: {chain_data['overall_width_L_mm']:.3f} mm")
    print(f"  Breaking load: {chain_data['breaking_load_kgf']:.1f} kgf")
    print(f"  Weight: {chain_data['weight_kg_per_m']:.3f} kg/m")


def plot_result(result: dict[str, Any], chain_data: dict[str, Any]) -> None:
    plot_polygonal_layout(result, chain_data)
    plot_chain_dimension_sheet(result, chain_data)
    
def plot_polygonal_layout(result: dict[str, Any], chain_data: dict[str, Any]) -> None:
    points = result["points"]
    closed_points = np.vstack([points, points[0]])

    pitch_mm = float(result["pitch_mm"])
    z1 = int(result["z1"])
    z2 = int(result["z2"])

    R1 = pitch_radius(pitch_mm, z1)
    R2 = pitch_radius(pitch_mm, z2)
    C = float(result["real_center_distance_mm"])

    pitch_diameter_1 = 2.0 * R1
    pitch_diameter_2 = 2.0 * R2

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
            R1,
            fill=False,
            linestyle="--",
            label=f"Pitch circle 1 (Øp1 = {pitch_diameter_1:.2f} mm)",
        )
    )

    ax.add_patch(
        Circle(
            (C, 0.0),
            R2,
            fill=False,
            linestyle="--",
            label=f"Pitch circle 2 (Øp2 = {pitch_diameter_2:.2f} mm)",
        )
    )

    ax.scatter([0.0, C], [0.0, 0.0], marker="x", s=90, label="Centers")

    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.3)
    ax.set_xlabel("x [mm]")
    ax.set_ylabel("y [mm]")
    ax.set_title(
        f"ASA {chain_data['asa_size']} | "
        f"z1={result['z1']}, z2={result['z2']} | "
        f"C_real={C:.2f} mm | N={result['selected_links']}"
    )
    ax.legend(loc="best")

    fig.tight_layout()
    plt.show(block=True)

def find_chain_dimension_image(image_name: str = "enco_asa_dimensions.png") -> Path:
    """
    Locate the chain dimension reference image.

    Expected repository structure:

        chain-drive-geometry-calculator/
        ├── src/
        │   └── chain_drive_geometry_calculator.py
        └── assets/
            └── enco_asa_dimensions.png

    Returns
    -------
    Path
        Absolute path to the image file.

    Raises
    ------
    FileNotFoundError
        If the image cannot be found in the expected locations.
    """
    try:
        module_dir = Path(__file__).resolve().parent
    except NameError:
        module_dir = Path.cwd()

    project_root = module_dir.parent

    candidate_paths = [
        project_root / "assets" / image_name,
        module_dir / "assets" / image_name,
        Path.cwd() / "assets" / image_name,
        Path.cwd() / image_name,
    ]

    for path in candidate_paths:
        if path.exists():
            return path

    searched_paths = "\n".join(str(path) for path in candidate_paths)

    raise FileNotFoundError(
        f"Could not find '{image_name}'. Searched in:\n{searched_paths}"
    )
def plot_chain_dimension_sheet(result: dict[str, Any], chain_data: dict[str, Any]) -> None:
    image_path = find_chain_dimension_image()
    dimension_image = mpimg.imread(image_path)

    pitch_mm = float(chain_data["pitch_mm"])
    inner_width_mm = float(chain_data["inner_width_E_mm"])
    roller_diameter_mm = float(chain_data["roller_diameter_R_mm"])
    plate_height_mm = float(chain_data["plate_height_H_mm"])
    pin_diameter_mm = float(chain_data["pin_diameter_G_mm"])
    overall_width_mm = float(chain_data["overall_width_L_mm"])
    plate_thickness_mm = float(chain_data["plate_thickness_T_mm"])
    breaking_load_kgf = float(chain_data["breaking_load_kgf"])
    weight_kg_per_m = float(chain_data["weight_kg_per_m"])

    chain_length_mm = float(result["chain_length_mm"])
    chain_length_m = chain_length_mm / 1000.0
    total_chain_weight_kg = chain_length_m * weight_kg_per_m
    topology = result["topology"]

    fig = plt.figure(figsize=(8.27, 11.69))  # A4 portrait

    grid = fig.add_gridspec(
        2,
        1,
        height_ratios=[0.74, 0.26],
        hspace=0.08,
    )

    ax_table = fig.add_subplot(grid[0, 0])
    ax_image = fig.add_subplot(grid[1, 0])

    # -------------------------------------------------------------------------
    # COMPACT MANUAL TABLE
    # -------------------------------------------------------------------------
    ax_table.axis("off")

    table_rows = [
        ("section", "INPUT DATA", ""),
        ("data", "ASA size", f"ASA {chain_data['asa_size']}"),
        ("data", "Small sprocket teeth", f"{result['z1']}"),
        ("data", "Large sprocket teeth", f"{result['z2']}"),
        ("data", "Desired center distance", f"{result['desired_center_distance_mm']:.2f} mm"),
        ("data", "Selected link count", f"{result['selected_links']}"),
        ("data", "Offset link required", "YES" if result["offset_link_required"] else "NO"),

        ("section", "CALCULATED DRIVE GEOMETRY", ""),
        ("data", "Pitch diameter Øp1", f"{result['small_pitch_diameter_mm']:.2f} mm"),
        ("data", "Pitch diameter Øp2", f"{result['large_pitch_diameter_mm']:.2f} mm"),
        ("data", "Reference center distance", f"{result['reference_center_distance_mm']:.2f} mm"),
        ("data", "Real center distance", f"{result['real_center_distance_mm']:.2f} mm"),
        ("data", "Center correction", f"{result['center_correction_vs_desired_mm']:+.2f} mm"),
        ("data", "Chain length", f"{chain_length_mm:.2f} mm"),
        ("data", "Topology M1/S/M2/R", topology.roller_label()),
        ("data", "Topology intervals", topology.interval_label()),
        ("data", "Valid candidates", f"{result['candidate_count']}"),
        ("data", "Maximum pitch error", f"{result['max_edge_error_mm']:.3e} mm"),

        ("section", "CHAIN DIMENSIONS", ""),
        ("data", "Pitch P", f"{pitch_mm:.2f} mm"),
        ("data", "Roller diameter R", f"{roller_diameter_mm:.2f} mm"),
        ("data", "Inner width E", f"{inner_width_mm:.2f} mm"),
        ("data", "Plate height H", f"{plate_height_mm:.2f} mm"),
        ("data", "Pin diameter G", f"{pin_diameter_mm:.2f} mm"),
        ("data", "Overall width L", f"{overall_width_mm:.2f} mm"),
        ("data", "Plate thickness T", f"{plate_thickness_mm:.2f} mm"),
        ("data", "Breaking load", f"{breaking_load_kgf:.0f} kgf"),
        ("data", "Weight", f"{weight_kg_per_m:.2f} kg/m"),
        ("data", "Total chain weight", f"{total_chain_weight_kg:.2f} kg"),
    ]
    table_line_color = "black"

    # Table geometry in axis coordinates.
    x_left = 0.18
    x_split = 0.58
    x_right = 0.80

    y_top = 0.98
    y_bottom = 0.02

    row_count = len(table_rows)
    row_height = (y_top - y_bottom) / row_count

    # Outer vertical lines.
    ax_table.plot([x_left, x_left], [y_bottom, y_top], linewidth=0.8, color=table_line_color)
    ax_table.plot([x_split, x_split], [y_bottom, y_top], linewidth=0.8, color=table_line_color)
    ax_table.plot([x_right, x_right], [y_bottom, y_top], linewidth=0.8, color=table_line_color)

    # Top border.
    ax_table.plot([x_left, x_right], [y_top, y_top], linewidth=0.8, color=table_line_color)

    for row_index, (row_type, label, value) in enumerate(table_rows):
        y_center = y_top - (row_index + 0.5) * row_height
        y_line = y_top - (row_index + 1.0) * row_height

        if row_type == "section":
            ax_table.text(
                x_left + 0.012,
                y_center,
                label,
                ha="left",
                va="center",
                fontsize=11.0,
                fontweight="bold",
            )
            ax_table.plot([x_left, x_right], [y_line, y_line], linewidth=0.8, color=table_line_color)

        else:
            ax_table.text(
                x_left + 0.012,
                y_center,
                label,
                ha="left",
                va="center",
                fontsize=10.5,
            )

            ax_table.text(
                x_split + 0.012,
                y_center,
                value,
                ha="left",
                va="center",
                fontsize=10.5,
            )

            ax_table.plot([x_left, x_right], [y_line, y_line], linewidth=0.45, color=table_line_color)

    ax_table.set_xlim(0.0, 1.0)
    ax_table.set_ylim(0.0, 1.0)

    ax_table.set_title(
        "Calculation summary",
        fontsize=13,
        pad=8,
    )

    # -------------------------------------------------------------------------
    # DIMENSION IMAGE BELOW TABLE
    # -------------------------------------------------------------------------
    ax_image.imshow(dimension_image)
    ax_image.axis("off")
    ax_image.set_title(
        "ASA roller chain dimensions",
        fontsize=10,
        pad=4,
    )

    fig.suptitle(
        f"ASA {chain_data['asa_size']} - Chain drive technical sheet",
        fontsize=14,
        y=0.985,
    )

    fig.subplots_adjust(
        left=0.04,
        right=0.96,
        top=0.95,
        bottom=0.04,
    )

    plt.show(block=True)
    
# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    print("=" * 72)
    print("ASA ROLLER CHAIN DRIVE CALCULATOR")
    print("Discrete polygonal roller-center model for ASA roller chains")
    print("=" * 72)
    print("1. Select the ASA chain size from the catalog.")
    print("2. Enter the smaller and larger sprocket tooth counts.")
    print("3. The program calculates the minimum allowed center distance.")
    print("4. Enter the desired center distance.")
    print("5. The program estimates N from the desired center distance.")
    print("6. The program then solves C using the symmetric polygonal roller-center model.")

    chain_data = ask_chain_size()
    pitch_mm = float(chain_data["pitch_mm"])

    print()
    print(f"Selected chain: ASA {chain_data['asa_size']}")
    print(f"Pitch: {pitch_mm:.3f} mm")

    z1 = ask_sprocket_teeth(
        "Number of teeth on the smaller sprocket z1",
        chain_data,
    )

    z2 = ask_sprocket_teeth(
        "Number of teeth on the larger sprocket z2",
        chain_data,
    )

    if z1 > z2:
        print()
        print("WARNING: z1 was entered as greater than z2.")
        print("The program will swap the values to keep z1 as the smaller sprocket.")
        z1, z2 = z2, z1

    roller_diameter_mm = float(chain_data["roller_diameter_R_mm"])

    minimum_center_distance_mm = minimum_center_distance_by_outer_diameter(
        pitch_mm=pitch_mm,
        roller_diameter_mm=roller_diameter_mm,
        z1=z1,
        z2=z2,
        clearance_mm=5.0,
    )

    outer_diameter_1_max = sprocket_outer_diameter_max(
        pitch_mm=pitch_mm,
        roller_diameter_mm=roller_diameter_mm,
        teeth=z1,
    )

    outer_diameter_2_max = sprocket_outer_diameter_max(
        pitch_mm=pitch_mm,
        roller_diameter_mm=roller_diameter_mm,
        teeth=z2,
    )

    print()
    print("=" * 72)
    print("MINIMUM CENTER DISTANCE CHECK")
    print("=" * 72)
    print(f"Maximum outer diameter 1: {outer_diameter_1_max:.3f} mm")
    print(f"Maximum outer diameter 2: {outer_diameter_2_max:.3f} mm")
    print("Adopted minimum clearance: 5.000 mm")
    print()
    print(f"Minimum allowed center distance: {minimum_center_distance_mm:.3f} mm")

    desired_center_distance_mm = ask_center_distance(
        "Desired center distance [mm]: ",
        minimum_center_distance_mm,
    )

    continuous_links = exact_continuous_link_count(
        pitch_mm=pitch_mm,
        z1=z1,
        z2=z2,
        center_distance_mm=desired_center_distance_mm,
    )

    selected_links = round_half_up(continuous_links)

    print()
    print("=" * 72)
    print("LINK COUNT DEFINITION")
    print("=" * 72)
    print(f"Estimated continuous link count: {continuous_links:.6f}")
    print(f"Adopted integer link count: {selected_links}")
    print(f"Offset link required: {'YES' if selected_links % 2 != 0 else 'NO'}")

    print()
    print("Processing the symmetric polygonal roller-center model...")

    result = solve_symmetric_polygonal_center_distance(
        pitch_mm=pitch_mm,
        z1=z1,
        z2=z2,
        desired_center_distance_mm=desired_center_distance_mm,
        selected_links=selected_links,
    )

    print_results(result, chain_data, continuous_links)
    plot_result(result, chain_data)


if __name__ == "__main__":
    main()
