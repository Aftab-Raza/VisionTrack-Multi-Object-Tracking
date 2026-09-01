from collections import defaultdict, deque

import cv2
import numpy as np

import config


class ZoneMonitor:

    def __init__(self):

        self.zones = config.ZONES

        # Stores whether each track is currently
        # inside each zone.
        #
        # Example:
        #
        # inside_state["Restricted Zone"][5] = True

        self.inside_state = defaultdict(dict)


        # Stores when an object entered a zone.

        self.entry_times = defaultdict(dict)


        # Stores latest frame where track was seen.

        self.last_seen_frame = {}


        # Zone statistics.

        self.entry_counts = defaultdict(int)
        self.exit_counts = defaultdict(int)


        # Recent event history.

        self.events = deque(
            maxlen=config.ZONE_EVENT_HISTORY_LIMIT
        )


    # ==========================================
    # Zone geometry
    # ==========================================

    def get_pixel_polygon(
        self,
        zone_name,
        frame_width,
        frame_height
    ):

        normalized_points = self.zones[
            zone_name
        ]

        pixel_points = []

        for x_ratio, y_ratio in normalized_points:

            x = int(
                x_ratio
                *
                frame_width
            )

            y = int(
                y_ratio
                *
                frame_height
            )

            pixel_points.append(
                (x, y)
            )

        return pixel_points


    def is_inside_zone(
        self,
        centroid,
        polygon
    ):

        polygon_array = np.array(
            polygon,
            dtype=np.int32
        )

        polygon_array = polygon_array.reshape(
            (-1, 1, 2)
        )

        result = cv2.pointPolygonTest(
            polygon_array,
            centroid,
            False
        )

        return result >= 0


    # ==========================================
    # Main zone analytics
    # ==========================================

    def update(
        self,
        track_id,
        centroid,
        timestamp,
        frame_index,
        frame_width,
        frame_height
    ):

        detected_events = []

        current_status = {}

        self.last_seen_frame[
            track_id
        ] = frame_index


        for zone_name in self.zones:

            polygon = (
                self.get_pixel_polygon(
                    zone_name,
                    frame_width,
                    frame_height
                )
            )


            is_inside = (
                self.is_inside_zone(
                    centroid,
                    polygon
                )
            )


            was_inside = (
                self.inside_state[
                    zone_name
                ].get(
                    track_id,
                    False
                )
            )


            # ==================================
            # ENTRY EVENT
            # ==================================

            if (
                is_inside
                and
                not was_inside
            ):

                self.inside_state[
                    zone_name
                ][
                    track_id
                ] = True


                self.entry_times[
                    zone_name
                ][
                    track_id
                ] = timestamp


                self.entry_counts[
                    zone_name
                ] += 1


                event = {

                    "type": "ZONE_ENTRY",

                    "zone": zone_name,

                    "track_id": track_id,

                    "timestamp": timestamp,

                    "dwell_time": 0.0

                }


                self.events.appendleft(
                    event
                )

                detected_events.append(
                    event
                )


            # ==================================
            # EXIT EVENT
            # ==================================

            elif (
                not is_inside
                and
                was_inside
            ):

                self.inside_state[
                    zone_name
                ][
                    track_id
                ] = False


                entry_time = (
                    self.entry_times[
                        zone_name
                    ].pop(
                        track_id,
                        timestamp
                    )
                )


                dwell_time = max(
                    0.0,
                    timestamp
                    -
                    entry_time
                )


                self.exit_counts[
                    zone_name
                ] += 1


                event = {

                    "type": "ZONE_EXIT",

                    "zone": zone_name,

                    "track_id": track_id,

                    "timestamp": timestamp,

                    "dwell_time": dwell_time

                }


                self.events.appendleft(
                    event
                )

                detected_events.append(
                    event
                )


            # ==================================
            # Current dwell time
            # ==================================

            dwell_time = 0.0


            if is_inside:

                entry_time = (
                    self.entry_times[
                        zone_name
                    ].get(
                        track_id,
                        timestamp
                    )
                )

                dwell_time = max(
                    0.0,
                    timestamp
                    -
                    entry_time
                )


            current_status[
                zone_name
            ] = {

                "inside": is_inside,

                "dwell_time":
                    dwell_time

            }


        return (
            detected_events,
            current_status
        )


    # ==========================================
    # Statistics
    # ==========================================

    def get_zone_counts(
        self,
        zone_name
    ):

        return {

            "entries":
                self.entry_counts[
                    zone_name
                ],

            "exits":
                self.exit_counts[
                    zone_name
                ]

        }


    def get_recent_events(
        self,
        limit=6
    ):

        return list(
            self.events
        )[:limit]


    # ==========================================
    # Memory cleanup
    # ==========================================

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
                config.ZONE_TRACK_MAX_AGE
            ):

                old_ids.append(
                    track_id
                )


        for track_id in old_ids:

            self.last_seen_frame.pop(
                track_id,
                None
            )


            for zone_name in self.zones:

                self.inside_state[
                    zone_name
                ].pop(
                    track_id,
                    None
                )

                self.entry_times[
                    zone_name
                ].pop(
                    track_id,
                    None
                )