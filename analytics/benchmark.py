import csv
import statistics
from pathlib import Path

import config


class BenchmarkManager:

    def __init__(
        self,
        tracker_mode
    ):

        self.enabled = (
            config.ENABLE_BENCHMARKING
        )

        self.tracker_mode = (
            tracker_mode
        )

        self.frame_records = []

        self.unique_track_ids = set()

        self.total_active_objects = 0


    # ==========================================
    # Record One Frame
    # ==========================================

    def record_frame(
        self,
        frame_index,
        tracking_ms,
        total_processing_ms,
        fps,
        objects
    ):

        if not self.enabled:
            return

        active_objects = len(
            objects
        )

        self.total_active_objects += (
            active_objects
        )


        for obj in objects:

            self.unique_track_ids.add(
                obj["track_id"]
            )


        self.frame_records.append({

            "frame_index":
                frame_index,

            "tracker_mode":
                self.tracker_mode,

            "tracking_ms":
                round(
                    tracking_ms,
                    3
                ),

            "total_processing_ms":
                round(
                    total_processing_ms,
                    3
                ),

            "fps":
                round(
                    fps,
                    3
                ),

            "active_objects":
                active_objects

        })


    # ==========================================
    # Calculate Summary
    # ==========================================

    def get_summary(self):

        if not self.frame_records:

            return {

                "tracker_mode":
                    self.tracker_mode,

                "total_frames":
                    0,

                "average_fps":
                    0,

                "average_tracking_ms":
                    0,

                "average_processing_ms":
                    0,

                "p95_processing_ms":
                    0,

                "unique_track_ids":
                    0,

                "average_active_objects":
                    0
            }


        fps_values = [

            record["fps"]

            for record
            in self.frame_records

        ]


        tracking_values = [

            record["tracking_ms"]

            for record
            in self.frame_records

        ]


        processing_values = [

            record[
                "total_processing_ms"
            ]

            for record
            in self.frame_records

        ]


        total_frames = len(
            self.frame_records
        )


        sorted_processing = sorted(
            processing_values
        )


        p95_index = int(
            0.95
            *
            (
                len(
                    sorted_processing
                )
                -
                1
            )
        )


        p95_processing = (
            sorted_processing[
                p95_index
            ]
        )


        return {

            "tracker_mode":
                self.tracker_mode,

            "total_frames":
                total_frames,

            "average_fps":
                round(
                    statistics.mean(
                        fps_values
                    ),
                    3
                ),

            "average_tracking_ms":
                round(
                    statistics.mean(
                        tracking_values
                    ),
                    3
                ),

            "average_processing_ms":
                round(
                    statistics.mean(
                        processing_values
                    ),
                    3
                ),

            "p95_processing_ms":
                round(
                    p95_processing,
                    3
                ),

            "unique_track_ids":
                len(
                    self.unique_track_ids
                ),

            "average_active_objects":
                round(
                    self.total_active_objects
                    /
                    total_frames,
                    3
                )

        }


    # ==========================================
    # Save Results
    # ==========================================

    def save(self):

        if (
            not self.enabled
            or
            not self.frame_records
        ):

            return None


        output_directory = Path(
            config.BENCHMARK_DIRECTORY
        )


        output_directory.mkdir(
            parents=True,
            exist_ok=True
        )


        # ======================================
        # Frame CSV
        # ======================================

        if (
            config
            .SAVE_FRAME_BENCHMARKS
        ):

            frame_file = (

                output_directory
                /
                (
                    f"{self.tracker_mode}"
                    "_frames.csv"
                )

            )


            with frame_file.open(
                "w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.DictWriter(

                    file,

                    fieldnames=[
                        "frame_index",
                        "tracker_mode",
                        "tracking_ms",
                        "total_processing_ms",
                        "fps",
                        "active_objects"
                    ]
                )


                writer.writeheader()

                writer.writerows(
                    self.frame_records
                )


        # ======================================
        # Summary CSV
        # ======================================

        summary = (
            self.get_summary()
        )


        summary_file = (

            output_directory
            /
            (
                f"{self.tracker_mode}"
                "_summary.csv"
            )

        )


        with summary_file.open(
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(

                file,

                fieldnames=list(
                    summary.keys()
                )
            )


            writer.writeheader()

            writer.writerow(
                summary
            )


        return summary