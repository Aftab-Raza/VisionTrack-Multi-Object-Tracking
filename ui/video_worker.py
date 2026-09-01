from PySide6.QtCore import (
    QThread,
    Signal
)

from core.engine import (
    VisionTrackEngine
)


class VideoWorker(QThread):

    # ==========================================
    # Signals
    # ==========================================

    frame_ready = Signal(
        object
    )

    stats_updated = Signal(
        dict
    )

    event_detected = Signal(
        dict
    )

    status_changed = Signal(
        str
    )

    error_occurred = Signal(
        str
    )


    def __init__(
        self,
        source,
        tracker_mode,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.source = source

        self.tracker_mode = (
            tracker_mode
        )

        self._stop_requested = (
            False
        )


    # ==========================================
    # Worker Thread
    # ==========================================

    def run(self):

        engine = None

        try:

            self.status_changed.emit(
                "Loading tracking system..."
            )

            # ==================================
            # Engine created inside worker thread
            # ==================================
            #
            # Important because SQLite connection
            # should belong to this thread.
            #

            engine = VisionTrackEngine(

                self.source,

                tracker_mode=
                    self.tracker_mode
            )

            self.status_changed.emit(
                "Opening video source..."
            )

            engine.start()

            if (
                self.tracker_mode
                ==
                "custom"
            ):

                self.status_changed.emit(
                    "Tracking - Custom MOT"
                )

            else:

                self.status_changed.emit(
                    "Tracking - ByteTrack"
                )

            # ==================================
            # Main Worker Loop
            # ==================================

            while not self._stop_requested:

                result = (
                    engine
                    .process_next_frame()
                )

                # --------------------------------
                # End of recorded video
                # --------------------------------

                if result is None:

                    self.status_changed.emit(
                        "Video completed"
                    )

                    break

                (
                    frame,
                    stats,
                    events
                ) = result

                # --------------------------------
                # Send frame to GUI
                # --------------------------------

                self.frame_ready.emit(
                    frame
                )

                # --------------------------------
                # Send statistics
                # --------------------------------

                self.stats_updated.emit(
                    stats
                )

                # --------------------------------
                # Send events
                # --------------------------------

                for event in events:

                    self.event_detected.emit(
                        event
                    )

        except Exception as error:

            self.error_occurred.emit(

                f"{type(error).__name__}: "
                f"{error}"
            )

        finally:

            if engine is not None:

                engine.stop()

            self.status_changed.emit(
                "Stopped"
            )


    # ==========================================
    # Stop Request
    # ==========================================

    def stop(self):

        self._stop_requested = True