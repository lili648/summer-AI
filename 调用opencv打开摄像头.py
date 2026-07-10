import cv2

# 0 是默认摄像头编号，有多个摄像头时可改为 1、2...
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

# 可选：设置分辨率
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:
    ret, frame = cap.read()  # 读取一帧
    if not ret:
        print("Cannot receive frame")
        break

    cv2.imshow('frame', frame)  # 显示画面

    # 按 q 退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()