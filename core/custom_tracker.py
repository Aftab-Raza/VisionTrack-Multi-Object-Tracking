import config

from core.kalman_filter import (
    KalmanBoxFilter
)

from core.association import (
    associate
)


# ==========================================
# Individual Track
# ==========================================

class Track:

    def __init__(
        self,
        track_id,
        detection
    ):

        self.track_id = (
            track_id
        )


        self.kalman = (
            KalmanBoxFilter(
                detection[
                    "bbox"
                ]
            )
        )


        self.bbox = (
            detection[
                "bbox"
            ]
        )


        self.class_id = (
            detection[
                "class_id"
            ]
        )


        self.class_name = (
            detection[
                "class_name"
            ]
        )


        self.confidence = (
            detection[
                "confidence"
            ]
        )


        # Number of successful
        # detection associations.

        self.hits = 1


        # Consecutive missed frames.

        self.misses = 0


        # Total lifetime in frames.

        self.age = 1


        if (
            config.CUSTOM_MIN_HITS
            <=
            1
        ):

            self.state = (
                "CONFIRMED"
            )

        else:

            self.state = (
                "TENTATIVE"
            )


    # ======================================
    # Prediction
    # ======================================

    def predict(self):

        self.bbox = (
            self.kalman.predict()
        )

        self.age += 1

        return self.bbox


    # ======================================
    # Detection Update
    # ======================================

    def update(
        self,
        detection
    ):

        self.bbox = (
            self.kalman.update(
                detection[
                    "bbox"
                ]
            )
        )


        self.class_id = (
            detection[
                "class_id"
            ]
        )


        self.class_name = (
            detection[
                "class_name"
            ]
        )


        self.confidence = (
            detection[
                "confidence"
            ]
        )


        self.hits += 1

        self.misses = 0


        if (
            self.hits
            >=
            config.CUSTOM_MIN_HITS
        ):

            self.state = (
                "CONFIRMED"
            )

        else:

            self.state = (
                "TENTATIVE"
            )


    # ======================================
    # Missed Detection
    # ======================================

    def mark_missed(self):

        self.misses += 1


        if (
            self.misses
            >
            config.CUSTOM_MAX_MISSED
        ):

            self.state = (
                "REMOVED"
            )


        elif (
            self.state
            ==
            "CONFIRMED"
        ):

            self.state = (
                "LOST"
            )


        elif (
            self.state
            ==
            "LOST"
        ):

            self.state = (
                "LOST"
            )


    # ======================================
    # Convert to VisionTrack Format
    # ======================================

    def to_object(self):

        x1, y1, x2, y2 = (
            self.bbox
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


        return {

            "track_id":
                self.track_id,

            "class_id":
                self.class_id,

            "class_name":
                self.class_name,

            "confidence":
                self.confidence,

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
                self.state,

            "track_hits":
                self.hits,

            "track_age":
                self.age
        }


# ==========================================
# Custom Multi-Object Tracker
# ==========================================

class CustomMOTTracker:

    def __init__(self):

        self.tracks = []

        self.next_track_id = 1


    # ======================================
    # Create Track
    # ======================================

    def _create_track(
        self,
        detection
    ):

        track = Track(

            track_id=
                self.next_track_id,

            detection=
                detection
        )


        self.next_track_id += 1


        self.tracks.append(
            track
        )


    # ======================================
    # Update
    # ======================================

    def update(
        self,
        detections
    ):

        # ----------------------------------
        # Remove already dead tracks
        # ----------------------------------

        self.tracks = [

            track

            for track in self.tracks

            if (
                track.state
                !=
                "REMOVED"
            )

        ]


        # ----------------------------------
        # Predict all existing tracks
        # ----------------------------------

        predicted_boxes = []


        for track in self.tracks:

            predicted_boxes.append(
                track.predict()
            )


        detection_boxes = [

            detection["bbox"]

            for detection in detections

        ]


        track_class_ids = [

            track.class_id

            for track in self.tracks

        ]


        detection_class_ids = [

            detection["class_id"]

            for detection in detections

        ]


        # ----------------------------------
        # Hungarian Association
        # ----------------------------------

        (
            matches,
            unmatched_track_indices,
            unmatched_detection_indices

        ) = associate(

            track_boxes=
                predicted_boxes,

            detection_boxes=
                detection_boxes,

            iou_threshold=
                config
                .CUSTOM_IOU_THRESHOLD,

            track_class_ids=
                track_class_ids,

            detection_class_ids=
                detection_class_ids
        )


        # ----------------------------------
        # Matched Tracks
        # ----------------------------------

        for (
            track_index,
            detection_index
        ) in matches:

            self.tracks[
                track_index
            ].update(

                detections[
                    detection_index
                ]

            )


        # ----------------------------------
        # Unmatched Tracks
        # ----------------------------------

        for track_index in (
            unmatched_track_indices
        ):

            self.tracks[
                track_index
            ].mark_missed()


        # ----------------------------------
        # New Detections
        # ----------------------------------

        for detection_index in (
            unmatched_detection_indices
        ):

            self._create_track(

                detections[
                    detection_index
                ]

            )


        # ----------------------------------
        # Remove dead tracks
        # ----------------------------------

        self.tracks = [

            track

            for track in self.tracks

            if (
                track.state
                !=
                "REMOVED"
            )

        ]


        # ----------------------------------
        # Output
        # ----------------------------------

        visible_tracks = []


        for track in self.tracks:

            # Only show tracks that:
            #
            # 1. are confirmed
            # 2. have a detection in the
            #    current frame
            #
            # Lost tracks remain internally
            # alive for possible recovery.

            if (
                track.state
                ==
                "CONFIRMED"
                and
                track.misses
                ==
                0
            ):

                visible_tracks.append(
                    track.to_object()
                )


        return visible_tracks