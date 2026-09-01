from ultralytics import YOLO

import config


class MultiObjectTracker:

    def __init__(self):

        print("Loading detection model...")

        self.model = YOLO(
            config.MODEL_PATH
        )

        print("Model loaded.")

    def track(self, frame):

        results = self.model.track(
            frame,
            persist=True,
            tracker=config.TRACKER_CONFIG,
            conf=config.CONFIDENCE_THRESHOLD,
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
                (x1 + x2) / 2
            )

            cy = int(
                (y1 + y2) / 2
            )

            tracked_object = {

                "track_id": track_id,

                "class_id": class_id,

                "class_name":
                    self.model.names[class_id],

                "confidence":
                    confidence,

                "bbox":
                    (x1, y1, x2, y2),

                "centroid":
                    (cx, cy)
            }

            tracked_objects.append(
                tracked_object
            )

        return tracked_objects