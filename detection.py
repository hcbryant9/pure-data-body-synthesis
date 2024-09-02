import cv2
import mediapipe as mp
import numpy as np
import requests
import time
from pythonosc import osc_message_builder
from pythonosc import udp_client


mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


osc_client = udp_client.SimpleUDPClient("127.0.0.1", 9000) 

def send_data(left_wrist, right_wrist):
        try:
            # sending left wrist x
            osc_message_l_wrist_x = osc_message_builder.OscMessageBuilder(address="/l_wrist_x")
            osc_message_l_wrist_x.add_arg(left_wrist.x)
            osc_message_l_wrist_x = osc_message_l_wrist_x.build()
            osc_client.send(osc_message_l_wrist_x)
            print("left wrist x sent over OSC")

            # sending left wrist z
            osc_message_l_wrist_z = osc_message_builder.OscMessageBuilder(address="/l_wrist_z")
            osc_message_l_wrist_z.add_arg(left_wrist.z)
            osc_message_l_wrist_z = osc_message_l_wrist_z.build()
            osc_client.send(osc_message_l_wrist_z)
            print("left wrist z sent over OSC.")

            # sending right wrist x
            osc_message_r_wrist_x = osc_message_builder.OscMessageBuilder(address="/r_wrist_x")
            osc_message_r_wrist_x.add_arg(right_wrist.x)
            osc_message_r_wrist_x = osc_message_r_wrist_x.build()
            osc_client.send(osc_message_r_wrist_x)
            print("right wrist x sent over OSC")

             # sending right wrist z
            osc_message_r_wrist_z = osc_message_builder.OscMessageBuilder(address="/r_wrist_z")
            osc_message_r_wrist_z.add_arg(right_wrist.z)
            osc_message_r_wrist_z = osc_message_r_wrist_z.build()
            osc_client.send(osc_message_r_wrist_z)
            print("right wrist z sent over OSC")

            
        except requests.exceptions.RequestException as e:
            print("error while sending coordinates")
            raise e


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

        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
        right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]

        send_data(left_wrist, right_wrist)

        # Format text to display
        left_wrist_text = f"Left wrist: x={left_wrist.x:.2f}, z={left_wrist.z:.2f}"
        right_wrist_text = f"Right wrist: x={right_wrist.x:.2f}, z={right_wrist.z:.2f}"

        # Put text on the frame
        cv2.putText(image, left_wrist_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(image, right_wrist_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)



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

