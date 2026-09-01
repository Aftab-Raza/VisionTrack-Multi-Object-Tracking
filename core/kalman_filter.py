import numpy as np


class KalmanBoxFilter:

    """
    Constant-velocity Kalman Filter.

    State:

    x = [
        cx,
        cy,
        w,
        h,
        vx,
        vy,
        vw,
        vh
    ]

    Measurement:

    z = [
        cx,
        cy,
        w,
        h
    ]
    """


    def __init__(
        self,
        bbox
    ):

        self.state = np.zeros(
            (8, 1),
            dtype=np.float64
        )


        cx, cy, w, h = (
            self._bbox_to_measurement(
                bbox
            )
        )


        self.state[
            0:4,
            0
        ] = [
            cx,
            cy,
            w,
            h
        ]


        # ======================================
        # State Transition Matrix
        # ======================================

        self.F = np.eye(
            8,
            dtype=np.float64
        )


        # Position depends on velocity.

        self.F[0, 4] = 1.0
        self.F[1, 5] = 1.0
        self.F[2, 6] = 1.0
        self.F[3, 7] = 1.0


        # ======================================
        # Measurement Matrix
        # ======================================

        self.H = np.zeros(
            (4, 8),
            dtype=np.float64
        )


        self.H[0, 0] = 1.0
        self.H[1, 1] = 1.0
        self.H[2, 2] = 1.0
        self.H[3, 3] = 1.0


        # ======================================
        # Covariance
        # ======================================

        self.P = np.eye(
            8,
            dtype=np.float64
        )


        # Velocity is initially uncertain.

        self.P[
            4:8,
            4:8
        ] *= 100.0


        # ======================================
        # Process Noise
        # ======================================

        self.Q = np.eye(
            8,
            dtype=np.float64
        ) * 0.05


        # ======================================
        # Measurement Noise
        # ======================================

        self.R = np.eye(
            4,
            dtype=np.float64
        ) * 5.0


    # ==========================================
    # Predict
    # ==========================================

    def predict(self):

        self.state = (
            self.F
            @
            self.state
        )


        self.P = (
            self.F
            @
            self.P
            @
            self.F.T
            +
            self.Q
        )


        self._ensure_valid_size()


        return self.get_bbox()


    # ==========================================
    # Correct / Update
    # ==========================================

    def update(
        self,
        bbox
    ):

        measurement = (
            self._bbox_to_measurement(
                bbox
            )
        )


        z = np.array(
            measurement,
            dtype=np.float64
        ).reshape(
            (4, 1)
        )


        # Innovation / residual

        innovation = (
            z
            -
            self.H
            @
            self.state
        )


        innovation_covariance = (

            self.H
            @
            self.P
            @
            self.H.T

            +

            self.R
        )


        # Using pseudo-inverse instead of
        # inverse improves numerical robustness.

        kalman_gain = (

            self.P
            @
            self.H.T

            @

            np.linalg.pinv(
                innovation_covariance
            )
        )


        self.state = (

            self.state

            +

            kalman_gain
            @
            innovation
        )


        identity = np.eye(
            8,
            dtype=np.float64
        )


        self.P = (

            identity

            -

            kalman_gain
            @
            self.H

        ) @ self.P


        self._ensure_valid_size()


        return self.get_bbox()


    # ==========================================
    # Convert Bounding Box → Measurement
    # ==========================================

    @staticmethod
    def _bbox_to_measurement(
        bbox
    ):

        x1, y1, x2, y2 = bbox


        width = max(
            1.0,
            float(x2 - x1)
        )


        height = max(
            1.0,
            float(y2 - y1)
        )


        cx = (
            float(x1)
            +
            width / 2.0
        )


        cy = (
            float(y1)
            +
            height / 2.0
        )


        return (
            cx,
            cy,
            width,
            height
        )


    # ==========================================
    # State → Bounding Box
    # ==========================================

    def get_bbox(self):

        cx = float(
            self.state[0, 0]
        )

        cy = float(
            self.state[1, 0]
        )

        width = max(
            1.0,
            float(
                self.state[2, 0]
            )
        )

        height = max(
            1.0,
            float(
                self.state[3, 0]
            )
        )


        x1 = int(
            round(
                cx
                -
                width / 2
            )
        )

        y1 = int(
            round(
                cy
                -
                height / 2
            )
        )

        x2 = int(
            round(
                cx
                +
                width / 2
            )
        )

        y2 = int(
            round(
                cy
                +
                height / 2
            )
        )


        return (
            x1,
            y1,
            x2,
            y2
        )


    def _ensure_valid_size(self):

        self.state[
            2,
            0
        ] = max(
            1.0,
            self.state[
                2,
                0
            ]
        )


        self.state[
            3,
            0
        ] = max(
            1.0,
            self.state[
                3,
                0
            ]
        )