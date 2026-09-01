import time
import cv2

import config

from core.video_source import VideoSource
from core.tracker import MultiObjectTracker

from analytics.trajectory import TrajectoryManager

from utils.drawing import (
    draw_object,
    draw_trajectory
)


def main():

    video = VideoSource(
        config.VIDEO_SOURCE
    )

    tracker = (
        MultiObjectTracker()
    )

    trajectories = (
        TrajectoryManager()
    )


    video.open()


    previous_time = time.time()


    while True:

        success, frame = video.read()

        if not success:
            break


        objects = tracker.track(
            frame
        )


        active_ids = set()


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


            draw_trajectory(
                frame,
                points
            )


            draw_object(
                frame,
                obj,
                direction
            )


        current_time = time.time()

        elapsed = (
            current_time
            -
            previous_time
        )


        if elapsed > 0:

            fps = 1 / elapsed

        else:

            fps = 0


        previous_time = (
            current_time
        )


        cv2.putText(
            frame,
            f"Active Objects: {len(active_ids)}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )


        cv2.putText(
            frame,
            f"FPS: {fps:.1f}",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )


        cv2.imshow(
            "VisionTrack - Multi Object Tracking",
            frame
        )


        key = (
            cv2.waitKey(1)
            &
            0xFF
        )


        if key == ord("q"):
            break


    video.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":

    main()