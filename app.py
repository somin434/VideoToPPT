import threading
import queue
import traceback
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from converter import VideoToSlides, ConversionConfig


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Video → PPTX / PDF")
        self.geometry("760x600")
        self.minsize(700, 540)

        self.msg_queue = queue.Queue()
        self.worker = None

        self.video_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.sample_fps_var = tk.DoubleVar(value=3.0)
        self.stable_var = tk.DoubleVar(value=1.0)
        self.change_var = tk.DoubleVar(value=0.035)
        self.similarity_var = tk.DoubleVar(value=0.94)
        self.min_gap_var = tk.DoubleVar(value=1.5)
        self.crop_var = tk.BooleanVar(value=False)

        self._build()
        self.after(100, self._poll_queue)

    def _build(self):
        pad = {"padx": 12, "pady": 7}

        top = ttk.Frame(self)
        top.pack(fill="x", **pad)
        ttk.Label(top, text="MP4 영상", width=12).grid(row=0, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.video_var).grid(row=0, column=1, sticky="ew")
        ttk.Button(top, text="찾아보기", command=self.choose_video).grid(row=0, column=2, padx=(8,0))
        top.columnconfigure(1, weight=1)

        out = ttk.Frame(self)
        out.pack(fill="x", **pad)
        ttk.Label(out, text="출력 폴더", width=12).grid(row=0, column=0, sticky="w")
        ttk.Entry(out, textvariable=self.output_var).grid(row=0, column=1, sticky="ew")
        ttk.Button(out, text="폴더 선택", command=self.choose_output).grid(row=0, column=2, padx=(8,0))
        out.columnconfigure(1, weight=1)

        options = ttk.LabelFrame(self, text="추출 설정")
        options.pack(fill="x", **pad)

        labels = [
            ("분석 FPS", self.sample_fps_var, "높일수록 짧은 슬라이드를 잘 잡지만 느려집니다."),
            ("안정 시간(초)", self.stable_var, "슬라이드가 이 시간 동안 안정된 뒤 캡처합니다."),
            ("변화 임계값", self.change_var, "낮추면 작은 화면 변화도 감지합니다."),
            ("중복 유사도", self.similarity_var, "높을수록 비슷한 슬라이드를 더 많이 제거합니다."),
            ("최소 간격(초)", self.min_gap_var, "슬라이드 후보 사이의 최소 시간 간격입니다."),
        ]
        for i, (label, var, hint) in enumerate(labels):
            ttk.Label(options, text=label, width=18).grid(row=i, column=0, sticky="w", padx=10, pady=5)
            ttk.Spinbox(options, textvariable=var, from_=0.01, to=10, increment=0.05, width=10).grid(row=i, column=1, sticky="w")
            ttk.Label(options, text=hint, foreground="#666").grid(row=i, column=2, sticky="w", padx=10)
        ttk.Checkbutton(options, text="화면 가장자리 5% 자동 제외", variable=self.crop_var).grid(
            row=len(labels), column=1, columnspan=2, sticky="w", pady=7
        )

        action = ttk.Frame(self)
        action.pack(fill="x", **pad)
        self.start_btn = ttk.Button(action, text="변환 시작", command=self.start)
        self.start_btn.pack(side="left")
        self.progress = ttk.Progressbar(action, mode="determinate")
        self.progress.pack(side="left", fill="x", expand=True, padx=12)

        log_frame = ttk.LabelFrame(self, text="진행 상황")
        log_frame.pack(fill="both", expand=True, **pad)
        self.log = tk.Text(log_frame, wrap="word", height=18, state="disabled")
        self.log.pack(fill="both", expand=True, padx=6, pady=6)

        ttk.Label(
            self,
            text="결과: PPTX + PDF + 추출 이미지 + 타임스탬프 CSV",
            foreground="#555"
        ).pack(anchor="w", padx=14, pady=(0, 12))

    def choose_video(self):
        path = filedialog.askopenfilename(
            title="MP4 영상 선택",
            filetypes=[("MP4 video", "*.mp4"), ("Video files", "*.mp4;*.mov;*.mkv;*.avi"), ("All files", "*.*")]
        )
        if path:
            self.video_var.set(path)
            if not self.output_var.get():
                self.output_var.set(str(Path(path).parent / (Path(path).stem + "_slides")))

    def choose_output(self):
        path = filedialog.askdirectory(title="출력 폴더 선택")
        if path:
            self.output_var.set(path)

    def write_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def start(self):
        video = Path(self.video_var.get().strip())
        out = Path(self.output_var.get().strip()) if self.output_var.get().strip() else video.parent / f"{video.stem}_slides"

        if not video.exists():
            messagebox.showerror("오류", "MP4 파일을 선택하세요.")
            return

        out.mkdir(parents=True, exist_ok=True)
        self.start_btn.configure(state="disabled")
        self.progress["value"] = 0
        self.write_log("=" * 60)
        self.write_log(f"입력: {video}")
        self.write_log(f"출력: {out}")

        crop = (0.05, 0.05, 0.95, 0.95) if self.crop_var.get() else (0, 0, 1, 1)

        config = ConversionConfig(
            sample_fps=float(self.sample_fps_var.get()),
            stable_seconds=float(self.stable_var.get()),
            change_threshold=float(self.change_var.get()),
            similarity=float(self.similarity_var.get()),
            min_gap=float(self.min_gap_var.get()),
            crop=crop,
        )

        self.worker = threading.Thread(
            target=self._convert,
            args=(video, out, config),
            daemon=True
        )
        self.worker.start()

    def _convert(self, video, out, config):
        try:
            converter = VideoToSlides(config)
            result = converter.run(
                video,
                out,
                progress=lambda value, msg: self.msg_queue.put(("progress", value, msg))
            )
            self.msg_queue.put(("done", result))
        except Exception as e:
            self.msg_queue.put(("error", f"{e}\n\n{traceback.format_exc()}"))

    def _poll_queue(self):
        try:
            while True:
                item = self.msg_queue.get_nowait()
                kind = item[0]
                if kind == "progress":
                    _, value, msg = item
                    self.progress["value"] = value
                    self.write_log(msg)
                elif kind == "done":
                    result = item[1]
                    self.progress["value"] = 100
                    self.write_log("")
                    self.write_log(f"완료: {result['count']}개 슬라이드")
                    self.write_log(f"PPTX: {result['pptx']}")
                    self.write_log(f"PDF : {result['pdf']}")
                    self.write_log(f"이미지: {result['images']}")
                    self.write_log(f"CSV: {result['csv']}")
                    self.start_btn.configure(state="normal")
                    messagebox.showinfo(
                        "변환 완료",
                        f"{result['count']}개 슬라이드를 만들었습니다.\n\n"
                        f"PPTX:\n{result['pptx']}\n\nPDF:\n{result['pdf']}"
                    )
                elif kind == "error":
                    self.write_log(item[1])
                    self.start_btn.configure(state="normal")
                    messagebox.showerror("변환 실패", item[1].split("\n\n")[0])
        except queue.Empty:
            pass
        self.after(100, self._poll_queue)


if __name__ == "__main__":
    App().mainloop()
