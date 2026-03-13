"""Planner base classes for backward search."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from .map import GridMap

Node = Tuple[int, int]


@dataclass
class SearchResult:
    """Container for planner output."""

    algorithm_name: str
    start: Node
    goal: Node
    path: list[Node]
    explored_order: list[Node]
    path_cost: float
    runtime_seconds: float
    success: bool


class Navigator:
    """Base class for backward graph search planners."""

    def __init__(self, grid_map: GridMap, algorithm_name: str) -> None:
        self.grid_map = grid_map
        self.algorithm_name = algorithm_name
        self.parent_map: dict[Node, Optional[Node]] = {}
        self.explored_order: list[Node] = []
        self.action_set = [
            self.move_right,
            self.move_left,
            self.move_up,
            self.move_down,
            self.move_up_right,
            self.move_up_left,
            self.move_down_right,
            self.move_down_left,
        ]

    def reset_search_state(self) -> None:
        self.parent_map = {}
        self.explored_order = []

    def validate_endpoints(self, start: Node, goal: Node) -> None:
        start_validation = self.grid_map.validate_user_node(start)
        if not start_validation.is_valid:
            raise ValueError(f"Invalid start node: {start_validation.message}")

        goal_validation = self.grid_map.validate_user_node(goal)
        if not goal_validation.is_valid:
            raise ValueError(f"Invalid goal node: {goal_validation.message}")

    def is_start_node(self, node: Node, start: Node) -> bool:
        return node == start

    def _move(self, node: Node, dx: int, dy: int) -> Optional[Node]:
        candidate = (node[0] + dx, node[1] + dy)
        if self.grid_map.is_valid_node(candidate):
            return candidate
        return None

    def move_right(self, node: Node) -> Optional[Node]:
        return self._move(node, 1, 0)

    def move_left(self, node: Node) -> Optional[Node]:
        return self._move(node, -1, 0)

    def move_up(self, node: Node) -> Optional[Node]:
        return self._move(node, 0, 1)

    def move_down(self, node: Node) -> Optional[Node]:
        return self._move(node, 0, -1)

    def move_up_right(self, node: Node) -> Optional[Node]:
        return self._move(node, 1, 1)

    def move_up_left(self, node: Node) -> Optional[Node]:
        return self._move(node, -1, 1)

    def move_down_right(self, node: Node) -> Optional[Node]:
        return self._move(node, 1, -1)

    def move_down_left(self, node: Node) -> Optional[Node]:
        return self._move(node, -1, -1)

    def iter_neighbors(self, node: Node) -> list[Node]:
        neighbors: list[Node] = []
        for action in self.action_set:
            candidate = action(node)
            if candidate is not None:
                neighbors.append(candidate)
        return neighbors

    def transition_cost(self, current: Node, neighbor: Node) -> float:
        dx = abs(neighbor[0] - current[0])
        dy = abs(neighbor[1] - current[1])
        return self._movement_cost(dx, dy)

    def _movement_cost(self, dx: int, dy: int) -> float:
        raise NotImplementedError

    def backtrack_path(self, start: Node, goal: Node) -> list[Node]:
        if start not in self.parent_map:
            return []

        path = [start]
        current = start
        while current != goal:
            next_node = self.parent_map.get(current)
            if next_node is None:
                raise RuntimeError("Backtracking failed before reaching the goal.")
            path.append(next_node)
            current = next_node
        return path

    def compute_path_cost(self, path: list[Node]) -> float:
        if len(path) < 2:
            return 0.0

        total_cost = 0.0
        for current, neighbor in zip(path[:-1], path[1:], strict=False):
            total_cost += self.transition_cost(current, neighbor)
        return total_cost

    def search(self, start: Node, goal: Node) -> SearchResult:
        raise NotImplementedError
