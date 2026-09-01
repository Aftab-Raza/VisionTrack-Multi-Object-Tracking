from pathlib import Path

import cv2

from PySide6.QtCore import Qt

from PySide6.QtGui import (
    QImage,
    QPixmap
)

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QFileDialog,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QGroupBox,
    QListWidget,
    QMessageBox,
    QComboBox
)

import config

from ui.video_worker import VideoWorker


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "VisionTrack - Multi-Object Tracking"
        )

        self.resize(
            1350,
            820
        )

        self.selected_source = (
            config.VIDEO_SOURCE
        )

        self.worker = None

        self.last_frame = None

        self._build_ui()

        self._update_source_label()


    # ==========================================
    # Build UI
    # ==========================================

    def _build_ui(self):

        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )

        root_layout = QVBoxLayout(
            central_widget
        )


        # ======================================
        # Main Content
        # ======================================

        content_layout = QHBoxLayout()


        # ======================================
        # Video Display
        # ======================================

        self.video_label = QLabel(
            "VisionTrack\n\n"
            "Select source, tracker "
            "and press Start"
        )

        self.video_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.video_label.setMinimumSize(
            850,
            600
        )

        self.video_label.setStyleSheet(
            """
            QLabel {
                background-color: #111111;
                color: #DDDDDD;
                border: 1px solid #333333;
                font-size: 18px;
            }
            """
        )

        content_layout.addWidget(
            self.video_label,
            stretch=4
        )


        # ======================================
        # Side Panel
        # ======================================

        side_panel = QWidget()

        side_panel.setMaximumWidth(
            360
        )

        side_layout = QVBoxLayout(
            side_panel
        )


        # ======================================
        # Live Statistics
        # ======================================

        stats_group = QGroupBox(
            "Live Statistics"
        )

        stats_layout = QGridLayout(
            stats_group
        )


        self.active_value = QLabel(
            "0"
        )

        self.in_value = QLabel(
            "0"
        )

        self.out_value = QLabel(
            "0"
        )

        self.fps_value = QLabel(
            "0.0"
        )

        self.tracking_value = QLabel(
            "0.0 ms"
        )

        self.processing_value = QLabel(
            "0.0 ms"
        )


        # --------------------------------------
        # Active Objects
        # --------------------------------------

        stats_layout.addWidget(
            QLabel("Active Objects"),
            0,
            0
        )

        stats_layout.addWidget(
            self.active_value,
            0,
            1
        )


        # --------------------------------------
        # IN
        # --------------------------------------

        stats_layout.addWidget(
            QLabel("IN"),
            1,
            0
        )

        stats_layout.addWidget(
            self.in_value,
            1,
            1
        )


        # --------------------------------------
        # OUT
        # --------------------------------------

        stats_layout.addWidget(
            QLabel("OUT"),
            2,
            0
        )

        stats_layout.addWidget(
            self.out_value,
            2,
            1
        )


        # --------------------------------------
        # FPS
        # --------------------------------------

        stats_layout.addWidget(
            QLabel("FPS"),
            3,
            0
        )

        stats_layout.addWidget(
            self.fps_value,
            3,
            1
        )


        # --------------------------------------
        # Tracking Latency
        # --------------------------------------

        stats_layout.addWidget(
            QLabel("Tracking"),
            4,
            0
        )

        stats_layout.addWidget(
            self.tracking_value,
            4,
            1
        )


        # --------------------------------------
        # Complete Frame Latency
        # --------------------------------------

        stats_layout.addWidget(
            QLabel("Frame Latency"),
            5,
            0
        )

        stats_layout.addWidget(
            self.processing_value,
            5,
            1
        )


        # --------------------------------------
        # Style Statistic Values
        # --------------------------------------

        for label in (

            self.active_value,
            self.in_value,
            self.out_value,
            self.fps_value,
            self.tracking_value,
            self.processing_value

        ):

            label.setStyleSheet(
                """
                font-size: 20px;
                font-weight: bold;
                """
            )


        side_layout.addWidget(
            stats_group
        )


        # ======================================
        # Session Information
        # ======================================

        session_group = QGroupBox(
            "Session"
        )

        session_layout = QVBoxLayout(
            session_group
        )


        self.session_label = QLabel(
            "Session ID: -"
        )

        self.frame_label = QLabel(
            "Frame: 0"
        )

        self.tracker_label = QLabel(
            "Tracker: -"
        )


        session_layout.addWidget(
            self.session_label
        )

        session_layout.addWidget(
            self.frame_label
        )

        session_layout.addWidget(
            self.tracker_label
        )


        side_layout.addWidget(
            session_group
        )


        # ======================================
        # Recent Events
        # ======================================

        events_group = QGroupBox(
            "Recent Events"
        )

        events_layout = QVBoxLayout(
            events_group
        )

        self.event_list = QListWidget()

        events_layout.addWidget(
            self.event_list
        )

        side_layout.addWidget(
            events_group,
            stretch=1
        )


        content_layout.addWidget(
            side_panel,
            stretch=1
        )


        root_layout.addLayout(
            content_layout,
            stretch=1
        )


        # ======================================
        # Controls
        # ======================================

        control_group = QGroupBox(
            "Controls"
        )

        controls = QHBoxLayout(
            control_group
        )


        self.source_label = QLabel()


        self.webcam_button = QPushButton(
            "Use Webcam"
        )


        self.open_video_button = QPushButton(
            "Open Video"
        )


        # ======================================
        # Tracker Selector
        # ======================================

        self.tracker_combo = QComboBox()

        self.tracker_combo.addItem(
            "ByteTrack",
            "bytetrack"
        )

        self.tracker_combo.addItem(
            "Custom MOT",
            "custom"
        )


        default_index = (
            self.tracker_combo.findData(
                config.TRACKER_MODE
            )
        )


        if default_index >= 0:

            self.tracker_combo.setCurrentIndex(
                default_index
            )


        # ======================================
        # Start / Stop
        # ======================================

        self.start_button = QPushButton(
            "Start"
        )

        self.stop_button = QPushButton(
            "Stop"
        )

        self.stop_button.setEnabled(
            False
        )


        controls.addWidget(
            self.source_label,
            stretch=1
        )

        controls.addWidget(
            self.webcam_button
        )

        controls.addWidget(
            self.open_video_button
        )

        controls.addWidget(
            QLabel("Tracker:")
        )

        controls.addWidget(
            self.tracker_combo
        )

        controls.addWidget(
            self.start_button
        )

        controls.addWidget(
            self.stop_button
        )


        root_layout.addWidget(
            control_group
        )


        # ======================================
        # Connections
        # ======================================

        self.webcam_button.clicked.connect(
            self.select_webcam
        )

        self.open_video_button.clicked.connect(
            self.select_video
        )

        self.start_button.clicked.connect(
            self.start_tracking
        )

        self.stop_button.clicked.connect(
            self.stop_tracking
        )


        self.statusBar().showMessage(
            "Ready"
        )


    # ==========================================
    # Webcam Source
    # ==========================================

    def select_webcam(self):

        if self._is_running():
            return

        self.selected_source = 0

        self._update_source_label()


    # ==========================================
    # Video Source
    # ==========================================

    def select_video(self):

        if self._is_running():
            return


        file_path, _ = QFileDialog.getOpenFileName(

            self,

            "Select Video",

            "",

            (
                "Video Files "
                "(*.mp4 *.avi *.mov *.mkv);;"
                "All Files (*)"
            )
        )


        if not file_path:
            return


        self.selected_source = (
            file_path
        )

        self._update_source_label()


    # ==========================================
    # Source Label
    # ==========================================

    def _update_source_label(self):

        if isinstance(
            self.selected_source,
            int
        ):

            text = (
                f"Source: Webcam "
                f"({self.selected_source})"
            )

        else:

            path = Path(
                self.selected_source
            )

            text = (
                f"Source: "
                f"{path.name}"
            )


        self.source_label.setText(
            text
        )


    # ==========================================
    # Start Tracking
    # ==========================================

    def start_tracking(self):

        if self._is_running():
            return


        self._reset_live_display()


        tracker_mode = (
            self.tracker_combo
            .currentData()
        )


        self.worker = VideoWorker(

            self.selected_source,

            tracker_mode
        )


        # --------------------------------------
        # Worker Signals
        # --------------------------------------

        self.worker.frame_ready.connect(
            self.update_frame
        )

        self.worker.stats_updated.connect(
            self.update_stats
        )

        self.worker.event_detected.connect(
            self.add_event
        )

        self.worker.status_changed.connect(
            self.update_status
        )

        self.worker.error_occurred.connect(
            self.show_error
        )

        self.worker.finished.connect(
            self.worker_finished
        )


        # --------------------------------------
        # Disable Controls
        # --------------------------------------

        self.start_button.setEnabled(
            False
        )

        self.stop_button.setEnabled(
            True
        )

        self.webcam_button.setEnabled(
            False
        )

        self.open_video_button.setEnabled(
            False
        )

        self.tracker_combo.setEnabled(
            False
        )


        self.statusBar().showMessage(
            "Starting VisionTrack..."
        )


        self.worker.start()


    # ==========================================
    # Stop Tracking
    # ==========================================

    def stop_tracking(self):

        if not self._is_running():
            return


        self.statusBar().showMessage(
            "Stopping..."
        )


        self.stop_button.setEnabled(
            False
        )


        self.worker.stop()


    # ==========================================
    # Video Frame
    # ==========================================

    def update_frame(
        self,
        frame
    ):

        self.last_frame = frame


        rgb_frame = cv2.cvtColor(

            frame,

            cv2.COLOR_BGR2RGB
        )


        height, width, channels = (
            rgb_frame.shape
        )


        bytes_per_line = (
            channels
            *
            width
        )


        image = QImage(

            rgb_frame.data,

            width,

            height,

            bytes_per_line,

            QImage.Format.Format_RGB888

        ).copy()


        pixmap = QPixmap.fromImage(
            image
        )


        scaled_pixmap = pixmap.scaled(

            self.video_label.size(),

            Qt.AspectRatioMode.KeepAspectRatio,

            Qt.TransformationMode.SmoothTransformation
        )


        self.video_label.setPixmap(
            scaled_pixmap
        )


    # ==========================================
    # Live Statistics
    # ==========================================

    def update_stats(
        self,
        stats
    ):

        # --------------------------------------
        # Object Analytics
        # --------------------------------------

        self.active_value.setText(
            str(
                stats.get(
                    "active_objects",
                    0
                )
            )
        )


        self.in_value.setText(
            str(
                stats.get(
                    "total_in",
                    0
                )
            )
        )


        self.out_value.setText(
            str(
                stats.get(
                    "total_out",
                    0
                )
            )
        )


        # --------------------------------------
        # FPS
        # --------------------------------------

        self.fps_value.setText(

            f"{stats.get(
                'fps',
                0
            ):.1f}"

        )


        # --------------------------------------
        # Tracking Time
        # --------------------------------------

        self.tracking_value.setText(

            f"{stats.get(
                'tracking_ms',
                0
            ):.1f} ms"

        )


        # --------------------------------------
        # Total Frame Latency
        # --------------------------------------

        self.processing_value.setText(

            f"{stats.get(
                'processing_ms',
                0
            ):.1f} ms"

        )


        # --------------------------------------
        # Session ID
        # --------------------------------------

        session_id = stats.get(
            "session_id",
            "-"
        )


        self.session_label.setText(

            f"Session ID: "
            f"{session_id}"

        )


        # --------------------------------------
        # Frame Number
        # --------------------------------------

        self.frame_label.setText(

            f"Frame: "
            f"{stats.get(
                'frame_index',
                0
            )}"

        )


        # --------------------------------------
        # Tracker
        # --------------------------------------

        tracker_mode = stats.get(
            "tracker_mode",
            "-"
        )


        if tracker_mode == "custom":

            tracker_text = (
                "Custom MOT"
            )

        elif tracker_mode == "bytetrack":

            tracker_text = (
                "ByteTrack"
            )

        else:

            tracker_text = (
                str(
                    tracker_mode
                )
            )


        self.tracker_label.setText(

            f"Tracker: "
            f"{tracker_text}"

        )


    # ==========================================
    # Event Feed
    # ==========================================

    def add_event(
        self,
        event
    ):

        timestamp = event.get(
            "timestamp_seconds",
            0
        )

        track_id = event.get(
            "track_id",
            "-"
        )

        event_type = event.get(
            "event_type",
            ""
        )

        class_name = event.get(
            "class_name",
            ""
        )

        zone = event.get(
            "zone",
            ""
        )

        dwell = event.get(
            "dwell_time",
            0
        )


        text = (

            f"{timestamp:7.2f}s | "
            f"ID {track_id} | "
            f"{event_type} | "
            f"{class_name}"

        )


        if zone:

            text += (
                f" | {zone}"
            )


        if event_type == "ZONE_EXIT":

            text += (
                f" | "
                f"{dwell:.1f}s"
            )


        self.event_list.insertItem(
            0,
            text
        )


        # Keep latest 100 events

        while (
            self.event_list.count()
            >
            100
        ):

            self.event_list.takeItem(

                self.event_list.count()
                -
                1
            )


    # ==========================================
    # Status
    # ==========================================

    def update_status(
        self,
        message
    ):

        self.statusBar().showMessage(
            message
        )


    # ==========================================
    # Error
    # ==========================================

    def show_error(
        self,
        message
    ):

        QMessageBox.critical(

            self,

            "VisionTrack Error",

            message
        )


    # ==========================================
    # Worker Finished
    # ==========================================

    def worker_finished(self):

        self.start_button.setEnabled(
            True
        )

        self.stop_button.setEnabled(
            False
        )

        self.webcam_button.setEnabled(
            True
        )

        self.open_video_button.setEnabled(
            True
        )

        self.tracker_combo.setEnabled(
            True
        )


        self.statusBar().showMessage(
            "Stopped"
        )


        self.worker = None


    # ==========================================
    # Running?
    # ==========================================

    def _is_running(self):

        return (

            self.worker is not None

            and

            self.worker.isRunning()

        )


    # ==========================================
    # Reset Dashboard
    # ==========================================

    def _reset_live_display(self):

        self.active_value.setText(
            "0"
        )

        self.in_value.setText(
            "0"
        )

        self.out_value.setText(
            "0"
        )

        self.fps_value.setText(
            "0.0"
        )

        self.tracking_value.setText(
            "0.0 ms"
        )

        self.processing_value.setText(
            "0.0 ms"
        )

        self.session_label.setText(
            "Session ID: -"
        )

        self.frame_label.setText(
            "Frame: 0"
        )

        self.tracker_label.setText(
            "Tracker: -"
        )

        self.event_list.clear()


    # ==========================================
    # Resize
    # ==========================================

    def resizeEvent(
        self,
        event
    ):

        super().resizeEvent(
            event
        )


        if self.last_frame is not None:

            self.update_frame(
                self.last_frame
            )


    # ==========================================
    # Close Application
    # ==========================================

    def closeEvent(
        self,
        event
    ):

        if self._is_running():

            self.worker.stop()

            self.worker.wait(
                5000
            )


        event.accept()