import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.core import base_options
import cv2

class HandDetector:
    def __init__(self, model_path):
        options = vision.HandLandmarkerOptions(
            base_options=base_options.BaseOptions(
                model_asset_path=model_path
            ),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

    def detect(self, frame, timestamp):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )
        result = self.detector.detect_for_video(mp_image, timestamp)

        if result.hand_landmarks:
            return result.hand_landmarks[0]
        return None