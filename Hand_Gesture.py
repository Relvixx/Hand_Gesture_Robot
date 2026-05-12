import cv2
import math
import urllib.request
from pathlib import Path

from mediapipe.tasks.python.core import base_options
from mediapipe.tasks.python.vision import hand_landmarker
from mediapipe.tasks.python.vision.core import image as mp_image
from mediapipe.tasks.python.vision.core import vision_task_running_mode as running_mode

MODEL_URL = 'https://storage.googleapis.com/mediapipe-assets/hand_landmarker.task'
MODEL_FILE = Path(__file__).with_name('hand_landmarker.task')


def download_model(model_path: Path) -> Path:
    if model_path.exists():
        return model_path

    model_path.parent.mkdir(parents=True, exist_ok=True)
    print(f'Downloading MediaPipe hand landmarker model to {model_path}...')

    with urllib.request.urlopen(MODEL_URL) as response:
        model_path.write_bytes(response.read())

    return model_path


def draw_landmarks(image, landmarks):
    height, width, _ = image.shape
    for landmark in landmarks:
        x = int(landmark.x * width)
        y = int(landmark.y * height)
        cv2.circle(image, (x, y), 3, (0, 255, 0), -1)


print('System Ready! Camera on ho raha hai...')

model_path = download_model(MODEL_FILE)
base_options = base_options.BaseOptions(model_asset_path=str(model_path))
options = hand_landmarker.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=running_mode.VisionTaskRunningMode.IMAGE,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

cap = cv2.VideoCapture(0)
with hand_landmarker.HandLandmarker.create_from_options(options) as landmarker:
    while True:
        success, img = cap.read()
        if not success:
            break

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_img = mp_image.Image(
            image_format=mp_image.ImageFormat.SRGB,
            data=img_rgb,
        )

        result = landmarker.detect(mp_img)

        if result.hand_landmarks:
            for hand_landmarks in result.hand_landmarks:
                draw_landmarks(img, hand_landmarks)

                dist = math.hypot(
                    hand_landmarks[8].x - hand_landmarks[4].x,
                    hand_landmarks[8].y - hand_landmarks[4].y,
                )

                if (
                    hand_landmarks[8].y < hand_landmarks[5].y
                    and hand_landmarks[12].y < hand_landmarks[9].y
                    and hand_landmarks[16].y < hand_landmarks[13].y
                    and hand_landmarks[20].y < hand_landmarks[17].y
                ):
                    print('Forward')
                elif (
                    hand_landmarks[8].y > hand_landmarks[5].y
                    and hand_landmarks[12].y > hand_landmarks[9].y
                    and hand_landmarks[16].y > hand_landmarks[13].y
                    and hand_landmarks[20].y > hand_landmarks[17].y
                ):
                    print('Stop')
                elif (
                    hand_landmarks[8].y < hand_landmarks[5].y
                    and hand_landmarks[12].y > hand_landmarks[9].y
                    and hand_landmarks[16].y > hand_landmarks[13].y
                    and hand_landmarks[20].y > hand_landmarks[17].y
                ):
                    print('Backward')
                elif (
                    hand_landmarks[8].y < hand_landmarks[5].y
                    and hand_landmarks[12].y < hand_landmarks[9].y
                    and hand_landmarks[16].y > hand_landmarks[13].y
                    and hand_landmarks[20].y > hand_landmarks[17].y
                ):
                    print('Left')
                elif (
                    dist < 0.05
                    and hand_landmarks[12].y < hand_landmarks[9].y
                    and hand_landmarks[16].y < hand_landmarks[13].y
                    and hand_landmarks[20].y < hand_landmarks[17].y
                ):
                    print('Right')

        cv2.imshow('AI Hand Gesture Control', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
