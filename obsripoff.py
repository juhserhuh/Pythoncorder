import pyautogui
import cv2
import numpy as np
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from threading import Thread
from PIL import Image, ImageTk
import time
import pyaudio
import wave
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip

class ScreenRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("Pythoncorder! //since 2024!//")
        self.root.geometry("800x600")
        self.root.configure(bg="#ffffff")

        self.recording = False
        self.out = None
        self.dot_size = 20
        self.dot_position = (30, 30)  # Initial position of the red dot

        self.menu_bar = tk.Menu(root)

        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Start Recording", command=self.start_recording)
        file_menu.add_command(label="Stop Recording", command=self.stop_recording)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        about_menu = tk.Menu(self.menu_bar, tearoff=0)
        about_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="About", menu=about_menu)

        settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        settings_menu.add_command(label="Settings", command=self.show_settings)
        self.menu_bar.add_cascade(label="Settings", menu=settings_menu)

        report_menu = tk.Menu(self.menu_bar, tearoff=0)
        report_menu.add_command(label="Report a Bug", command=self.report_bug)
        self.menu_bar.add_cascade(label="Report", menu=report_menu)

        root.config(menu=self.menu_bar)

        self.speed_label = tk.Label(root, text="Recording Speed:")
        self.speed_label.pack()

        self.speed_slider = tk.Scale(root, from_=0.9, to=2.0, resolution=0.1, orient=tk.HORIZONTAL)
        self.speed_slider.set(1.0)
        self.speed_slider.pack()

        self.volume_label = tk.Label(root, text="Volume:")
        self.volume_label.pack()

        self.volume_slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL)
        self.volume_slider.set(100)
        self.volume_slider.pack()

        self.preview_label = tk.Label(root)
        self.preview_label.pack()

        self.update_preview()

    def update_preview(self):
        frame = self.capture_screen()
        if frame is not None:
            if self.recording:
                frame = cv2.circle(frame, self.dot_position, self.dot_size, (0, 0, 255), -1)  # Add red dot when recording
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert color space to RGB
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.preview_label.imgtk = imgtk  # Store reference to avoid garbage collection
            self.preview_label.config(image=imgtk)

        self.root.after(10, self.update_preview)

    def capture_screen(self):
        screen = pyautogui.screenshot()
        frame = np.array(screen)
        return frame

    def start_recording(self):
        if not self.recording:
            filename = simpledialog.askstring("Filename", "Enter the filename:")
            if filename:
                videos_folder = os.path.join(os.path.expanduser("~"), "Videos")
                if not os.path.exists(videos_folder):
                    os.makedirs(videos_folder)
                self.video_filepath = os.path.join(videos_folder, f"{filename}.avi")
                self.audio_filepath = os.path.join(videos_folder, f"{filename}.wav")
                self.output_filepath = os.path.join(videos_folder, f"{filename}_with_audio.mp4")

                self.out = cv2.VideoWriter(self.video_filepath, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (800, 600))
                self.recording = True
                self.audio_thread = Thread(target=self.record_audio)
                self.video_thread = Thread(target=self.record_video)
                self.audio_thread.start()
                self.video_thread.start()
            else:
                messagebox.showerror("Error", "Filename cannot be empty.")

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.video_thread.join()
            self.audio_thread.join()
            self.out.release()
            self.combine_audio_video()
            messagebox.showinfo("Info", "Recording stopped and saved.")

    def record_video(self):
        while self.recording:
            frame = self.capture_screen()
            if frame is not None:
                frame = cv2.resize(frame, (800, 600))
                self.out.write(frame)
            time.sleep(0.05 / self.speed_slider.get())  # Adjust sleep time based on speed slider value

    def record_audio(self):
        chunk = 1024
        sample_format = pyaudio.paInt16
        channels = 2
        rate = 44100

        p = pyaudio.PyAudio()
        stream = p.open(format=sample_format, channels=channels, rate=rate, frames_per_buffer=chunk, input=True)

        frames = []

        while self.recording:
            data = stream.read(chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(self.audio_filepath, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()

    def combine_audio_video(self):
        video_clip = VideoFileClip(self.video_filepath)
        audio_clip = AudioFileClip(self.audio_filepath).volumex(self.volume_slider.get() / 100)
        final_clip = CompositeVideoClip([video_clip.set_audio(audio_clip)])
        final_clip.write_videofile(self.output_filepath, codec="libx264")

    def on_closing(self):
        if self.recording:
            self.recording = False
            self.video_thread.join()
            self.audio_thread.join()
            self.out.release()
        self.root.destroy()

    def show_about(self):
        messagebox.showinfo("About", "Pythoncorder va.0.1\n\nCreated by juhser!")

    def show_settings(self):
        # Placeholder for settings window
        messagebox.showinfo("Settings", "Settings window will be implemented in future versions.")

    def report_bug(self):
        messagebox.showinfo("Report a Bug", "website wip")

if __name__ == "__main__":
    root = tk.Tk()
    recorder = ScreenRecorder(root)
    root.protocol("WM_DELETE_WINDOW", recorder.on_closing)
    root.mainloop()

