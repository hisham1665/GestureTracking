import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Initialize Camera
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 640)  # width
cap.set(4, 480)  # height

# Variables
prev_x, prev_y = None, None
movement_threshold = 50
last_action_time = time.time()
cooldown = 0.5  # seconds
prev_time = 0

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)  # Mirror effect
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # Draw landmarks if hand detected
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Get wrist position
        h, w, _ = frame.shape
        wrist = hand_landmarks.landmark[0]
        x, y = int(wrist.x * w), int(wrist.y * h)

        # Check movement
        if prev_x is not None and prev_y is not None:
            dx, dy = x - prev_x, y - prev_y

            if time.time() - last_action_time > cooldown:
                if abs(dx) > abs(dy):  # Horizontal
                    if dx > movement_threshold:
                        print("Swipe Right → Press RIGHT")
                        pyautogui.press('right')
                        last_action_time = time.time()
                    elif dx < -movement_threshold:
                        print("Swipe Left → Press LEFT")
                        pyautogui.press('left')
                        last_action_time = time.time()
                else:  # Vertical
                    if dy > movement_threshold:
                        print("Swipe Down → Press DOWN")
                        pyautogui.press('down')
                        last_action_time = time.time()
                    elif dy < -movement_threshold:
                        print("Swipe Up → Press UP")
                        pyautogui.press('up')
                        last_action_time = time.time()

        prev_x, prev_y = x, y

    # Calculate and display FPS
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if prev_time else 0
    prev_time = curr_time
    cv2.putText(frame, f'FPS: {int(fps)}', (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show frame
    cv2.imshow("Hand Gesture Game Control", frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
