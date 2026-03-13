"""Backward BFS implementation."""

from __future__ import annotations

import time
from collections import deque

from .map import Node
from .navigator import Navigator, SearchResult


class BackwardBFS(Navigator):
    """Backward breadth-first search for an 8-connected grid."""

    def __init__(self, grid_map) -> None:
        super().__init__(grid_map, "Backward BFS")

    def _movement_cost(self, dx: int, dy: int) -> float:
        if (dx, dy) in {(1, 0), (0, 1), (1, 1)}:
            return 1.0
        raise ValueError(f"Unsupported motion delta: {(dx, dy)}")

    def search(self, start: Node, goal: Node) -> SearchResult:
        self.validate_endpoints(start, goal)
        self.reset_search_state()

        queue = deque([goal])
        visited = {goal}
        self.parent_map[goal] = None

        success = False
        start_time = time.perf_counter()

        while queue:
            current = queue.popleft()
            self.explored_order.append(current)

            if self.is_start_node(current, start):
                success = True
                break

            for neighbor in self.iter_neighbors(current):
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                self.parent_map[neighbor] = current
                queue.append(neighbor)

        runtime_seconds = time.perf_counter() - start_time
        path = self.backtrack_path(start, goal) if success else []
        path_cost = self.compute_path_cost(path)

        return SearchResult(
            algorithm_name=self.algorithm_name,
            start=start,
            goal=goal,
            path=path,
            explored_order=self.explored_order.copy(),
            path_cost=path_cost,
            runtime_seconds=runtime_seconds,
            success=success,
        )
