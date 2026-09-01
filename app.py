import time

import cv2

import config

from core.video_source import VideoSource
from core.tracker import MultiObjectTracker

from analytics.trajectory import TrajectoryManager
from analytics.line_counter import LineCounter
from analytics.zone_monitor import ZoneMonitor

from utils.drawing import (
    draw_object,
    draw_trajectory,
    draw_counting_line,
    draw_statistics,
    draw_zone,
    draw_zone_status,
    draw_event_history
)


def get_stream_timestamp(
    frame_index,
    source_fps,
    source,
    live_start_time
):

    # Webcam / local live camera
    if isinstance(
        source,
        int
    ):

        return (
            time.monotonic()
            -
            live_start_time
        )


    # Recorded video
    if (
        source_fps is not None
        and
        source_fps > 1
    ):

        return (
            frame_index
            /
            source_fps
        )


    # Fallback
    return (
        time.monotonic()
        -
        live_start_time
    )


def main():

    # ==========================================
    # Initialize modules
    # ==========================================

    video = VideoSource(
        config.VIDEO_SOURCE
    )

    tracker = MultiObjectTracker()

    trajectories = TrajectoryManager()

    line_counter = LineCounter()

    zone_monitor = ZoneMonitor()


    video.open()


    source_fps = video.get_fps()

    live_start_time = time.monotonic()

    previous_time = time.time()

    frame_index = 0


    # ==========================================
    # Main loop
    # ==========================================

    while True:

        success, frame = video.read()

        if not success:
            break


        frame_index += 1


        frame_height = frame.shape[0]

        frame_width = frame.shape[1]


        # ======================================
        # Stream timestamp
        # ======================================

        timestamp = (
            get_stream_timestamp(
                frame_index,
                source_fps,
                config.VIDEO_SOURCE,
                live_start_time
            )
        )


        # ======================================
        # Draw polygon zones
        # ======================================

        for zone_name in config.ZONES:

            polygon = (
                zone_monitor.get_pixel_polygon(
                    zone_name,
                    frame_width,
                    frame_height
                )
            )


            zone_counts = (
                zone_monitor.get_zone_counts(
                    zone_name
                )
            )


            draw_zone(
                frame,
                zone_name,
                polygon,
                entries=zone_counts[
                    "entries"
                ],
                exits=zone_counts[
                    "exits"
                ]
            )


        # ======================================
        # Multi-object tracking
        # ======================================

        objects = tracker.track(
            frame
        )


        active_ids = set()


        # ======================================
        # Process tracked objects
        # ======================================

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


            # ----------------------------------
            # Trajectory
            # ----------------------------------

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


            # ----------------------------------
            # Line crossing
            # ----------------------------------

            line_event = (
                line_counter.update(
                    track_id=track_id,
                    centroid=centroid,
                    frame_index=frame_index,
                    frame_height=frame_height
                )
            )


            if line_event is not None:

                print(
                    f"[LINE EVENT] "
                    f"ID {track_id} "
                    f"{line_event}"
                )


            # ----------------------------------
            # Polygon zone monitoring
            # ----------------------------------

            (
                zone_events,
                zone_status
            ) = zone_monitor.update(

                track_id=track_id,

                centroid=centroid,

                timestamp=timestamp,

                frame_index=frame_index,

                frame_width=frame_width,

                frame_height=frame_height
            )


            # ----------------------------------
            # Print zone events
            # ----------------------------------

            for event in zone_events:

                if (
                    event["type"]
                    ==
                    "ZONE_ENTRY"
                ):

                    print(
                        f"[ZONE ENTRY] "
                        f"ID {track_id} "
                        f"entered "
                        f"{event['zone']}"
                    )


                elif (
                    event["type"]
                    ==
                    "ZONE_EXIT"
                ):

                    print(
                        f"[ZONE EXIT] "
                        f"ID {track_id} "
                        f"left "
                        f"{event['zone']} "
                        f"after "
                        f"{event['dwell_time']:.2f}s"
                    )


            # ----------------------------------
            # Draw trajectory
            # ----------------------------------

            draw_trajectory(
                frame,
                points
            )


            # ----------------------------------
            # Draw tracked object
            # ----------------------------------

            draw_object(
                frame,
                obj,
                direction
            )


            # ----------------------------------
            # Show current zone dwell
            # ----------------------------------

            for (
                zone_name,
                status
            ) in zone_status.items():

                if status[
                    "inside"
                ]:

                    draw_zone_status(
                        frame,
                        centroid,
                        zone_name,
                        status[
                            "dwell_time"
                        ]
                    )


            # ----------------------------------
            # Highlight line crossing event
            # ----------------------------------

            if line_event is not None:

                x1, y1, _, _ = obj[
                    "bbox"
                ]


                cv2.putText(
                    frame,
                    f"CROSSED: {line_event}",
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


        # ======================================
        # Cleanup old tracks
        # ======================================

        line_counter.cleanup(
            frame_index
        )


        zone_monitor.cleanup(
            frame_index
        )


        # ======================================
        # FPS
        # ======================================

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


        previous_time = current_time


        # ======================================
        # Counting line
        # ======================================

        line_y = (
            line_counter.get_line_y(
                frame_height
            )
        )


        draw_counting_line(
            frame,
            line_y
        )


        # ======================================
        # Statistics
        # ======================================

        draw_statistics(
            frame=frame,
            active_objects=len(
                active_ids
            ),
            total_in=
                line_counter.total_in,
            total_out=
                line_counter.total_out,
            fps=fps
        )


        # ======================================
        # Event history
        # ======================================

        recent_events = (
            zone_monitor.get_recent_events(
                limit=6
            )
        )


        draw_event_history(
            frame,
            recent_events
        )


        # ======================================
        # Display
        # ======================================

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


    # ==========================================
    # Shutdown
    # ==========================================

    video.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":

    main()