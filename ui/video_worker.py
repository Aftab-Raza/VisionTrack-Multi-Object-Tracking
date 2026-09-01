from PySide6.QtCore import (
    QThread,
    Signal
)

from core.engine import VisionTrackEngine


class VideoWorker(QThread):

    frame_ready = Signal(object)

    stats_updated = Signal(dict)

    event_detected = Signal(dict)

    status_changed = Signal(str)

    error_occurred = Signal(str)


    def __init__(
        self,
        source,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.source = source

        self._stop_requested = False


    # ==========================================
    # Worker Thread
    # ==========================================

    def run(self):

        engine = None

        try:

            self.status_changed.emit(
                "Loading detection model..."
            )


            # IMPORTANT:
            # Engine is created inside this
            # worker thread.
            #
            # This also ensures that the SQLite
            # connection belongs to this thread.

            engine = VisionTrackEngine(
                self.source
            )


            self.status_changed.emit(
                "Opening video source..."
            )


            engine.start()


            self.status_changed.emit(
                "Tracking"
            )


            while not self._stop_requested:

                result = (
                    engine
                    .process_next_frame()
                )


                # End of recorded video
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


                self.frame_ready.emit(
                    frame
                )


                self.stats_updated.emit(
                    stats
                )


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
    # Request Stop
    # ==========================================

    def stop(self):

        self._stop_requested = True