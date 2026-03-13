"""Record a backward Dijkstra animation to MP4."""

from record_animation import run_recording


if __name__ == "__main__":
    run_recording(default_algorithm="dijkstra", default_output="outputs/backward_dijkstra.mp4")
