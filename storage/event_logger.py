import csv
from pathlib import Path

import config


class EventLogger:

    def __init__(self):

        self.enabled = config.ENABLE_CSV_LOGGING

        self.file_path = Path(
            config.EVENT_LOG_FILE
        )

        self.fieldnames = [
            "frame_index",
            "timestamp_seconds",
            "event_type",
            "track_id",
            "class_name",
            "zone",
            "direction",
            "dwell_time",
            "centroid_x",
            "centroid_y"
        ]

        if self.enabled:
            self._prepare_file()


    def _prepare_file(self):

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        file_exists = (
            self.file_path.exists()
        )

        file_empty = (
            not file_exists
            or
            self.file_path.stat().st_size == 0
        )

        if file_empty:

            with self.file_path.open(
                "w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.DictWriter(
                    file,
                    fieldnames=self.fieldnames
                )

                writer.writeheader()


    def log(self, event):

        if not self.enabled:
            return

        row = {}

        for field in self.fieldnames:

            row[field] = event.get(
                field,
                ""
            )

        with self.file_path.open(
            "a",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=self.fieldnames
            )

            writer.writerow(row)