"""Record a planner animation to an MP4 file."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MPL_CONFIG_DIR = PROJECT_ROOT / ".matplotlib"
XDG_CACHE_DIR = PROJECT_ROOT / ".cache"
MPL_CONFIG_DIR.mkdir(exist_ok=True)
XDG_CACHE_DIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", MPL_CONFIG_DIR.as_posix())
os.environ.setdefault("XDG_CACHE_HOME", XDG_CACHE_DIR.as_posix())
if PROJECT_ROOT.as_posix() not in sys.path:
    sys.path.insert(0, PROJECT_ROOT.as_posix())

import matplotlib

matplotlib.use("Agg")

from src import BackwardBFS, BackwardDijkstra, GridMap, Visualizer
from src.map import Node
from src.navigator import SearchResult


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record an MP4 animation for ENPM661 Project 02.")
    parser.add_argument("--algorithm", choices=["bfs", "dijkstra"], default="dijkstra", help="Planner to execute.")
    parser.add_argument("--start", nargs=2, type=int, metavar=("X", "Y"), help="Start coordinate.")
    parser.add_argument("--goal", nargs=2, type=int, metavar=("X", "Y"), help="Goal coordinate.")
    parser.add_argument(
        "--output",
        default=None,
        help="Output MP4 path. Defaults to outputs/<algorithm>_animation.mp4.",
    )
    parser.add_argument("--fps", type=int, default=30, help="Frames per second for the MP4 file.")
    parser.add_argument("--interval", type=int, default=30, help="Animation interval in milliseconds.")
    return parser.parse_args()


def build_planner(algorithm: str, grid_map: GridMap):
    if algorithm == "bfs":
        return BackwardBFS(grid_map)
    return BackwardDijkstra(grid_map)


def find_default_nodes(grid_map: GridMap) -> tuple[Node, Node]:
    start = _find_first_valid_node(grid_map, range(5, grid_map.width // 3), range(5, grid_map.height - 5))
    goal = _find_first_valid_node(
        grid_map,
        range(grid_map.width - 6, grid_map.width // 2, -1),
        range(grid_map.height - 6, 4, -1),
    )
    if start == goal:
        raise RuntimeError("Failed to select distinct default nodes.")
    return start, goal


def _find_first_valid_node(grid_map: GridMap, x_values, y_values) -> Node:
    for y_value in y_values:
        for x_value in x_values:
            candidate = (x_value, y_value)
            if grid_map.is_valid_node(candidate):
                return candidate
    raise RuntimeError("Unable to locate a valid default node.")


def validate_or_default(grid_map: GridMap, candidate: Node | None, label: str, fallback: Node) -> Node:
    if candidate is None:
        return fallback

    validation = grid_map.validate_user_node(candidate)
    if not validation.is_valid:
        raise ValueError(f"Invalid {label} node {candidate}: {validation.message}")
    return candidate


def print_summary(search_result: SearchResult, output_path: str) -> None:
    print(f"Algorithm: {search_result.algorithm_name}")
    print(f"Start: {search_result.start}")
    print(f"Goal: {search_result.goal}")
    print(f"Runtime: {search_result.runtime_seconds:.6f} seconds")
    print(f"Explored nodes: {len(search_result.explored_order)}")
    print(f"Path length: {len(search_result.path)}")
    print(f"Path cost: {search_result.path_cost:.2f}")
    print(f"Output video: {output_path}")


def run_recording(default_algorithm: str | None = None, default_output: str | None = None) -> str:
    arguments = parse_arguments()
    grid_map = GridMap()
    default_start, default_goal = find_default_nodes(grid_map)

    start = validate_or_default(grid_map, tuple(arguments.start) if arguments.start else None, "start", default_start)
    goal = validate_or_default(grid_map, tuple(arguments.goal) if arguments.goal else None, "goal", default_goal)

    algorithm = default_algorithm or arguments.algorithm
    planner = build_planner(algorithm, grid_map)
    search_result = planner.search(start=start, goal=goal)
    if not search_result.success:
        raise RuntimeError("The planner failed to find a path from start to goal.")

    output_path = arguments.output or default_output or f"outputs/{algorithm}_animation.mp4"
    saved_path = Visualizer(grid_map).save_animation(
        search_result,
        output_path=output_path,
        interval=arguments.interval,
        fps=arguments.fps,
    )
    print_summary(search_result, saved_path)
    return saved_path


def main() -> None:
    run_recording()


if __name__ == "__main__":
    main()
