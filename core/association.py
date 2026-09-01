import numpy as np

from scipy.optimize import (
    linear_sum_assignment
)


# ==========================================
# Intersection over Union
# ==========================================

def calculate_iou(
    box_a,
    box_b
):

    ax1, ay1, ax2, ay2 = box_a

    bx1, by1, bx2, by2 = box_b


    intersection_x1 = max(
        ax1,
        bx1
    )

    intersection_y1 = max(
        ay1,
        by1
    )

    intersection_x2 = min(
        ax2,
        bx2
    )

    intersection_y2 = min(
        ay2,
        by2
    )


    intersection_width = max(
        0,
        intersection_x2
        -
        intersection_x1
    )


    intersection_height = max(
        0,
        intersection_y2
        -
        intersection_y1
    )


    intersection_area = (

        intersection_width

        *

        intersection_height
    )


    area_a = max(
        0,
        ax2 - ax1
    ) * max(
        0,
        ay2 - ay1
    )


    area_b = max(
        0,
        bx2 - bx1
    ) * max(
        0,
        by2 - by1
    )


    union_area = (

        area_a

        +

        area_b

        -

        intersection_area
    )


    if union_area <= 0:
        return 0.0


    return (
        intersection_area
        /
        union_area
    )


# ==========================================
# Build IoU Matrix
# ==========================================

def build_iou_matrix(
    track_boxes,
    detection_boxes,
    track_class_ids=None,
    detection_class_ids=None
):

    matrix = np.zeros(

        (
            len(track_boxes),
            len(detection_boxes)
        ),

        dtype=np.float64
    )


    for track_index, track_box in enumerate(
        track_boxes
    ):

        for detection_index, detection_box in enumerate(
            detection_boxes
        ):

            # Avoid matching different
            # object classes.

            if (
                track_class_ids is not None
                and
                detection_class_ids is not None
                and
                track_class_ids[
                    track_index
                ]
                !=
                detection_class_ids[
                    detection_index
                ]
            ):

                matrix[
                    track_index,
                    detection_index
                ] = 0.0

                continue


            matrix[
                track_index,
                detection_index
            ] = calculate_iou(

                track_box,
                detection_box
            )


    return matrix


# ==========================================
# Hungarian Association
# ==========================================

def associate(
    track_boxes,
    detection_boxes,
    iou_threshold,
    track_class_ids=None,
    detection_class_ids=None
):

    num_tracks = len(
        track_boxes
    )

    num_detections = len(
        detection_boxes
    )


    # No existing tracks

    if num_tracks == 0:

        return (
            [],
            [],
            list(
                range(
                    num_detections
                )
            )
        )


    # No detections

    if num_detections == 0:

        return (
            [],
            list(
                range(
                    num_tracks
                )
            ),
            []
        )


    iou_matrix = (
        build_iou_matrix(

            track_boxes,
            detection_boxes,

            track_class_ids=
                track_class_ids,

            detection_class_ids=
                detection_class_ids
        )
    )


    # Hungarian minimizes cost.
    #
    # Higher IoU = better,
    # therefore:
    #
    # cost = 1 - IoU

    cost_matrix = (
        1.0
        -
        iou_matrix
    )


    row_indices, column_indices = (
        linear_sum_assignment(
            cost_matrix
        )
    )


    matches = []

    unmatched_tracks = set(
        range(
            num_tracks
        )
    )

    unmatched_detections = set(
        range(
            num_detections
        )
    )


    for track_index, detection_index in zip(
        row_indices,
        column_indices
    ):

        score = iou_matrix[
            track_index,
            detection_index
        ]


        if score < iou_threshold:
            continue


        matches.append(
            (
                track_index,
                detection_index
            )
        )


        unmatched_tracks.discard(
            track_index
        )

        unmatched_detections.discard(
            detection_index
        )


    return (

        matches,

        sorted(
            unmatched_tracks
        ),

        sorted(
            unmatched_detections
        )

    )