from ultralytics import YOLO

import config

from core.detector import (
    ObjectDetector
)

from core.custom_tracker import (
    CustomMOTTracker
)


class MultiObjectTracker:

    def __init__(
        self,
        mode=None
    ):

        self.mode = (
            mode
            or
            config.TRACKER_MODE
        ).lower()


        if self.mode == "bytetrack":

            print(
                "Loading ByteTrack backend..."
            )

            self.model = YOLO(
                config.MODEL_PATH
            )

            self.detector = None

            self.custom_tracker = None


        elif self.mode == "custom":

            print(
                "Loading Custom MOT backend..."
            )

            self.model = None


            self.detector = (
                ObjectDetector()
            )


            self.custom_tracker = (
                CustomMOTTracker()
            )


        else:

            raise ValueError(

                f"Unsupported tracker mode: "
                f"{self.mode}"

            )


    # ==========================================
    # Common Interface
    # ==========================================

    def track(
        self,
        frame
    ):

        if (
            self.mode
            ==
            "bytetrack"
        ):

            return (
                self._track_bytetrack(
                    frame
                )
            )


        detections = (
            self.detector.detect(
                frame
            )
        )


        return (
            self.custom_tracker.update(
                detections
            )
        )


    # ==========================================
    # ByteTrack Backend
    # ==========================================

    def _track_bytetrack(
        self,
        frame
    ):

        results = self.model.track(

            frame,

            persist=True,

            tracker=
                config.TRACKER_CONFIG,

            conf=
                config
                .CONFIDENCE_THRESHOLD,

            verbose=False
        )


        result = results[0]

        tracked_objects = []


        if result.boxes is None:
            return tracked_objects


        boxes = result.boxes


        if boxes.id is None:
            return tracked_objects


        coordinates = (
            boxes.xyxy
            .cpu()
            .tolist()
        )


        track_ids = (
            boxes.id
            .int()
            .cpu()
            .tolist()
        )


        class_ids = (
            boxes.cls
            .int()
            .cpu()
            .tolist()
        )


        confidences = (
            boxes.conf
            .cpu()
            .tolist()
        )


        for (
            box,
            track_id,
            class_id,
            confidence
        ) in zip(
            coordinates,
            track_ids,
            class_ids,
            confidences
        ):

            x1, y1, x2, y2 = map(
                int,
                box
            )


            cx = int(
                (x1 + x2)
                /
                2
            )


            cy = int(
                (y1 + y2)
                /
                2
            )


            tracked_objects.append({

                "track_id":
                    track_id,

                "class_id":
                    class_id,

                "class_name":
                    self.model.names[
                        class_id
                    ],

                "confidence":
                    float(
                        confidence
                    ),

                "bbox":
                    (
                        x1,
                        y1,
                        x2,
                        y2
                    ),

                "centroid":
                    (
                        cx,
                        cy
                    ),

                "track_state":
                    "CONFIRMED"

            })


        return tracked_objects