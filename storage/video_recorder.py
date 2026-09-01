import math

from pathlib import Path

import cv2

import config


class VideoRecorder:

    def __init__(self):

        self.enabled = (
            config.ENABLE_VIDEO_RECORDING
        )

        self.writer = None

        self.file_path = Path(
            config.OUTPUT_VIDEO_FILE
        )


    def open(
        self,
        frame_width,
        frame_height,
        fps
    ):

        if not self.enabled:
            return


        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )


        if (
            fps is None
            or
            not math.isfinite(fps)
            or
            fps <= 1
        ):

            fps = (
                config
                .OUTPUT_VIDEO_FPS_FALLBACK
            )


        fourcc = (
            cv2.VideoWriter_fourcc(
                *"mp4v"
            )
        )


        self.writer = cv2.VideoWriter(

            str(
                self.file_path
            ),

            fourcc,

            fps,

            (
                frame_width,
                frame_height
            )
        )


        if not self.writer.isOpened():

            raise RuntimeError(
                "Unable to initialize "
                "output video recorder."
            )


    def write(
        self,
        frame
    ):

        if (
            self.enabled
            and
            self.writer is not None
        ):

            self.writer.write(
                frame
            )


    def release(self):

        if self.writer is not None:

            self.writer.release()

            self.writer = None