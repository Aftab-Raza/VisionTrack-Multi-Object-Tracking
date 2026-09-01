import cv2
import numpy as np


# ==========================================
# Tracked Object
# ==========================================

def draw_object(
    frame,
    obj,
    direction
):

    x1, y1, x2, y2 = (
        obj[
            "bbox"
        ]
    )

    cx, cy = (
        obj[
            "centroid"
        ]
    )

    track_id = (
        obj[
            "track_id"
        ]
    )

    class_name = (
        obj[
            "class_name"
        ]
    )

    confidence = (
        obj[
            "confidence"
        ]
    )

    track_state = (
        obj.get(
            "track_state",
            ""
        )
    )

    # ======================================
    # Bounding Box
    # ======================================

    cv2.rectangle(

        frame,

        (
            x1,
            y1
        ),

        (
            x2,
            y2
        ),

        (
            0,
            255,
            0
        ),

        2
    )

    # ======================================
    # Centroid
    # ======================================

    cv2.circle(

        frame,

        (
            cx,
            cy
        ),

        4,

        (
            0,
            0,
            255
        ),

        -1
    )

    # ======================================
    # Label
    # ======================================

    label = (

        f"{class_name} "
        f"ID:{track_id} "
        f"{confidence:.2f} "
        f"{direction}"

    )

    if track_state:

        label += (

            f" "
            f"{track_state}"

        )

    cv2.putText(

        frame,

        label,

        (
            x1,

            max(
                20,
                y1 - 10
            )
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.55,

        (
            0,
            255,
            0
        ),

        2
    )


# ==========================================
# Trajectory
# ==========================================

def draw_trajectory(
    frame,
    points
):

    if len(points) < 2:
        return

    for i in range(
        1,
        len(points)
    ):

        cv2.line(

            frame,

            points[
                i - 1
            ],

            points[
                i
            ],

            (
                255,
                0,
                0
            ),

            2
        )


# ==========================================
# Counting Line
# ==========================================

def draw_counting_line(
    frame,
    line_y
):

    _, width = (
        frame.shape[
            :2
        ]
    )

    cv2.line(

        frame,

        (
            0,
            line_y
        ),

        (
            width,
            line_y
        ),

        (
            0,
            255,
            255
        ),

        2
    )

    cv2.putText(

        frame,

        "COUNTING LINE",

        (
            20,

            max(
                20,
                line_y - 12
            )
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.6,

        (
            0,
            255,
            255
        ),

        2
    )


# ==========================================
# Live Statistics
# ==========================================

def draw_statistics(
    frame,
    active_objects,
    total_in,
    total_out,
    fps
):

    cv2.putText(

        frame,

        f"Active: "
        f"{active_objects}",

        (
            20,
            35
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.75,

        (
            255,
            255,
            255
        ),

        2
    )

    cv2.putText(

        frame,

        f"IN: "
        f"{total_in}",

        (
            20,
            70
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.75,

        (
            255,
            255,
            255
        ),

        2
    )

    cv2.putText(

        frame,

        f"OUT: "
        f"{total_out}",

        (
            20,
            105
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.75,

        (
            255,
            255,
            255
        ),

        2
    )

    cv2.putText(

        frame,

        f"FPS: "
        f"{fps:.1f}",

        (
            20,
            140
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.75,

        (
            255,
            255,
            255
        ),

        2
    )


# ==========================================
# Polygon Zone
# ==========================================

def draw_zone(
    frame,
    zone_name,
    polygon,
    entries=0,
    exits=0
):

    if not polygon:
        return

    polygon_array = (
        np.array(

            polygon,

            dtype=np.int32

        ).reshape(
            (
                -1,
                1,
                2
            )
        )
    )

    cv2.polylines(

        frame,

        [
            polygon_array
        ],

        True,

        (
            255,
            255,
            0
        ),

        2
    )

    label_x = (
        polygon[
            0
        ][
            0
        ]
    )

    label_y = max(

        25,

        polygon[
            0
        ][
            1
        ]
        -
        10
    )

    label = (

        f"{zone_name} "
        f"E:{entries} "
        f"X:{exits}"

    )

    cv2.putText(

        frame,

        label,

        (
            label_x,
            label_y
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.6,

        (
            255,
            255,
            0
        ),

        2
    )


# ==========================================
# Zone Dwell Time
# ==========================================

def draw_zone_status(
    frame,
    centroid,
    zone_name,
    dwell_time
):

    cx, cy = centroid

    text = (

        f"{zone_name}: "
        f"{dwell_time:.1f}s"

    )

    cv2.putText(

        frame,

        text,

        (
            cx + 10,
            cy + 25
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.5,

        (
            0,
            255,
            255
        ),

        2
    )


# ==========================================
# Recent Zone Events
# ==========================================

def draw_event_history(
    frame,
    events
):

    _, width = (
        frame.shape[
            :2
        ]
    )

    x = max(

        20,

        width
        -
        390
    )

    y = 35

    cv2.putText(

        frame,

        "ZONE EVENTS",

        (
            x,
            y
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.65,

        (
            255,
            255,
            255
        ),

        2
    )

    y += 30

    for event in events:

        event_type = (
            event[
                "type"
            ]
        )

        track_id = (
            event[
                "track_id"
            ]
        )

        zone = (
            event[
                "zone"
            ]
        )

        if (
            event_type
            ==
            "ZONE_ENTRY"
        ):

            text = (

                f"ID {track_id} "
                f"ENTERED {zone}"

            )

        else:

            dwell = (
                event[
                    "dwell_time"
                ]
            )

            text = (

                f"ID {track_id} "
                f"EXITED {zone} "
                f"({dwell:.1f}s)"

            )

        cv2.putText(

            frame,

            text,

            (
                x,
                y
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.45,

            (
                255,
                255,
                255
            ),

            1
        )

        y += 24