import time

import cv2

import config

from core.video_source import VideoSource
from core.tracker import MultiObjectTracker

from analytics.trajectory import TrajectoryManager
from analytics.line_counter import LineCounter
from analytics.zone_monitor import ZoneMonitor

from storage.event_logger import EventLogger
from storage.snapshot_manager import SnapshotManager
from storage.video_recorder import VideoRecorder

from utils.drawing import (
    draw_object,
    draw_trajectory,
    draw_counting_line,
    draw_statistics,
    draw_zone,
    draw_zone_status,
    draw_event_history
)


# ==========================================
# Stream Timestamp
# ==========================================

def get_stream_timestamp(
    frame_index,
    source_fps,
    source,
    live_start_time
):

    # Live webcam
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


# ==========================================
# Standard Event Structure
# ==========================================

def build_event(
    event_type,
    obj,
    frame_index,
    timestamp,
    direction,
    zone="",
    dwell_time=0.0
):

    cx, cy = obj[
        "centroid"
    ]


    return {

        "frame_index":
            frame_index,

        "timestamp_seconds":
            round(
                timestamp,
                3
            ),

        "event_type":
            event_type,

        "track_id":
            obj[
                "track_id"
            ],

        "class_name":
            obj[
                "class_name"
            ],

        "zone":
            zone,

        "direction":
            direction,

        "dwell_time":
            round(
                dwell_time,
                3
            ),

        "centroid_x":
            cx,

        "centroid_y":
            cy
    }


# ==========================================
# Main Application
# ==========================================

def main():

    # --------------------------------------
    # Core modules
    # --------------------------------------

    video = VideoSource(
        config.VIDEO_SOURCE
    )

    tracker = (
        MultiObjectTracker()
    )

    trajectories = (
        TrajectoryManager()
    )

    line_counter = (
        LineCounter()
    )

    zone_monitor = (
        ZoneMonitor()
    )


    # --------------------------------------
    # Persistence modules
    # --------------------------------------

    event_logger = (
        EventLogger()
    )

    snapshot_manager = (
        SnapshotManager()
    )

    video_recorder = (
        VideoRecorder()
    )


    # --------------------------------------
    # Open video source
    # --------------------------------------

    video.open()


    source_fps = (
        video.get_fps()
    )


    live_start_time = (
        time.monotonic()
    )


    previous_time = (
        time.time()
    )


    frame_index = 0

    recorder_initialized = False


    # ======================================
    # Main processing loop
    # ======================================

    while True:

        success, frame = (
            video.read()
        )


        if not success:
            break


        frame_index += 1


        frame_height = (
            frame.shape[0]
        )

        frame_width = (
            frame.shape[1]
        )


        # ----------------------------------
        # Initialize output recorder
        # ----------------------------------

        if not recorder_initialized:

            video_recorder.open(
                frame_width=
                    frame_width,

                frame_height=
                    frame_height,

                fps=
                    source_fps
            )

            recorder_initialized = True


        # ----------------------------------
        # Stream timestamp
        # ----------------------------------

        timestamp = (
            get_stream_timestamp(
                frame_index,
                source_fps,
                config.VIDEO_SOURCE,
                live_start_time
            )
        )


        # ----------------------------------
        # Draw zones
        # ----------------------------------

        for zone_name in config.ZONES:

            polygon = (
                zone_monitor
                .get_pixel_polygon(
                    zone_name,
                    frame_width,
                    frame_height
                )
            )


            zone_counts = (
                zone_monitor
                .get_zone_counts(
                    zone_name
                )
            )


            draw_zone(
                frame,
                zone_name,
                polygon,
                entries=
                    zone_counts[
                        "entries"
                    ],
                exits=
                    zone_counts[
                        "exits"
                    ]
            )


        # ----------------------------------
        # MOT
        # ----------------------------------

        objects = tracker.track(
            frame
        )


        active_ids = set()


        # ==================================
        # Process each object
        # ==================================

        for obj in objects:

            track_id = (
                obj[
                    "track_id"
                ]
            )

            centroid = (
                obj[
                    "centroid"
                ]
            )


            active_ids.add(
                track_id
            )


            # ------------------------------
            # Trajectory
            # ------------------------------

            trajectories.update(
                track_id,
                centroid
            )


            direction = (
                trajectories
                .get_direction(
                    track_id
                )
            )


            points = (
                trajectories
                .get_trajectory(
                    track_id
                )
            )


            # ------------------------------
            # Line crossing
            # ------------------------------

            line_event = (
                line_counter.update(
                    track_id=
                        track_id,

                    centroid=
                        centroid,

                    frame_index=
                        frame_index,

                    frame_height=
                        frame_height
                )
            )


            # ------------------------------
            # Zone monitoring
            # ------------------------------

            (
                zone_events,
                zone_status
            ) = zone_monitor.update(

                track_id=
                    track_id,

                centroid=
                    centroid,

                timestamp=
                    timestamp,

                frame_index=
                    frame_index,

                frame_width=
                    frame_width,

                frame_height=
                    frame_height
            )


            # ------------------------------
            # Draw tracking information
            # ------------------------------

            draw_trajectory(
                frame,
                points
            )


            draw_object(
                frame,
                obj,
                direction
            )


            # ------------------------------
            # Current dwell time
            # ------------------------------

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


            # ==============================
            # LINE EVENT
            # ==============================

            if line_event is not None:

                event_type = (
                    f"LINE_{line_event}"
                )


                event = build_event(
                    event_type=
                        event_type,

                    obj=
                        obj,

                    frame_index=
                        frame_index,

                    timestamp=
                        timestamp,

                    direction=
                        direction
                )


                event_logger.log(
                    event
                )


                snapshot_manager.save(
                    frame=
                        frame,

                    event_type=
                        event_type,

                    track_id=
                        track_id,

                    frame_index=
                        frame_index
                )


                print(
                    f"[{event_type}] "
                    f"ID {track_id} "
                    f"{obj['class_name']} "
                    f"at "
                    f"{timestamp:.2f}s"
                )


                x1, y1, _, _ = (
                    obj[
                        "bbox"
                    ]
                )


                cv2.putText(
                    frame,
                    f"CROSSED: "
                    f"{line_event}",
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
            # ZONE EVENTS
            # ==============================

            for zone_event in zone_events:

                event_type = (
                    zone_event[
                        "type"
                    ]
                )


                zone_name = (
                    zone_event[
                        "zone"
                    ]
                )


                dwell_time = (
                    zone_event[
                        "dwell_time"
                    ]
                )


                event = build_event(
                    event_type=
                        event_type,

                    obj=
                        obj,

                    frame_index=
                        frame_index,

                    timestamp=
                        timestamp,

                    direction=
                        direction,

                    zone=
                        zone_name,

                    dwell_time=
                        dwell_time
                )


                event_logger.log(
                    event
                )


                snapshot_manager.save(
                    frame=
                        frame,

                    event_type=
                        event_type,

                    track_id=
                        track_id,

                    frame_index=
                        frame_index
                )


                if (
                    event_type
                    ==
                    "ZONE_ENTRY"
                ):

                    print(
                        f"[ZONE ENTRY] "
                        f"ID {track_id} "
                        f"entered "
                        f"{zone_name}"
                    )


                elif (
                    event_type
                    ==
                    "ZONE_EXIT"
                ):

                    print(
                        f"[ZONE EXIT] "
                        f"ID {track_id} "
                        f"left "
                        f"{zone_name} "
                        f"after "
                        f"{dwell_time:.2f}s"
                    )


        # ==================================
        # Cleanup old track state
        # ==================================

        line_counter.cleanup(
            frame_index
        )


        zone_monitor.cleanup(
            frame_index
        )


        # ==================================
        # FPS
        # ==================================

        current_time = (
            time.time()
        )


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


        # ==================================
        # Counting line
        # ==================================

        line_y = (
            line_counter
            .get_line_y(
                frame_height
            )
        )


        draw_counting_line(
            frame,
            line_y
        )


        # ==================================
        # Statistics
        # ==================================

        draw_statistics(
            frame=
                frame,

            active_objects=
                len(
                    active_ids
                ),

            total_in=
                line_counter
                .total_in,

            total_out=
                line_counter
                .total_out,

            fps=
                fps
        )


        # ==================================
        # Event history
        # ==================================

        recent_events = (
            zone_monitor
            .get_recent_events(
                limit=6
            )
        )


        draw_event_history(
            frame,
            recent_events
        )


        # ==================================
        # Record processed frame
        # ==================================

        video_recorder.write(
            frame
        )


        # ==================================
        # Display
        # ==================================

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


    # ======================================
    # Shutdown
    # ======================================

    video.release()

    video_recorder.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":

    main()