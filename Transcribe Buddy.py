import os
import tkinter as tk
from tkinter import filedialog, ttk
import threading
import whisper
import moviepy.editor as mp

class VideoProcessor:
    def __init__(self):
        # Use the smaller Whisper model (tiny or base for CPU)
        self.model = whisper.load_model("base", device="cpu")  # Change "base" to "tiny" if speed is more important than accuracy
        self.current_video = None
        self.setup_gui()

    def setup_gui(self):
        """Setup the GUI for the application"""
        self.root = tk.Tk()
        self.root.title("Video Transcriber")
        self.root.geometry("600x400")

        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Buttons
        ttk.Button(main_frame, text="Select Video", command=self.select_video).grid(row=0, column=0, pady=5)
        ttk.Button(main_frame, text="Transcribe", command=self.start_transcription).grid(row=1, column=0, pady=5)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, length=400, mode='indeterminate', variable=self.progress_var)
        self.progress_bar.grid(row=2, column=0, pady=10)

        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.grid(row=3, column=0, pady=5)

        # Text display area
        self.text_display = tk.Text(main_frame, height=15, width=60)
        self.text_display.grid(row=4, column=0, pady=5)

    def select_video(self):
        """Open file dialog to select a video file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")]
        )
        if file_path:
            self.current_video = file_path
            self.status_label.config(text=f"Selected: {os.path.basename(file_path)}")
            self.text_display.delete(1.0, tk.END)
            self.text_display.insert(tk.END, "Video successfully loaded. Ready to transcribe!")

    def extract_audio(self, video_path):
        """Extract audio from the video file"""
        self.update_status("Extracting audio...")
        audio_path = video_path.rsplit('.', 1)[0] + '.wav'
        video = mp.VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path, fps=16000, codec="pcm_s16le")
        video.close()
        return audio_path

    def transcribe_video(self):
        """Transcribe video using Whisper"""
        try:
            if not self.current_video:
                self.update_status("Please select a video first")
                return

            # Extract audio
            audio_path = self.extract_audio(self.current_video)
            
            # Transcribe with optimizations
            self.update_status("Transcribing...")
            self.progress_bar.start(10)  # Start loader
            result = self.model.transcribe(audio_path, without_timestamps=True)  # Skip timestamps for speed
            self.progress_bar.stop()  # Stop loader

            # Display the transcription
            self.text_display.delete(1.0, tk.END)
            self.text_display.insert(tk.END, result["text"])

            # Clean up
            os.remove(audio_path)
            self.update_status("Transcription complete!")

        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            self.progress_bar.stop()  # Stop progress animation

    def start_transcription(self):
        """Start transcription in a separate thread"""
        thread = threading.Thread(target=self.transcribe_video)
        thread.daemon = True
        thread.start()

    def update_status(self, message):
        """Update the status label"""
        self.status_label.config(text=message)

    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    # Run the app
    app = VideoProcessor()
    app.run()
