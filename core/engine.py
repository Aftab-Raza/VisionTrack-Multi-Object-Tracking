import math
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
from storage.database import DatabaseManager

from utils.drawing import (
    draw_object,
    draw_trajectory,
    draw_counting_line,
    draw_statistics,
    draw_zone,
    draw_zone_status,
    draw_event_history
)


class VisionTrackEngine:

    def __init__(self, source):

        self.source = source

        # Core
        self.video = VideoSource(source)
        self.tracker = MultiObjectTracker()

        # Analytics
        self.trajectories = TrajectoryManager()
        self.line_counter = LineCounter()
        self.zone_monitor = ZoneMonitor()

        # Persistence
        self.event_logger = EventLogger()
        self.snapshot_manager = SnapshotManager()
        self.video_recorder = VideoRecorder()
        self.database = DatabaseManager()

        # Runtime state
        self.source_fps = None
        self.frame_index = 0
        self.session_id = None

        self.live_start_time = None
        self.previous_time = None

        self.current_fps = 0.0

        self.recorder_initialized = False
        self.started = False
        self.stopped = False


    # ==========================================
    # Start Engine
    # ==========================================

    def start(self):

        self.video.open()

        self.source_fps = self.video.get_fps()

        self.live_start_time = time.monotonic()

        self.previous_time = time.perf_counter()

        self.started = True


    # ==========================================
    # Timestamp
    # ==========================================

    def _get_timestamp(self):

        # Live camera
        if isinstance(self.source, int):

            return (
                time.monotonic()
                -
                self.live_start_time
            )

        # Recorded video
        if (
            self.source_fps is not None
            and
            math.isfinite(self.source_fps)
            and
            self.source_fps > 1
        ):

            return (
                self.frame_index
                /
                self.source_fps
            )

        # Fallback
        return (
            time.monotonic()
            -
            self.live_start_time
        )


    # ==========================================
    # Standard Event Structure
    # ==========================================

    def _build_event(
        self,
        event_type,
        obj,
        timestamp,
        direction,
        zone="",
        dwell_time=0.0
    ):

        cx, cy = obj["centroid"]

        return {

            "frame_index":
                self.frame_index,

            "timestamp_seconds":
                round(timestamp, 3),

            "event_type":
                event_type,

            "track_id":
                obj["track_id"],

            "class_name":
                obj["class_name"],

            "zone":
                zone,

            "direction":
                direction,

            "dwell_time":
                round(dwell_time, 3),

            "centroid_x":
                cx,

            "centroid_y":
                cy
        }


    # ==========================================
    # Persist Event
    # ==========================================

    def _persist_event(
        self,
        event,
        frame
    ):

        snapshot_path = (
            self.snapshot_manager.save(

                frame=frame,

                event_type=
                    event["event_type"],

                track_id=
                    event["track_id"],

                frame_index=
                    event["frame_index"]
            )
        )

        event["snapshot_path"] = (
            snapshot_path
        )

        self.event_logger.log(event)

        self.database.log_event(
            session_id=self.session_id,
            event=event,
            snapshot_path=snapshot_path
        )


    # ==========================================
    # FPS
    # ==========================================

    def _update_fps(self):

        current_time = (
            time.perf_counter()
        )

        elapsed = (
            current_time
            -
            self.previous_time
        )

        self.previous_time = (
            current_time
        )

        if elapsed <= 0:
            return

        instant_fps = (
            1.0 / elapsed
        )

        # Smooth FPS instead of showing
        # highly unstable per-frame values.
        if self.current_fps == 0:

            self.current_fps = (
                instant_fps
            )

        else:

            self.current_fps = (
                0.90
                *
                self.current_fps
                +
                0.10
                *
                instant_fps
            )


    # ==========================================
    # Process One Frame
    # ==========================================

    def process_next_frame(self):

        if not self.started:

            raise RuntimeError(
                "VisionTrack engine "
                "has not been started."
            )


        success, frame = (
            self.video.read()
        )


        if not success:

            return None


        self.frame_index += 1


        frame_height = frame.shape[0]

        frame_width = frame.shape[1]


        # ======================================
        # Create DB session on first frame
        # ======================================

        if self.session_id is None:

            self.session_id = (
                self.database.start_session(

                    source=
                        self.source,

                    source_fps=
                        self.source_fps,

                    frame_width=
                        frame_width,

                    frame_height=
                        frame_height
                )
            )


        # ======================================
        # Initialize video recorder
        # ======================================

        if not self.recorder_initialized:

            self.video_recorder.open(

                frame_width=
                    frame_width,

                frame_height=
                    frame_height,

                fps=
                    self.source_fps
            )

            self.recorder_initialized = (
                True
            )


        timestamp = (
            self._get_timestamp()
        )


        # ======================================
        # Draw configured zones
        # ======================================

        for zone_name in config.ZONES:

            polygon = (
                self.zone_monitor
                .get_pixel_polygon(

                    zone_name,
                    frame_width,
                    frame_height
                )
            )


            counts = (
                self.zone_monitor
                .get_zone_counts(
                    zone_name
                )
            )


            draw_zone(

                frame,
                zone_name,
                polygon,

                entries=
                    counts["entries"],

                exits=
                    counts["exits"]
            )


        # ======================================
        # Multi-object tracking
        # ======================================

        objects = (
            self.tracker.track(
                frame
            )
        )


        active_ids = set()

        frame_events = []


        # ======================================
        # Process Objects
        # ======================================

        for obj in objects:

            track_id = (
                obj["track_id"]
            )

            centroid = (
                obj["centroid"]
            )


            active_ids.add(
                track_id
            )


            # ----------------------------------
            # Track persistence
            # ----------------------------------

            self.database.upsert_track(

                session_id=
                    self.session_id,

                obj=
                    obj,

                frame_index=
                    self.frame_index,

                timestamp=
                    timestamp
            )


            # ----------------------------------
            # Trajectory
            # ----------------------------------

            self.trajectories.update(
                track_id,
                centroid
            )


            direction = (
                self.trajectories
                .get_direction(
                    track_id
                )
            )


            points = (
                self.trajectories
                .get_trajectory(
                    track_id
                )
            )


            # ----------------------------------
            # Counting Line
            # ----------------------------------

            line_event = (
                self.line_counter.update(

                    track_id=
                        track_id,

                    centroid=
                        centroid,

                    frame_index=
                        self.frame_index,

                    frame_height=
                        frame_height
                )
            )


            # ----------------------------------
            # Zone Analytics
            # ----------------------------------

            (
                zone_events,
                zone_status
            ) = self.zone_monitor.update(

                track_id=
                    track_id,

                centroid=
                    centroid,

                timestamp=
                    timestamp,

                frame_index=
                    self.frame_index,

                frame_width=
                    frame_width,

                frame_height=
                    frame_height
            )


            # ----------------------------------
            # Draw tracking
            # ----------------------------------

            draw_trajectory(
                frame,
                points
            )


            draw_object(
                frame,
                obj,
                direction
            )


            # ----------------------------------
            # Draw dwell time
            # ----------------------------------

            for (
                zone_name,
                status
            ) in zone_status.items():

                if status["inside"]:

                    draw_zone_status(

                        frame,
                        centroid,
                        zone_name,

                        status[
                            "dwell_time"
                        ]
                    )


            # ==================================
            # Line Event
            # ==================================

            if line_event is not None:

                event = (
                    self._build_event(

                        event_type=
                            f"LINE_{line_event}",

                        obj=
                            obj,

                        timestamp=
                            timestamp,

                        direction=
                            direction
                    )
                )


                self._persist_event(
                    event,
                    frame
                )


                frame_events.append(
                    event
                )


                x1, y1, _, _ = (
                    obj["bbox"]
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


            # ==================================
            # Zone Events
            # ==================================

            for zone_event in zone_events:

                event = (
                    self._build_event(

                        event_type=
                            zone_event["type"],

                        obj=
                            obj,

                        timestamp=
                            timestamp,

                        direction=
                            direction,

                        zone=
                            zone_event["zone"],

                        dwell_time=
                            zone_event[
                                "dwell_time"
                            ]
                    )
                )


                self._persist_event(
                    event,
                    frame
                )


                frame_events.append(
                    event
                )


        # ======================================
        # Cleanup old state
        # ======================================

        self.line_counter.cleanup(
            self.frame_index
        )


        self.zone_monitor.cleanup(
            self.frame_index
        )


        # ======================================
        # Periodic DB commit
        # ======================================

        if (
            self.frame_index
            %
            config.DB_COMMIT_INTERVAL_FRAMES
            ==
            0
        ):

            self.database.commit()


        # ======================================
        # Performance
        # ======================================

        self._update_fps()


        # ======================================
        # Counting Line
        # ======================================

        line_y = (
            self.line_counter
            .get_line_y(
                frame_height
            )
        )


        draw_counting_line(
            frame,
            line_y
        )


        # ======================================
        # Statistics Overlay
        # ======================================

        draw_statistics(

            frame=
                frame,

            active_objects=
                len(active_ids),

            total_in=
                self.line_counter
                .total_in,

            total_out=
                self.line_counter
                .total_out,

            fps=
                self.current_fps
        )


        # ======================================
        # Existing zone event overlay
        # ======================================

        recent_events = (
            self.zone_monitor
            .get_recent_events(
                limit=6
            )
        )


        draw_event_history(
            frame,
            recent_events
        )


        # ======================================
        # Save annotated video
        # ======================================

        self.video_recorder.write(
            frame
        )


        # ======================================
        # Data for GUI
        # ======================================

        stats = {

            "active_objects":
                len(active_ids),

            "total_in":
                self.line_counter.total_in,

            "total_out":
                self.line_counter.total_out,

            "fps":
                self.current_fps,

            "frame_index":
                self.frame_index,

            "session_id":
                self.session_id
        }


        return (
            frame,
            stats,
            frame_events
        )


    # ==========================================
    # Stop
    # ==========================================

    def stop(self):

        if self.stopped:
            return

        self.stopped = True


        try:

            self.database.commit()


            if self.session_id is not None:

                self.database.end_session(

                    session_id=
                        self.session_id,

                    total_frames=
                        self.frame_index,

                    total_in=
                        self.line_counter
                        .total_in,

                    total_out=
                        self.line_counter
                        .total_out
                )

        finally:

            self.video.release()

            self.video_recorder.release()

            self.database.close()