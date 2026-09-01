import time
import cv2

import config

from core.video_source import VideoSource
from core.tracker import MultiObjectTracker

from analytics.trajectory import TrajectoryManager
from analytics.line_counter import LineCounter

from utils.drawing import (
    draw_object,
    draw_trajectory,
    draw_counting_line,
    draw_statistics
)


def main():

    # ==============================
    # Initialize modules
    # ==============================

    video = VideoSource(
        config.VIDEO_SOURCE
    )

    tracker = MultiObjectTracker()

    trajectories = TrajectoryManager()

    line_counter = LineCounter()

    video.open()

    previous_time = time.time()

    frame_index = 0


    # ==============================
    # Main processing loop
    # ==============================

    while True:

        success, frame = video.read()

        if not success:
            break

        frame_index += 1

        frame_height = frame.shape[0]


        # ==============================
        # Multi-object tracking
        # ==============================

        objects = tracker.track(
            frame
        )

        active_ids = set()


        # ==============================
        # Process each tracked object
        # ==============================

        for obj in objects:

            track_id = obj[
                "track_id"
            ]

            centroid = obj[
                "centroid"
            ]

            active_ids.add(
                track_id
            )


            # --------------------------
            # Trajectory
            # --------------------------

            trajectories.update(
                track_id,
                centroid
            )

            direction = (
                trajectories.get_direction(
                    track_id
                )
            )

            points = (
                trajectories.get_trajectory(
                    track_id
                )
            )


            # --------------------------
            # Line crossing
            # --------------------------

            event = line_counter.update(
                track_id=track_id,
                centroid=centroid,
                frame_index=frame_index,
                frame_height=frame_height
            )


            if event is not None:

                print(
                    f"[EVENT] "
                    f"Object {track_id} "
                    f"crossed {event}"
                )


            # --------------------------
            # Draw trajectory
            # --------------------------

            draw_trajectory(
                frame,
                points
            )


            # --------------------------
            # Draw object
            # --------------------------

            draw_object(
                frame,
                obj,
                direction
            )


            # Show crossing event briefly
            # on the exact frame it occurs.

            if event is not None:

                x1, y1, _, _ = obj[
                    "bbox"
                ]

                cv2.putText(
                    frame,
                    f"CROSSED: {event}",
                    (
                        x1,
                        max(
                            40,
                            y1 - 35
                        )
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )


        # ==============================
        # Clean old tracking information
        # ==============================

        line_counter.cleanup(
            frame_index
        )


        # ==============================
        # FPS calculation
        # ==============================

        current_time = time.time()

        elapsed = (
            current_time
            -
            previous_time
        )

        fps = (
            1 / elapsed
            if elapsed > 0
            else 0
        )

        previous_time = (
            current_time
        )


        # ==============================
        # Counting line
        # ==============================

        line_y = (
            line_counter.get_line_y(
                frame_height
            )
        )

        draw_counting_line(
            frame,
            line_y
        )


        # ==============================
        # Statistics
        # ==============================

        draw_statistics(
            frame=frame,
            active_objects=len(
                active_ids
            ),
            total_in=line_counter.total_in,
            total_out=line_counter.total_out,
            fps=fps
        )


        # ==============================
        # Display
        # ==============================

        cv2.imshow(
            "VisionTrack - MOT Analytics",
            frame
        )


        key = (
            cv2.waitKey(1)
            &
            0xFF
        )

        if key == ord("q"):
            break


    # ==============================
    # Cleanup
    # ==============================

    video.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()