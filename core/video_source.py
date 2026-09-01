import cv2


class VideoSource:

    def __init__(self, source=0):
        self.source = source
        self.cap = None

    def open(self):

        self.cap = cv2.VideoCapture(self.source)

        if not self.cap.isOpened():
            raise RuntimeError(
                f"Unable to open video source: {self.source}"
            )

    def read(self):

        if self.cap is None:
            return False, None

        return self.cap.read()

    def get_width(self):

        return int(
            self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        )

    def get_height(self):

        return int(
            self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )

    def get_fps(self):

        return self.cap.get(
            cv2.CAP_PROP_FPS
        )

    def release(self):

        if self.cap is not None:
            self.cap.release()