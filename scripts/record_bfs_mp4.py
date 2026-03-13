"""Record a backward BFS animation to MP4."""

from record_animation import run_recording


if __name__ == "__main__":
    run_recording(default_algorithm="bfs", default_output="outputs/backward_bfs.mp4")
