from collections import defaultdict, deque

import config


class TrajectoryManager:

    def __init__(self):

        self.history = defaultdict(
            lambda: deque(
                maxlen=config.MAX_TRAJECTORY_LENGTH
            )
        )


    def update(
        self,
        track_id,
        centroid
    ):

        self.history[
            track_id
        ].append(
            centroid
        )


    def get_trajectory(
        self,
        track_id
    ):

        return list(
            self.history[
                track_id
            ]
        )


    def get_direction(
        self,
        track_id
    ):

        points = self.history[
            track_id
        ]

        if len(points) < 2:
            return "UNKNOWN"


        old_x, old_y = points[-2]

        new_x, new_y = points[-1]


        dx = new_x - old_x

        dy = new_y - old_y


        threshold = (
            config.MOVEMENT_THRESHOLD
        )


        if (
            abs(dx) < threshold
            and
            abs(dy) < threshold
        ):

            return "STATIONARY"


        if abs(dx) > abs(dy):

            if dx > 0:
                return "RIGHT"

            return "LEFT"


        else:

            if dy > 0:
                return "DOWN"

            return "UP"