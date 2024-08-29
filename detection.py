import cv2
import mediapipe as mp
import numpy as np
import socket

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Set up UDP socket for communication with Pure Data
UDP_IP = "127.0.0.1"  # Localhost
UDP_PORT = 3333       # The same port used in your Pure Data patch
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_data(left_shoulder, right_shoulder):
    left_shoulder_x = left_shoulder.x
    right_shoulder_x = right_shoulder.x
   
    center = left_shoulder_x/2
    center = 5
    # Convert coordinates to a byte array and send them over UDPq
    data = f"{center}"
    print(data)
    sock.sendto(data.encode('utf-8'), (UDP_IP, UDP_PORT))

    
#VIDEO FEED
cap = cv2.VideoCapture(0) # 0 - index of built-in laptop camera
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose: ## Mediapipe instance
    while cap.isOpened():
        ret, frame = cap.read()

        # Detection & Render

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        results = pose.process(image) # Make Detection

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        

        #Extract Landmarks
        try:
            landmarks = results.pose_landmarks.landmark
        except:
            pass

        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

        send_data(left_shoulder, right_shoulder)

        # Format text to display
        left_shoulder_text = f"Left Shoulder: x={left_shoulder.x:.2f}, z={left_shoulder.z:.2f}"
        right_shoulder_text = f"Right Shoulder: x={right_shoulder.x:.2f}, z={right_shoulder.z:.2f}"

        # Put text on the frame
        cv2.putText(image, left_shoulder_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(image, right_shoulder_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)



        #Render
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(245,117,66), thickness = 2, circle_radius = 2),
                                  mp_drawing.DrawingSpec(color=(245,117,66), thickness = 2, circle_radius = 2)
                                  )

        
        cv2.imshow("feed", image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows

