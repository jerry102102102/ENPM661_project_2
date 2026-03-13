"""Backward Dijkstra implementation."""

from __future__ import annotations

import heapq
import math
import time

from .map import Node
from .navigator import Navigator, SearchResult


class BackwardDijkstra(Navigator):
    """Backward Dijkstra search for an 8-connected grid."""

    def __init__(self, grid_map) -> None:
        super().__init__(grid_map, "Backward Dijkstra")

    def _movement_cost(self, dx: int, dy: int) -> float:
        if (dx, dy) in {(1, 0), (0, 1)}:
            return 1.0
        if (dx, dy) == (1, 1):
            return 1.4
        raise ValueError(f"Unsupported motion delta: {(dx, dy)}")

    def search(self, start: Node, goal: Node) -> SearchResult:
        self.validate_endpoints(start, goal)
        self.reset_search_state()

        heap: list[tuple[float, int, Node]] = [(0.0, 0, goal)]
        push_index = 1
        best_costs: dict[Node, float] = {goal: 0.0}
        expanded: set[Node] = set()
        self.parent_map[goal] = None

        success = False
        start_time = time.perf_counter()

        while heap:
            current_cost, _, current = heapq.heappop(heap)

            if current in expanded:
                continue
            if current_cost > best_costs.get(current, math.inf):
                continue

            expanded.add(current)
            self.explored_order.append(current)

            if self.is_start_node(current, start):
                success = True
                break

            for neighbor in self.iter_neighbors(current):
                new_cost = current_cost + self.transition_cost(current, neighbor)
                if new_cost >= best_costs.get(neighbor, math.inf):
                    continue

                best_costs[neighbor] = new_cost
                self.parent_map[neighbor] = current
                heapq.heappush(heap, (new_cost, push_index, neighbor))
                push_index += 1

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
