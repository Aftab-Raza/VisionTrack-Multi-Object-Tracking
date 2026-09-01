from pathlib import Path

import cv2

import config


class SnapshotManager:

    def __init__(self):

        self.enabled = (
            config.ENABLE_EVENT_SNAPSHOTS
        )

        self.directory = Path(
            config.SNAPSHOT_DIRECTORY
        )

        if self.enabled:

            self.directory.mkdir(
                parents=True,
                exist_ok=True
            )


    def save(
        self,
        frame,
        event_type,
        track_id,
        frame_index
    ):

        if not self.enabled:
            return None


        safe_event = (
            event_type
            .replace(" ", "_")
            .lower()
        )


        filename = (
            f"{safe_event}"
            f"_id_{track_id}"
            f"_frame_{frame_index}.jpg"
        )


        path = (
            self.directory
            /
            filename
        )


        cv2.imwrite(
            str(path),
            frame,
            [
                cv2.IMWRITE_JPEG_QUALITY,
                config.SNAPSHOT_JPEG_QUALITY
            ]
        )


        return str(path)