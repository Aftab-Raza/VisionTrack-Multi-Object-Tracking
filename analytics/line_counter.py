import config


class LineCounter:

    def __init__(self):

        self.total_in = 0
        self.total_out = 0

        # Stores which side of the line
        # each object was last seen on.
        self.last_stable_side = {}

        # Prevent duplicate counts caused
        # by movement around the line.
        self.last_count_frame = {}

        # Used to clean old track IDs.
        self.last_seen_frame = {}

    def get_line_y(self, frame_height):

        return int(
            frame_height
            * config.LINE_POSITION_RATIO
        )

    def get_side(
        self,
        y,
        line_y
    ):

        # Object is clearly above the line.
        if y < line_y - config.LINE_MARGIN:
            return -1

        # Object is clearly below the line.
        if y > line_y + config.LINE_MARGIN:
            return 1

        # Object is inside the dead zone.
        return 0

    def update(
        self,
        track_id,
        centroid,
        frame_index,
        frame_height
    ):

        _, cy = centroid

        line_y = self.get_line_y(
            frame_height
        )

        current_side = self.get_side(
            cy,
            line_y
        )

        self.last_seen_frame[
            track_id
        ] = frame_index

        # If object is close to the line,
        # don't change its stable state.
        if current_side == 0:
            return None

        previous_side = (
            self.last_stable_side.get(
                track_id
            )
        )

        # First observation of this object.
        if previous_side is None:

            self.last_stable_side[
                track_id
            ] = current_side

            return None

        # Object is still on the same side.
        if previous_side == current_side:
            return None

        # The object has changed sides.

        last_count = (
            self.last_count_frame.get(
                track_id,
                -100000
            )
        )

        frames_since_last_count = (
            frame_index
            - last_count
        )

        self.last_stable_side[
            track_id
        ] = current_side

        # Ignore rapid repeated crossings.
        if (
            frames_since_last_count
            <
            config.CROSSING_COOLDOWN_FRAMES
        ):
            return None

        # ABOVE -> BELOW
        if (
            previous_side == -1
            and
            current_side == 1
        ):

            self.total_in += 1

            event = "IN"

        # BELOW -> ABOVE
        elif (
            previous_side == 1
            and
            current_side == -1
        ):

            self.total_out += 1

            event = "OUT"

        else:
            return None

        self.last_count_frame[
            track_id
        ] = frame_index

        return event

    def cleanup(
        self,
        frame_index
    ):

        old_ids = []

        for (
            track_id,
            last_seen
        ) in self.last_seen_frame.items():

            age = (
                frame_index
                -
                last_seen
            )

            if (
                age
                >
                config.TRACK_MEMORY_MAX_AGE
            ):

                old_ids.append(
                    track_id
                )

        for track_id in old_ids:

            self.last_seen_frame.pop(
                track_id,
                None
            )

            self.last_stable_side.pop(
                track_id,
                None
            )

            self.last_count_frame.pop(
                track_id,
                None
            )