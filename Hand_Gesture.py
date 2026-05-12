import cv2
import mediapipe as mp

# Camera on kiya
cap = cv2.VideoCapture(0)

# MediaPipe Hands tool ko setup kiya (Jaise aapne finger counter mein kiya tha)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1) # Hum car chalane ke liye ek hi haath use karenge
mp_draw = mp.solutions.drawing_utils

while True:
    success, img = cap.read()
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    # Agar haath detect hua hai:
    if results.multi_hand_landmarks:
        pass