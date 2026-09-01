from ultralytics import YOLO

import config


class ObjectDetector:

    def __init__(self):

        print("Loading YOLO detector...")

        self.model = YOLO(
            config.MODEL_PATH
        )

        print("YOLO detector loaded.")


    def detect(self, frame):

        results = self.model.predict(
            frame,
            conf=config.CONFIDENCE_THRESHOLD,
            verbose=False
        )

        result = results[0]

        detections = []


        if result.boxes is None:
            return detections


        boxes = result.boxes


        if len(boxes) == 0:
            return detections


        coordinates = (
            boxes.xyxy
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
            class_id,
            confidence
        ) in zip(
            coordinates,
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


            detections.append({

                "bbox":
                    (x1, y1, x2, y2),

                "centroid":
                    (cx, cy),

                "class_id":
                    class_id,

                "class_name":
                    self.model.names[
                        class_id
                    ],

                "confidence":
                    float(confidence)

            })


        return detections