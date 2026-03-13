"""Interactive GUI runner for backward planners."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MPL_CONFIG_DIR = PROJECT_ROOT / ".matplotlib"
XDG_CACHE_DIR = PROJECT_ROOT / ".cache"
MPL_CONFIG_DIR.mkdir(exist_ok=True)
XDG_CACHE_DIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", MPL_CONFIG_DIR.as_posix())
os.environ.setdefault("XDG_CACHE_HOME", XDG_CACHE_DIR.as_posix())
if PROJECT_ROOT.as_posix() not in sys.path:
    sys.path.insert(0, PROJECT_ROOT.as_posix())

from src import BackwardBFS, BackwardDijkstra, GridMap, Visualizer
from src.map import Node
from src.navigator import SearchResult


def build_planner(algorithm: str, grid_map: GridMap):
    normalized = algorithm.strip().lower()
    if normalized == "bfs":
        return BackwardBFS(grid_map)
    if normalized == "dijkstra":
        return BackwardDijkstra(grid_map)
    raise ValueError("Algorithm must be either 'bfs' or 'dijkstra'.")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the ENPM661 Project 02 GUI.")
    parser.add_argument("--algorithm", choices=["bfs", "dijkstra"], help="Planner to execute.")
    parser.add_argument("--start", nargs=2, type=int, metavar=("X", "Y"), help="Start coordinate.")
    parser.add_argument("--goal", nargs=2, type=int, metavar=("X", "Y"), help="Goal coordinate.")
    parser.add_argument("--no-show", action="store_true", help="Skip the matplotlib GUI window.")
    return parser.parse_args()


def prompt_algorithm(default_algorithm: Optional[str] = None) -> str:
    if default_algorithm:
        return default_algorithm

    while True:
        choice = input("Select planner (bfs/dijkstra): ").strip().lower()
        if choice in {"bfs", "dijkstra"}:
            return choice
        print("Invalid planner. Enter 'bfs' or 'dijkstra'.")


def _prompt_integer(prompt: str) -> int:
    while True:
        raw_value = input(prompt).strip()
        try:
            return int(raw_value)
        except ValueError:
            print("Invalid integer input. Please enter an integer value.")


def prompt_valid_node(grid_map: GridMap, label: str, initial: Optional[Node] = None) -> Node:
    if initial is not None:
        validation = grid_map.validate_user_node(initial)
        if validation.is_valid:
            return initial
        print(f"Invalid {label} node {initial}: {validation.message}")

    while True:
        x_value = _prompt_integer(f"Enter {label} x coordinate: ")
        y_value = _prompt_integer(f"Enter {label} y coordinate: ")
        candidate = (x_value, y_value)
        validation = grid_map.validate_user_node(candidate)
        if validation.is_valid:
            return candidate
        print(f"Invalid {label} node: {validation.message}")


def print_summary(search_result: SearchResult) -> None:
    print(f"Algorithm: {search_result.algorithm_name}")
    print(f"Start: {search_result.start}")
    print(f"Goal: {search_result.goal}")
    print(f"Runtime: {search_result.runtime_seconds:.6f} seconds")
    print(f"Explored nodes: {len(search_result.explored_order)}")
    print(f"Path length: {len(search_result.path)}")
    print(f"Path cost: {search_result.path_cost:.2f}")


def run_application(default_algorithm: Optional[str] = None, show_gui: bool = True) -> SearchResult:
    arguments = parse_arguments()
    grid_map = GridMap()

    algorithm = arguments.algorithm or prompt_algorithm(default_algorithm)
    start = prompt_valid_node(grid_map, "start", tuple(arguments.start) if arguments.start else None)
    goal = prompt_valid_node(grid_map, "goal", tuple(arguments.goal) if arguments.goal else None)

    planner = build_planner(algorithm, grid_map)
    search_result = planner.search(start=start, goal=goal)

    if not search_result.success:
        raise RuntimeError("The planner failed to find a path from start to goal.")

    print_summary(search_result)

    if show_gui and not arguments.no_show:
        Visualizer(grid_map).show_animation(search_result)

    return search_result


def main() -> None:
    run_application()


if __name__ == "__main__":
    main()
