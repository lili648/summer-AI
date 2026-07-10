import os
import time
import cv2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk


class CameraApp:
    """摄像头界面：打开摄像头 / 拍照 / 关闭。"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("摄像头界面")
        self.root.geometry("960x540")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.cap = None
        self.running = False
        self.current_frame = None  # 保存当前帧，拍照时使用

        # ---------- 按钮区 ----------
        btn_frame = tk.Frame(root)
        btn_frame.pack(side="bottom", fill="x", pady=8)

        self.btn_open = tk.Button(
            btn_frame, text="打开摄像头", width=12, command=self.open_camera
        )
        self.btn_open.pack(side="left", padx=6)

        self.btn_capture = tk.Button(
            btn_frame, text="拍照", width=12, command=self.capture_photo,
            state=tk.DISABLED,
        )
        self.btn_capture.pack(side="left", padx=6)

        self.btn_exit = tk.Button(
            btn_frame, text="关闭", width=12, command=self.on_close
        )
        self.btn_exit.pack(side="left", padx=6)

        # ---------- 画面显示区 ----------
        self.video_label = tk.Label(root, bg="black", text="点击「打开摄像头」开始")
        self.video_label.pack(fill="both", expand=True)

    def open_camera(self):
        """打开摄像头并开始循环读取画面。"""
        if self.running:
            return

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("错误", "无法打开摄像头")
            self.cap = None
            return

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)

        self.running = True
        self.btn_open.config(state=tk.DISABLED)
        self.btn_capture.config(state=tk.NORMAL)
        self.video_label.config(text="")
        self.update_frame()

    def capture_photo(self):
        """保存当前帧到 data 文件夹。"""
        if self.current_frame is None:
            messagebox.showwarning("提示", "暂无画面，请先打开摄像头")
            return

        # 确保 data 目录存在
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        os.makedirs(data_dir, exist_ok=True)

        # 用时间戳命名，避免覆盖
        filename = time.strftime("%Y%m%d_%H%M%S") + ".jpg"
        filepath = os.path.join(data_dir, filename)

        # OpenCV 默认 BGR → 转 RGB 再保存
        frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame_rgb)
        image.save(filepath, quality=95)

        messagebox.showinfo("拍照成功", f"已保存到 data/{filename}")

    def update_frame(self):
        """循环读取一帧并显示在界面上。"""
        if not self.running or self.cap is None:
            return

        ret, frame = self.cap.read()
        if not ret:
            messagebox.showerror("错误", "无法获取画面")
            self.on_close()
            return

        self.current_frame = frame.copy()  # 保存原始帧（BGR 格式）

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        w = max(self.video_label.winfo_width(), 1)
        h = max(self.video_label.winfo_height(), 1)
        image = image.resize((w, h))
        photo = ImageTk.PhotoImage(image)

        self.video_label.config(image=photo)
        self.video_label.image = photo

        self.root.after(15, self.update_frame)

    def on_close(self):
        """关闭窗口前释放资源。"""
        self.running = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
