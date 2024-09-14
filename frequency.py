import time
import cv2
import mediapipe as mp
import numpy as np
import requests
from pythonosc import osc_message_builder
from pythonosc import udp_client


mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

camera_index= 1
prev_left_wrist = None
prev_right_wrist = None
prev_time = None
show_video = True

def calculate_velocity(curr_wrist, prev_wrist, time_diff):
    if prev_wrist is None or time_diff == 0:
        return 0, 0
    # Calculate velocity in x and y direction
    velocity_x = (curr_wrist.x - prev_wrist.x) / time_diff
    velocity_y = (curr_wrist.y - prev_wrist.y) / time_diff
    return velocity_x, velocity_y

cap = cv2.VideoCapture(camera_index)  # Camera setup
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        try:
            landmarks = results.pose_landmarks.landmark
        except:
            pass

        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
        right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]

        # Get current time
        curr_time = time.time()
        
        if prev_time is not None:
            time_diff = curr_time - prev_time

            # Calculate velocity for both wrists
            left_wrist_velocity = calculate_velocity(left_wrist, prev_left_wrist, time_diff)
            right_wrist_velocity = calculate_velocity(right_wrist, prev_right_wrist, time_diff)

            # Display the velocity on the video feed
            left_wrist_velocity_text = f"Left wrist velocity: x={left_wrist_velocity[0]:.2f}, y={left_wrist_velocity[1]:.2f}"
            right_wrist_velocity_text = f"Right wrist velocity: x={right_wrist_velocity[0]:.2f}, y={right_wrist_velocity[1]:.2f}"
            
            if show_video:
                cv2.putText(image, left_wrist_velocity_text, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.putText(image, right_wrist_velocity_text, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)

        # Update previous wrist positions and time
        prev_left_wrist = left_wrist
        prev_right_wrist = right_wrist
        prev_time = curr_time

        # Rest of your existing code
        cv2.imshow("feed", image)
        
        key = cv2.waitKey(10) & 0xFF
        if key == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
