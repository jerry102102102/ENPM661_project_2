"""Grid map construction for ENPM661 Project 02."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path
from matplotlib.textpath import TextPath
from matplotlib.transforms import Affine2D

Node = Tuple[int, int]


@dataclass(frozen=True)
class NodeValidation:
    """Validation result for a user-provided map node."""

    is_valid: bool
    message: str


class GridMap:
    """Create and query the occupancy map."""

    def __init__(
        self,
        width: int = 180,
        height: int = 50,
        robot_radius: int = 0,
        clearance: int = 2,
        obstacle_text: str = "CCJ7196",
    ) -> None:
        self.width = width
        self.height = height
        self.robot_radius = robot_radius
        self.clearance = clearance
        self.total_clearance = robot_radius + clearance
        self.obstacle_text = obstacle_text

        self.wall_mask = np.zeros((self.height, self.width), dtype=bool)
        self.text_mask = np.zeros((self.height, self.width), dtype=bool)
        self.inflated_text_mask = np.zeros((self.height, self.width), dtype=bool)
        self.occupancy_grid = np.zeros((self.height, self.width), dtype=np.uint8)
        self._build_map()

    def _build_map(self) -> None:
        self.wall_mask = self._create_wall_mask()
        self.text_mask = self._create_text_mask()
        self.inflated_text_mask = self._inflate_mask(self.text_mask, self.total_clearance)
        occupied = self.wall_mask | self.inflated_text_mask
        self.occupancy_grid = occupied.astype(np.uint8)

    def _create_wall_mask(self) -> np.ndarray:
        mask = np.zeros((self.height, self.width), dtype=bool)
        if self.total_clearance <= 0:
            return mask

        border = self.total_clearance
        mask[:border, :] = True
        mask[-border:, :] = True
        mask[:, :border] = True
        mask[:, -border:] = True
        return mask

    def _create_text_mask(self) -> np.ndarray:
        path = self._create_text_path()
        grid_x, grid_y = np.meshgrid(np.arange(self.width), np.arange(self.height))
        user_y = self.height - 1 - grid_y
        points = np.column_stack((grid_x.ravel(), user_y.ravel()))
        mask = path.contains_points(points).reshape(self.height, self.width)
        return mask

    def _create_text_path(self) -> Path:
        font = FontProperties(family="DejaVu Sans", weight="bold")
        text_path = TextPath((0.0, 0.0), self.obstacle_text, size=1.0, prop=font)
        bbox = text_path.get_extents()

        horizontal_margin = self.total_clearance + 10
        vertical_margin = self.total_clearance + 7
        available_width = self.width - (2 * horizontal_margin)
        available_height = self.height - (2 * vertical_margin)
        scale = min(available_width / bbox.width, available_height / bbox.height)

        translate_x = (self.width - (bbox.width * scale)) / 2.0 - (bbox.x0 * scale)
        translate_y = (self.height - (bbox.height * scale)) / 2.0 - (bbox.y0 * scale)
        transform = Affine2D().scale(scale).translate(translate_x, translate_y)
        return text_path.transformed(transform)

    def _inflate_mask(self, mask: np.ndarray, inflation_radius: int) -> np.ndarray:
        if inflation_radius <= 0:
            return mask.copy()

        inflated = mask.copy()
        offsets = self._disk_offsets(inflation_radius)
        rows, cols = np.nonzero(mask)

        for row, col in zip(rows, cols, strict=False):
            for dx, dy in offsets:
                next_row = row - dy
                next_col = col + dx
                if 0 <= next_row < self.height and 0 <= next_col < self.width:
                    inflated[next_row, next_col] = True

        return inflated

    @staticmethod
    def _disk_offsets(radius: int) -> list[Node]:
        offsets: list[Node] = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if (dx * dx) + (dy * dy) <= radius * radius:
                    offsets.append((dx, dy))
        return offsets

    def user_to_grid(self, node: Node) -> tuple[int, int]:
        x, y = node
        return self.height - 1 - y, x

    def grid_to_user(self, row: int, col: int) -> Node:
        return col, self.height - 1 - row

    def user_to_plot(self, node: Node) -> tuple[int, int]:
        x, y = node
        return x, self.height - 1 - y

    def is_within_bounds(self, node: Node) -> bool:
        x, y = node
        return 0 <= x < self.width and 0 <= y < self.height

    def is_obstacle(self, node: Node) -> bool:
        if not self.is_within_bounds(node):
            return True
        row, col = self.user_to_grid(node)
        return bool(self.occupancy_grid[row, col])

    def is_valid_node(self, node: Node) -> bool:
        return self.is_within_bounds(node) and not self.is_obstacle(node)

    def validate_user_node(self, node: Node) -> NodeValidation:
        if not self.is_within_bounds(node):
            return NodeValidation(False, "Node is outside the map bounds.")
        if self.is_obstacle(node):
            return NodeValidation(False, "Node is inside an obstacle or clearance region.")
        return NodeValidation(True, "Node is valid.")
