import cv2
import mediapipe as mp
import numpy as np
import requests
from pythonosc import osc_message_builder
from pythonosc import udp_client


mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

draw_landmarks = True
show_video = True
camera_index = 1 # switch to 1 for mac users


toggle_text_1 = "Controls:"
toggle_text_2 = "t - toggle landmarks"
toggle_text_3 = "v - toggle video feed"

# Starting y-coordinate and vertical spacing
y_position = 90
vertical_spacing = 30
osc_client = udp_client.SimpleUDPClient("127.0.0.1", 9000) 

def send_data(left_wrist, right_wrist, nose):
        try:
            #abs values of left and right wrist
            dist_x = abs(right_wrist.x - left_wrist.x) 
            dist_y = abs(right_wrist.y - left_wrist.y)
            nose_x = nose.x

            # sending dist in x
            osc_message_dist_x = osc_message_builder.OscMessageBuilder(address="/dist_x")
            osc_message_dist_x.add_arg(dist_x)
            osc_message_dist_x = osc_message_dist_x.build()
            osc_client.send(osc_message_dist_x)

            # sending dist in y
            osc_message_dist_y = osc_message_builder.OscMessageBuilder(address="/dist_y")
            osc_message_dist_y.add_arg(dist_y)
            osc_message_dist_y = osc_message_dist_y.build()
            osc_client.send(osc_message_dist_y)
           
           # sending nose x pos
            osc_message_nose_x = osc_message_builder.OscMessageBuilder(address="/nose_x")
            osc_message_nose_x.add_arg(nose_x)
            osc_message_nose_x = osc_message_nose_x.build()
            osc_client.send(osc_message_nose_x)
           

            
        except requests.exceptions.RequestException as e:
            print("error while sending coordinates")
            raise e


#VIDEO FEED
cap = cv2.VideoCapture(camera_index) # change to camera option
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
        nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
        send_data(left_wrist, right_wrist, nose)

        # Format text to display
        left_wrist_text = f"Left wrist: x={left_wrist.x:.2f}, y={left_wrist.y:.2f}"
        right_wrist_text = f"Right wrist: x={right_wrist.x:.2f}, y={right_wrist.y:.2f}"
        nose_text = f"Nose: x={nose.x:.2f}"

        if show_video:
            cv2.putText(image, left_wrist_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(image, right_wrist_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(image, nose_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)

            # Render landmarks if enabled
            if draw_landmarks:
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                          mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                          mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2))

            # Show video if enabled
            cv2.imshow("feed", image)
        

        key = cv2.waitKey(10) & 0xFF
        if key == ord('q'):  # Quit if 'q' is pressed
            break
        elif key == ord('t'):  # Toggle drawing if 't' is pressed
            draw_landmarks = not draw_landmarks  # Toggle the flag
        elif key == ord('v'):  # Toggle video output if 'v' is pressed
            show_video = not show_video  # Toggle video visibility
            if not show_video:  # If video is turned off, display a black screen
                black_frame = np.zeros_like(image)  # Create a black frame of the same size as the current image
                cv2.putText(black_frame, toggle_text_1, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.putText(black_frame, toggle_text_2, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.putText(black_frame, toggle_text_3, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.imshow("feed", black_frame)
                

    cap.release()
    cv2.destroyAllWindows

