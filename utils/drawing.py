import cv2


def draw_object(
    frame,
    obj,
    direction
):

    x1, y1, x2, y2 = obj["bbox"]

    cx, cy = obj["centroid"]

    track_id = obj["track_id"]

    class_name = obj["class_name"]

    confidence = obj["confidence"]


    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        2
    )


    cv2.circle(
        frame,
        (cx, cy),
        4,
        (0, 0, 255),
        -1
    )


    label = (
        f"{class_name} "
        f"ID:{track_id} "
        f"{confidence:.2f} "
        f"{direction}"
    )


    cv2.putText(
        frame,
        label,
        (
            x1,
            max(20, y1 - 10)
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 0),
        2
    )


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
            points[i - 1],
            points[i],
            (255, 0, 0),
            2
        )