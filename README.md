# ENPM661 Project 02

This project implements backward BFS and backward Dijkstra for point robot path planning on a 2D grid map. The search always starts from the goal, stops when the start node is reached, and then backtracks a path from start to goal.

## Features

- `Backward BFS` on an 8-connected grid with unit cost for cardinal and diagonal moves.
- `Backward Dijkstra` on an 8-connected grid with `1.0` cost for cardinal moves and `1.4` cost for diagonal moves.
- `CCJ7196` text obstacle generated with matplotlib text rendering.
- `2 mm` wall inflation and obstacle inflation for clearance handling.
- Matplotlib GUI replay that starts only after the search finishes.
- MP4 recording script using `matplotlib.animation`.

## Project Structure

```text
src/
    map.py
    navigator.py
    bfs.py
    dijkstra.py
    visualizer.py

scripts/
    run_gui.py
    record_animation.py
    record_bfs_mp4.py
    record_dijkstra_mp4.py

BW-BFS_Che-Jung_Chuang.py
BW-dijkstra_Che-Jung_Chuang.py
README.md
pyproject.toml
```

## Map Configuration

- Workspace width: `180`
- Workspace height: `50`
- Robot radius: `0`
- Clearance: `2`
- Occupancy values:
  - `0` = free
  - `1` = obstacle or clearance

The planner accepts user coordinates in a bottom-left origin convention. Internally, the occupancy grid is stored as a NumPy 2D array in image coordinates, so the project includes explicit conversion functions between user coordinates and grid coordinates.

## Algorithms

### Backward BFS

Backward BFS uses a queue, a visited set, and a parent map:

1. Insert the goal node into the queue.
2. Expand neighbors in 8-connected space.
3. Stop when the start node is popped.
4. Backtrack from start to goal using the parent map.

### Backward Dijkstra

Backward Dijkstra uses a priority queue, a cost-to-come table, and a parent map:

1. Insert the goal node with cost `0`.
2. Pop the lowest-cost node.
3. Relax all valid neighbors.
4. Stop when the start node is popped.
5. Backtrack from start to goal using the parent map.

## Environment Setup

This project uses `uv` for environment management.

```bash
uv sync
```

## Dependencies

- `numpy`
- `matplotlib`

## Run the GUI

Run the generic GUI script and choose an algorithm interactively:

```bash
uv run python scripts/run_gui.py
```

Run the dedicated wrappers:

```bash
uv run python BW-BFS_Che-Jung_Chuang.py
uv run python BW-dijkstra_Che-Jung_Chuang.py
```

Optional command-line arguments:

```bash
uv run python scripts/run_gui.py --algorithm bfs --start 5 5 --goal 174 44
uv run python scripts/run_gui.py --algorithm dijkstra --start 5 5 --goal 174 44
```

## Record an MP4 Animation

The recording script runs the planner, replays the stored exploration order and path, and saves an MP4 file.

```bash
uv run python scripts/record_animation.py
```

Example with explicit arguments:

```bash
uv run python scripts/record_animation.py --algorithm bfs --start 5 5 --goal 174 44 --output outputs/bfs_animation.mp4

uv run python scripts/record_animation.py --algorithm dijkstra --start 5 5 --goal 174 44 --output outputs/dijkstra_animation.mp4
```

Dedicated MP4 scripts:

```bash
uv run python scripts/record_bfs_mp4.py --start 5 5 --goal 174 44
uv run python scripts/record_dijkstra_mp4.py --start 5 5 --goal 174 44
```

## Runtime Output

The terminal prints:

- runtime
- explored nodes
- path length
- path cost

## Notes

- Visualization starts only after the search completes.
- The recording script requires `ffmpeg` to be available on the system path for MP4 export.
