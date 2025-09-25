import cv2

video_path = r"C:\Users\deven\Downloads\PUNE\PUNE\video\noti.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video file")
else:
    print("Video file opened successfully")
    ret, frame = cap.read()
    if ret:
        print("Successfully read first frame")
    else:
        print("Failed to read first frame")
    cap.release()
