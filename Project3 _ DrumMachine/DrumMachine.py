from tkinter import *
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox
from tkinter import Menu

import time
import wave
import pygame  # Sử dụng pygame thay cho pymedia
import threading
import pickle
import os

MAX_DRUM_NUM = 5


class DrumMachine:
    def __init__(self):
        self.widget_drum_name = []
        self.widget_drum_file_name = [0] * MAX_DRUM_NUM
        self.current_drum_no = 0
        self.keep_playing = True
        pygame.mixer.init()  # Khởi tạo pygame mixer
        self.pattern_list = [None] * 10

    def app(self):
        self.root = Tk()
        self.root.title("Drum Beast")

        self.create_top_menu()
        self.create_top_bar()
        self.create_left_pad()
        self.create_right_pad()
        self.create_play_bar()
        self.create_top_menu()  # Tạo menu
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        self.set_window_icon()
        
        self.root.mainloop()

    def set_window_icon(self):
        try:
            icon_path = r"C:\Users\WINDOWS 11\Downloads\screenshot_2024_11_18_022030_jQ1_icon.ico"
            # Đặt biểu tượng cửa sổ
            self.root.iconbitmap(icon_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set window icon: {e}")

    # Phương thức tạo menu trên thanh công cụ
    def create_top_bar(self):
        top_bar_frame = Frame(self.root)
        top_bar_frame.config(height=25)
        top_bar_frame.grid(row=0, columnspan=12, rowspan=10, padx=5, pady=5)

        Label(top_bar_frame, text="Units:").grid(row=0, column=4)
        self.units = IntVar()
        self.units.set(4)
        self.units_widget = Spinbox(
            top_bar_frame,
            from_=1,
            to=10,
            width=5,
            textvariable=self.units,
            command=self.create_right_pad,
        )  # Callback
        self.units_widget.grid(row=0, column=5)

        Label(top_bar_frame, text="BPUs:").grid(row=0, column=6)
        self.bpu = IntVar()
        self.bpu.set(4)
        self.bpu_widget = Spinbox(
            top_bar_frame,
            from_=1,
            to=8,
            width=5,
            textvariable=self.bpu,
            command=self.create_right_pad,
        )  # Callback
        self.bpu_widget.grid(row=0, column=7)

        Label(top_bar_frame, text="Pattern Number:").grid(row=0, column=1)
        self.patt = IntVar()
        self.patt.set(0)
        self.prevpatvalue = 0  # Để theo dõi lần chọn trước
        Spinbox(
            top_bar_frame,
            from_=0,
            to=9,
            width=5,
            textvariable=self.patt,
            command=self.record_pattern,
        ).grid(row=0, column=2)

        self.pat_name = Entry(top_bar_frame)
        self.pat_name.grid(row=0, column=3, padx=7, pady=2)
        self.pat_name.insert(0, f"Pattern {self.patt.get()}")
        self.pat_name.config(state="readonly")

    def create_left_pad(self):
        left_frame = Frame(self.root)
        left_frame.grid(row=10, column=0, columnspan=6, sticky=W + E + N + S)

        # Load the image using Pillow
        image_path = "C:/Users/WINDOWS 11/OneDrive/Hình ảnh/images/TepNhac.jpg"
        image = Image.open(image_path)
        resized_image = image.resize((18, 18), Image.LANCZOS)
        tbicon = ImageTk.PhotoImage(resized_image)

        for i in range(0, MAX_DRUM_NUM):
            button = Button(left_frame, image=tbicon, command=self.drum_load(i))
            button.image = tbicon
            button.grid(row=i, column=0, padx=5, pady=2)

            self.drum_entry = Entry(left_frame)
            self.drum_entry.grid(row=i, column=4, padx=7, pady=2)

            self.widget_drum_name.append(self.drum_entry)

    def create_right_pad(self):
        bpu = self.bpu.get()
        units = self.units.get()
        c = bpu * units
        right_frame = Frame(self.root)
        right_frame.grid(row=10, column=6, sticky=W + E + N + S, padx=15, pady=2)

        self.button = [[0 for x in range(c)] for _ in range(MAX_DRUM_NUM)]
        for i in range(MAX_DRUM_NUM):
            for j in range(c):
                color = "grey55" if (j / bpu) % 2 else "khaki"

                self.button[i][j] = Button(
                    right_frame,
                    bg=color,
                    width=1,
                    command=self.button_clicked(i, j, bpu),
                )
                self.button[i][j].grid(row=i, column=j)

    def button_clicked(self, i, j, bpu):
        def callback():
            btn = self.button[i][j]
            color = "grey55" if (j / bpu) % 2 else "khaki"
            new_color = "green" if btn.cget("bg") != "green" else color
            btn.config(bg=new_color)

        return callback

    def create_play_bar(self):
        playbar_frame = Frame(self.root, height=15)
        ln = MAX_DRUM_NUM + 10
        playbar_frame.grid(row=ln, columnspan=13, sticky=W + E, padx=15, pady=10)

        self.start_button = Button(
            playbar_frame, text="Play", command=self.play_in_thread
        )
        self.start_button.grid(row=ln, column=1, padx=1)
        print(self.start_button.config())  # In tất cả các tùy chọn cấu hình
        print(self.start_button.config("bg"))  # Chỉ in cấu hình màu nền của nút Play

        stop_button = Button(playbar_frame, text="Stop", command=self.stop_play)
        stop_button.grid(row=ln, column=3, padx=1)
        print(stop_button.config())  # In tất cả các tùy chọn cấu hình
        print(stop_button.config("bg"))  # Chỉ in cấu hình màu nền của nút Stop

        self.loop = BooleanVar()
        loop_button = Checkbutton(
            playbar_frame,
            text="Loop",
            variable=self.loop,
            command=lambda: self.loop_play(self.loop.get()),
        )
        loop_button.grid(row=ln, column=16, padx=1)

        image_path = "C:/Users/WINDOWS 11/OneDrive/Hình ảnh/Ảnh chụp màn hình/Screenshot 2024-10-30 234545.png"
        logo_image = Image.open(image_path)
        logo_resized = logo_image.resize((300, 100), Image.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_resized)

        # Chèn ảnh vào playbar_frame
        logo_label = Label(playbar_frame, image=logo_photo)
        logo_label.image = logo_photo
        logo_label.grid(row=ln, column=100, padx=45, sticky=E)

    def loop_play(self, xval):
        self.loop = xval

    def drum_load(self, drum_no):
        def callback():
            self.current_drum_no = drum_no
            try:
                file_name = filedialog.askopenfilename(
                    defaultextension=".wav",
                    filetypes=[("Wave Files", "*.wav"), ("OGG Files", "*.ogg")],
                )
                if not file_name:
                    return
                try:
                    del self.widget_drum_file_name[drum_no]
                except:
                    pass
                self.widget_drum_file_name.insert(drum_no, file_name)
                drum_name = os.path.basename(file_name)
                self.widget_drum_name[drum_no].delete(0, END)
                self.widget_drum_name[drum_no].insert(0, drum_name)
                """
                # Sử dụng pymedia để phát âm thanh
                f = wave.open(file_name, 'rb')
                sampleRate = f.getframerate()
                channels = f.getnchannels()
                format = sound.AFMT_S16_LE
                snd = sound.Output(sampleRate, channels, format)
                s = f.readframes(300000)
                snd.play(s) """
                # Sử dụng pygame để phát âm thanh
                sound = pygame.mixer.Sound(file_name)
                sound.play()

            except Exception as e:
                messagebox.showerror("Invalid", f"Error loading drum samples: {e}")

        return callback

    def play_sound(self, sound_filename):
        try:
            sound = pygame.mixer.Sound(
                sound_filename
            )  # Sử dụng pygame để tải file âm thanh
            sound.play()  # Phát file âm thanh
        except Exception as e:
            print(f"Error playing sound: {e}")

    def stop_play(self):
        self.keep_playing = False
        self.start_button.config(state="normal")

    def play(self):
        self.keep_playing = True
        while self.keep_playing:  # Thay đổi để sử dụng vòng lặp while
            for i in range(len(self.button[0])):
                if not self.keep_playing:
                    break
                for item in self.button:
                    try:
                        if item[i].cget("bg") == "green":
                            if not self.widget_drum_file_name[self.button.index(item)]:
                                continue
                            sound_filename = self.widget_drum_file_name[
                                self.button.index(item)
                            ]
                            self.play_sound(sound_filename)
                    except:
                        continue
                time.sleep(3 / 4.0)  # Dừng trong khoảng thời gian giữa các nhịp
                if not self.loop:  # Kiểm tra giá trị của self.loop
                    self.keep_playing = False  # Nếu không loop, dừng phát nhạc
                    break
        self.start_button.config(
            state="normal"
        )  # Kích hoạt lại nút Play khi hoàn thành phát nhạc

    def play_in_thread(self):
        self.start_button.config(state="disabled")
        self.keep_playing = True
        self.thread = threading.Thread(target=self.play)
        self.thread.start()

    def record_pattern(self):
        # Lấy giá trị số mẫu, số nhịp trên ô và số lượng ô hiện tại
        pattern_num, bpu, units = self.patt.get(), self.bpu.get(), self.units.get()
        # Cập nhật tên mẫu mới vào Entry widget
        self.pat_name.config(state="normal")
        self.pat_name.delete(0, END)
        self.pat_name.insert(0, f"Pattern {pattern_num}")
        self.pat_name.config(state="readonly")
        # Lưu số mẫu trước đó và cập nhật số mẫu hiện tại
        prevpval = self.prevpatvalue  
        self.prevpatvalue = pattern_num
        c = bpu * units  # Khởi tạo ma trận lưu trạng thái của các nút nhịp
        self.buttonpickleformat = [[0] * c for _ in range(MAX_DRUM_NUM)]
        # Duyệt qua các nút nhịp trong mẫu và lưu trạng thái
        for i in range(MAX_DRUM_NUM):
            for j in range(c):
                if self.button[i][j].config("bg")[-1] == "green":
                    self.buttonpickleformat[i][j] = "active"
        # Lưu thông tin của mẫu hiện tại vào danh sách pattern_list
        self.pattern_list[prevpval] = {"df": self.widget_drum_file_name,"bl": self.buttonpickleformat,"bpu": bpu,"units": units,}
        # Gọi hàm để tái tạo mẫu nhịp dựa trên mẫu mới
        self.reconstruct_pattern(pattern_num, bpu, units)

    def reconstruct_pattern(self, pattern_num, bpu, units):
        # Phần 1: Tải lại các tệp âm thanh trống
        self.widget_drum_file_name = [0] * MAX_DRUM_NUM
        try:
            self.df = self.pattern_list[pattern_num]["df"]
            for i in range(len(self.df)):
                file_name = self.df[i]
                if file_name == 0:
                    self.widget_drum_name[i].delete(0, END)
                    continue
                self.widget_drum_file_name.insert(i, file_name)
                drum_name = os.path.basename(file_name)
                self.widget_drum_name[i].delete(0, END)
                self.widget_drum_name[i].insert(0, drum_name)
        except:
            for i in range(MAX_DRUM_NUM):
                try:
                    self.df
                except:
                    self.widget_drum_name[i].delete(0, END)

        # Phần 2: Khôi phục lại giá trị BPU và Units
        try:
            bpu = self.pattern_list[pattern_num]["bpu"]
            units = self.pattern_list[pattern_num]["units"]
        except:
            return
        self.bpu_widget.delete(0, END)
        self.bpu_widget.insert(0, bpu)
        self.units_widget.delete(0, END)
        self.units_widget.insert(0, units)
        self.create_right_pad()

        # Phần 3: Khôi phục lại mẫu nhịp (Beat Patterns)
        c = bpu * units
        self.create_right_pad()
        try:
            for i in range(MAX_DRUM_NUM):
                for j in range(c):
                    if self.pattern_list[pattern_num]["bl"][i][j] == "active":
                        self.button[i][j].config(bg="green")
        except:
            return

    def create_top_menu(self):
        self.menubar = Menu(self.root)
        # Tạo menu File với các tùy chọn Load, Save và Exit
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Load Project", command=self.load_project)
        self.filemenu.add_command(label="Save Project", command=self.save_project)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.exit_app)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.aboutmenu = Menu(self.menubar, tearoff=0)
        self.aboutmenu.add_command(label="About", command=self.about)
        self.menubar.add_cascade(label="About", menu=self.aboutmenu)
        self.root.config(menu=self.menubar)

    def load_project(self):
        """Phương thức để tải lại dự án đã lưu từ tệp `.bt`."""
        # Mở hộp thoại chọn file
        file_name = filedialog.askopenfilename(
            filetypes=[("Drum Beat File", "*.bt")], title="Load Project"
        )
        if file_name == "":
            return  # Người dùng hủy chọn tệp
        # Đặt tiêu đề cửa sổ thành tên của file đã tải
        self.root.title(os.path.basename(file_name) + " - DrumBeast")
        try:
            # Mở tệp ở chế độ đọc nhị phân
            with open(file_name, "rb") as fh:
                # Đọc dữ liệu đã pickled từ tệp
                while True:
                    try:
                        self.pattern_list = pickle.load(fh)
                    except EOFError:
                        break  # Kết thúc file
            # tái tạo mẫu đầu tiên từ pattern_list
            try:
                self.reconstruct_pattern(
                    0, self.pattern_list[0]["bpu"], self.pattern_list[0]["units"]
                )
            except:
                messagebox.showerror(
                    "Error",
                    "An unexpected error occurred trying to reconstruct patterns",
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load project: {e}")

    def save_project(self):
        """Phương thức để lưu dự án hiện tại vào tệp .bt."""
        self.record_pattern()  # Đảm bảo rằng mẫu cuối cùng đã được ghi lại
        # Mở hộp thoại để người dùng chọn vị trí và tên tệp để lưu
        file_name = filedialog.asksaveasfilename(
            filetypes=[("Drum Beat File", "*.bt")], title="Save project as..."
        )
        if file_name == "":
            return  # Người dùng hủy chọn tệp
        try:
            # Lưu danh sách mẫu đã pickled vào tệp đã chọn
            with open(file_name, "wb") as fh:
                pickle.dump(self.pattern_list, fh)
            # Cập nhật tiêu đề cửa sổ với tên của tệp đã lưu
            self.root.title(os.path.basename(file_name) + " - DrumBeast")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save project: {e}")

    def about(self):
        """Hiển thị thông tin về ứng dụng."""
        messagebox.showinfo("About", "About Info")

    def exit_app(self):
        """Xác nhận thoát ứng dụng."""
        if messagebox.askokcancel("Quit", "Really Quit?"):
            self.root.destroy()


# Run the program if this file is executed as a standalone program
if __name__ == "__main__":
    dm = DrumMachine()
    dm.app()
