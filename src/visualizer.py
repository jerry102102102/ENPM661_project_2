"""Visualization and animation utilities."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

from .map import GridMap, Node
from .navigator import SearchResult


class Visualizer:
    """Animate explored nodes and the final path after planning completes."""

    def __init__(self, grid_map: GridMap) -> None:
        self.grid_map = grid_map

    def _nodes_to_offsets(self, nodes: list[Node]) -> np.ndarray:
        if not nodes:
            return np.empty((0, 2))

        offsets = [self.grid_map.user_to_plot(node) for node in nodes]
        return np.asarray(offsets, dtype=float)

    def _nodes_to_line(self, nodes: list[Node]) -> tuple[list[float], list[float]]:
        if not nodes:
            return [], []

        xs, ys = zip(*(self.grid_map.user_to_plot(node) for node in nodes), strict=False)
        return list(xs), list(ys)

    def _build_figure(self, search_result: SearchResult) -> tuple[plt.Figure, plt.Axes]:
        fig, ax = plt.subplots(figsize=(14, 5))
        colormap = ListedColormap(["white", "black"])

        ax.imshow(self.grid_map.occupancy_grid, cmap=colormap, origin="upper", interpolation="nearest")
        ax.set_title(
            f"{search_result.algorithm_name} | Runtime: {search_result.runtime_seconds:.4f} s | "
            f"Explored: {len(search_result.explored_order)} | Cost: {search_result.path_cost:.2f}"
        )
        ax.set_xlabel("X")
        ax.set_ylabel("Image Row")
        ax.set_xlim(-0.5, self.grid_map.width - 0.5)
        ax.set_ylim(self.grid_map.height - 0.5, -0.5)
        ax.set_aspect("equal")
        ax.grid(False)
        return fig, ax

    def create_animation(
        self,
        search_result: SearchResult,
        interval: int = 30,
        exploration_batch: int = 30,
        path_batch: int = 2,
    ) -> tuple[plt.Figure, animation.FuncAnimation]:
        fig, ax = self._build_figure(search_result)

        start_x, start_y = self.grid_map.user_to_plot(search_result.start)
        goal_x, goal_y = self.grid_map.user_to_plot(search_result.goal)
        ax.scatter([start_x], [start_y], s=60, c="limegreen", edgecolors="black", label="Start", zorder=3)
        ax.scatter([goal_x], [goal_y], s=60, c="gold", edgecolors="black", label="Goal", zorder=3)

        explored_artist = ax.scatter([], [], s=12, c="dodgerblue", marker="s", linewidths=0, label="Exploration")
        path_artist, = ax.plot([], [], color="crimson", linewidth=2.5, label="Path", zorder=4)
        ax.legend(loc="upper right")

        explored_nodes = search_result.explored_order
        path_nodes = search_result.path
        explore_frames = max(1, math.ceil(len(explored_nodes) / max(1, exploration_batch)))
        path_frames = max(1, math.ceil(max(1, len(path_nodes)) / max(1, path_batch)))
        total_frames = explore_frames + path_frames

        def update(frame_index: int):
            explored_count = min(len(explored_nodes), (frame_index + 1) * exploration_batch)
            explored_artist.set_offsets(self._nodes_to_offsets(explored_nodes[:explored_count]))

            if frame_index >= explore_frames - 1:
                path_frame_index = frame_index - explore_frames + 1
                path_count = min(len(path_nodes), max(0, path_frame_index) * path_batch)
                line_x, line_y = self._nodes_to_line(path_nodes[:path_count])
                path_artist.set_data(line_x, line_y)

            return explored_artist, path_artist

        animation_handle = animation.FuncAnimation(
            fig,
            update,
            frames=total_frames,
            interval=interval,
            blit=False,
            repeat=False,
        )
        return fig, animation_handle

    def show_animation(self, search_result: SearchResult) -> None:
        fig, animation_handle = self.create_animation(search_result)
        fig._animation_handle = animation_handle  # type: ignore[attr-defined]
        plt.show()

    def save_animation(
        self,
        search_result: SearchResult,
        output_path: str,
        interval: int = 30,
        fps: int = 30,
    ) -> str:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        if not animation.writers.is_available("ffmpeg"):
            raise RuntimeError(
                "ffmpeg is required to save MP4 animations. "
                "Install ffmpeg and rerun the recording script. "
                "On macOS with Homebrew, use: brew install ffmpeg"
            )

        fig, animation_handle = self.create_animation(search_result, interval=interval)
        writer = animation.FFMpegWriter(fps=fps, metadata={"artist": "Che-Jung Chuang"})
        animation_handle.save(output.as_posix(), writer=writer)
        plt.close(fig)
        return output.as_posix()
