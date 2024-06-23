import customtkinter as ctk
from yt_dlp import YoutubeDL
import os
from tkinter import filedialog, StringVar, IntVar, Toplevel, Checkbutton, Scrollbar, Frame, Canvas, Label, Button, ttk
import threading
import time
import json
from PIL import Image
SETTINGS_FILE = "settings.json"


# Initialize the app
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("800x800")
app.title("YouTube Video Downloader")

# Global variables
download_folder = StringVar(value=os.path.expanduser("~/Downloads"))
resolution_var = StringVar(value="best")
format_var = StringVar(value="mp4")
progress_var = IntVar(value=0)
speed_var = StringVar(value="")
eta_var = StringVar(value="")
download_thread = None
pause_event = threading.Event()
stop_event = threading.Event()
playlist_videos = []
language_var = StringVar(value="English")
extract_audio_var = IntVar(value=0)
compress_files_var = IntVar(value=0)
organize_folders_var = IntVar(value=0)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as file:
            settings = json.load(file)
            download_folder.set(settings.get("download_folder", os.path.expanduser("~/Downloads")))
            resolution_var.set(settings.get("resolution", "best"))
            format_var.set(settings.get("format", "mp4"))
            language_var.set(settings.get("language", "English"))
    else:
        save_settings()


def save_settings():
    settings = {
        "download_folder": download_folder.get(),
        "resolution": resolution_var.get(),
        "format": format_var.get(),
        "language": language_var.get()
    }
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file)


# Translations dictionary
translations = {
    "English": {
        "title": "Youtube video downloader",
        "youtube_url": "YouTube URL:",
        "select_folder": "Select Folder",
        "resolution": "Resolution:",
        "fetch_playlist": "Download",
        "download": "Download",
        "speed": "Speed: {}",
        "eta": "ETA: {}",
        "paused": "Paused",
        "resume": "Resumed",
        "downloading": "Downloading...",
        "cancelled": "Cancelled",
        "download_complete": "Download complete",
        "error": "Error: {}",
        "no_videos_selected": "No videos selected",
        "fetching_playlist_videos": "Fetching playlist videos...",
        "not_a_playlist_url": "Not a playlist URL",
        "please_enter_url": "Please enter a URL",
        "select_videos_to_download": "Select Videos to Download",
        "download_selected": "Download Selected",
        "compressed":"Compress Files",
        "organized":"Organize into Folders"
    },
    "Arabic": {
        "title": "اليوتيوب فيديوهات تحميل",
        "youtube_url": "يوتيوب رابط",
        "select_folder": "المجلد اختر",
        "resolution": "الدقة:",
        "fetch_playlist": "تحميل",
        "download": "تنزيل",
        "speed": "السرعة: {}",
        "eta": "المتبقى الوقت : {}",
        "paused": "مؤقتا موقوف",
        "resume":"استمر",
        "downloading": "...التحميل جار",
        "cancelled": "أُلغي",
        "download_complete": "التنزيل اكتمل",
        "error": "خطأ: {}",
        "no_videos_selected": "فيديو مقاطع اي اختيار يتم لم",
        "fetching_playlist_videos": "...التشغيل قائمة من الفيديو مقاطع جلب جار",
        "not_a_playlist_url": "التشغيل لقائمة ليس الرابط",
        "please_enter_url": "الرابط ادخال يرجى",
        "select_videos_to_download": "لتنزيلها الفيديو مقاطع اختر",
        "download_selected": "المحدد تنزيل",
        "compressed":"الفيديوهات ضغط",
        "organized":"مجلد الى تحويل"
    }
}
# Function to update UI text based on selected language
def update_language():
    lang = language_var.get()
    title_label.configure(text=translations[lang]["title"])
    url_label.configure(text=translations[lang]["youtube_url"])
    folder_button.configure(text=translations[lang]["select_folder"])
    resolution_label.configure(text=translations[lang]["resolution"])
    fetch_button.configure(text=translations[lang]["fetch_playlist"])
    pause_button.configure(text=translations[lang]["paused"])
    resume_button.configure(text=translations[lang]["resume"])
    cancel_button.configure(text=translations[lang]["cancelled"])
    compress_files_checkbox.configure(text=translations[lang]["compressed"])
    organize_folders_checkbox.configure(text=translations[lang]["organized"])
    status_label.configure(text="")
    
# Load settings at startup
load_settings()

def open_settings():
    settings_window = Toplevel(app)
    settings_window.title("Settings")
    settings_window.geometry("400x200")

    resolution_menu = ctk.CTkOptionMenu(settings_window, variable=resolution_var, values=["best", "144", "240", "360", "480", "720", "1080"])
    resolution_menu.pack(pady=5)
    
    # Language Selection Menu
    language_menu = ctk.CTkOptionMenu(settings_window, variable=language_var, values=["English", "Arabic"], command=lambda _: update_language())
    language_menu.pack(pady=5)

    # Save Settings Button
    save_button = ctk.CTkButton(settings_window, text="Save", command=lambda: [save_settings(), settings_window.destroy()])
    save_button.pack(pady=10)


# Function to select download folder
def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        download_folder.set(folder_selected)
        save_settings()

def fetch_playlist_videos():
    global playlist_videos
    url = url_entry.get()
    if url:
        try:
            status_label.configure(text=translations[language_var.get()]["fetching_playlist_videos"], text_color="yellow")
            app.update_idletasks()  # Update UI immediately

            ydl_opts = {'quiet': True, 'extract_flat': 'in_playlist'}
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                if 'entries' in info_dict:
                    playlist_videos = [{'title': entry['title'], 'url': entry['url']} for entry in info_dict['entries']]
                    show_playlist_selection()
                else:
                    single_video = [{'title': info_dict.get('title', 'Single Video'), 'url': url}]
                    start_download(single_video, is_playlist=False)
        except Exception as e:
            status_label.configure(text=translations[language_var.get()]["error"].format(str(e)), text_color="red")
            print(f"Error: {str(e)}")
    else:
        status_label.configure(text=translations[language_var.get()]["please_enter_url"], text_color="red")
        print("Please enter a URL")

# Function to show playlist selection dialog
def show_playlist_selection():
    selection_window = Toplevel(app)
    selection_window.title(translations[language_var.get()]["select_videos_to_download"])
    selection_window.geometry("600x400")
    selection_window.configure(bg='#2B2B2B')

    # Frame for the checkboxes and scrollbar
    frame = ctk.CTkFrame(selection_window, fg_color="#2B2B2B")
    frame.pack(expand=True, fill='both', padx=20, pady=20)

    canvas = Canvas(frame, bg='#2B2B2B', highlightthickness=0) 
    canvas.pack(side="left", fill="both", expand=True)

    # Custom Scrollbar
    scrollbar = Scrollbar(frame, command=canvas.yview, bg='#2B2B2B', troughcolor='#3A3A3A', activebackground='#4A4A4A', highlightcolor='#4A4A4A')
    scrollbar.pack(side="right", fill="y")

    inner_frame = ctk.CTkFrame(canvas, fg_color="#2B2B2B")
    inner_frame_id = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    check_vars = []
    for video in playlist_videos:
        var = IntVar()
        check_vars.append(var)
        check = ctk.CTkCheckBox(inner_frame, text=video['title'], variable=var)
        check.pack(anchor="w", padx=10, pady=5)

    def on_select():
        selected_videos = [playlist_videos[i] for i, var in enumerate(check_vars) if var.get()]
        selection_window.destroy()
        start_download(selected_videos if selected_videos else playlist_videos, is_playlist=True)

    select_button = ctk.CTkButton(selection_window, text=translations[language_var.get()]["download_selected"], command=on_select)
    select_button.pack(pady=10)

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    inner_frame.bind("<Configure>", on_frame_configure)
    canvas.configure(yscrollcommand=scrollbar.set)

# Function to download selected videos
def start_download(selected_videos, is_playlist):
    global download_thread, pause_event, stop_event
    resolution = resolution_var.get()
    file_format = format_var.get()
    if selected_videos:
        pause_event.clear()
        stop_event.clear()
        download_thread = threading.Thread(target=download_videos, args=(selected_videos, resolution, file_format, is_playlist))
        download_thread.start()
    else:
        status_label.configure(text=translations[language_var.get()]["no_videos_selected"], text_color="red")
        print("No videos selected")

def download_videos(selected_videos, resolution,is_playlist):
    try:
        reset_ui_elements()
        ydl_opts = create_ydl_options(resolution)

        with YoutubeDL(ydl_opts) as ydl:
            for video in selected_videos:
                if stop_event.is_set():
                    break
                download_single_video(ydl, video)

        perform_post_download_actions(download_folder.get())
        update_status_label(selected_videos, is_playlist)
        open_download_folder(download_folder.get())
    except Exception as e:
        handle_error(e)

def reset_ui_elements():
    status_label.configure(text=translations[language_var.get()]["downloading"], text_color="yellow")
    progress_var.set(0)
    progress_bar.set(0)
    speed_var.set("")
    eta_var.set("")
    app.update_idletasks()

def create_ydl_options(resolution):
    download_path = download_folder.get()
    output_template = os.path.join(download_path, '%(title)s.%(ext)s')
    
    ydl_opts = {
        'format': f'{resolution}',
        'outtmpl': output_template,
        'progress_hooks': [progress_hook],
        'postprocessors': [],
        'retry_on_error': True,
    'abort_on_error': False,
    'retries': 10,
    }

    return ydl_opts



def download_single_video(ydl, video):
    try:
        ydl.download([video['url']])
    except Exception as e:
        error_message = str(e)
        if "Video unavailable" in error_message or "removed by the uploader" in error_message:
            print(f"Skipping unavailable video: {video['title']} ({video['url']})")
        else:
            raise e

def perform_post_download_actions(download_path):
    if organize_folders_var.get():
        organize_into_folders(download_path)
    if compress_files_var.get():
        compress_downloaded_files(download_path)

def update_status_label(selected_videos, is_playlist):
    if is_playlist:
        playlist_name = os.path.basename(url_entry.get()).split("?")[0]
        status_label.configure(text=f"{translations[language_var.get()]['download_complete']}: {playlist_name}", text_color="green")
    else:
        video_title = selected_videos[0]['title']
        status_label.configure(text=f"{translations[language_var.get()]['download_complete']}: {video_title}", text_color="green")

def handle_error(e):
    status_label.configure(text=translations[language_var.get()]["error"].format(str(e)), text_color="red")
    print(f"Error: {str(e)}")




def progress_hook(d):
    if stop_event.is_set():
        raise Exception("Download stopped by user")
    if pause_event.is_set():
        while pause_event.is_set():
            if stop_event.is_set():
                raise Exception("Download stopped by user")
            time.sleep(1)

    if d['status'] == 'downloading':
        percent_str = d['_percent_str'].strip().strip('%').strip()
        try:
            progress = float(percent_str)
            progress_var.set(progress)
            progress_bar.set(progress / 100)  # Update progress bar (0-1 scale)
            speed_var.set(translations[language_var.get()]["speed"].format(d['_speed_str'].strip()))
            eta_var.set(translations[language_var.get()]["eta"].format(d['_eta_str'].strip()))
            app.update_idletasks()
        except ValueError:
            print(f"Could not convert progress percentage '{percent_str}' to float.")
    elif d['status'] == 'finished':
        progress_var.set(100)
        progress_bar.set(1.0)
        app.update_idletasks()

# Pause download
def pause_download():
    pause_event.set()
    status_label.configure(text=translations[language_var.get()]["paused"], text_color="orange")

# Resume download
def resume_download():
    pause_event.clear()
    status_label.configure(text=translations[language_var.get()]["resume"], text_color="yellow")

# Cancel download
def cancel_download():
    stop_event.set()
    status_label.configure(text=translations[language_var.get()]["cancelled"], text_color="red")
    
    
import shutil

def organize_into_folders(path):
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(('.mp4', '.mp3')):
                folder_name = os.path.splitext(file)[0]
                folder_path = os.path.join(path, folder_name)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                shutil.move(os.path.join(root, file), os.path.join(folder_path, file))

def compress_downloaded_files(path):
    shutil.make_archive(path, 'zip', path)

import subprocess

def open_download_folder(path):
    if os.name == 'nt':
        os.startfile(path)


# Configure grid layout
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=1)
app.grid_columnconfigure(2, weight=1)
app.grid_columnconfigure(3, weight=1)
for i in range(11):
    app.grid_rowconfigure(i, weight=1)


# Load icon images
pause_icon = ctk.CTkImage(Image.open("E:/Youtube downloader/icons8-pause-30.png"), size=(20, 20))
resume_icon = ctk.CTkImage(Image.open("E:/Youtube downloader/icons8-continue-30.png"), size=(20, 20))
cancel_icon = ctk.CTkImage(Image.open("E:/Youtube downloader/icons8-cancel-30.png"), size=(20, 20))
settings_icon = ctk.CTkImage(Image.open("E:/Youtube downloader/icons8-setting-50.png"), size=(20, 20))

# Title Label
title_label = ctk.CTkLabel(app, text=translations[language_var.get()]["title"], font=ctk.CTkFont(size=24, weight="bold"))
title_label.grid(row=0, column=0,columnspan=4, padx=20, pady=10, sticky="ew")

# Settings Button
settings_button = ctk.CTkButton(app, image=settings_icon, text="", command=open_settings)
settings_button.grid(row=1, column=0, padx=20, pady=10, sticky="w")

# Language Selection Menu
language_menu = ctk.CTkOptionMenu(app, variable=language_var, values=["English", "Arabic"], command=lambda _: update_language())
language_menu.grid(row=1, column=3, padx=20, pady=10, sticky="e")

# URL Entry
url_label = ctk.CTkLabel(app, text=translations[language_var.get()]["youtube_url"], font=ctk.CTkFont(size=14))
url_label.grid(row=2, column=0,columnspan=4, padx=20, pady=10, sticky="ew")

url_entry = ctk.CTkEntry(app)
url_entry.grid(row=3, column=0, columnspan=4, padx=100, pady=10, sticky="ew")

# Folder Selection Button
folder_button = ctk.CTkButton(app, text=translations[language_var.get()]["select_folder"], command=select_folder)
folder_button.grid(row=4, column=0, padx=100, pady=10, sticky="ew")

# Folder Display
folder_label = ctk.CTkLabel(app, textvariable=download_folder, font=ctk.CTkFont(size=12))
folder_label.grid(row=4, column=1, columnspan=3, padx=100, pady=10, sticky="ew")

# Frame for Control Buttons
control_button_frameu0 = ctk.CTkFrame(app)
control_button_frameu0.grid(row=5, column=0, columnspan=4, padx=100, pady=0, sticky="ew")

# Resolution Selection
resolution_label = ctk.CTkLabel(control_button_frameu0, text=translations[language_var.get()]["resolution"], font=ctk.CTkFont(size=14))
resolution_label.pack(side="left", expand=True, padx=20, pady=20)

resolution_options = ["best","bestvideo","worstvideo", "worst"]
resolution_menu = ctk.CTkOptionMenu(control_button_frameu0, variable=resolution_var, values=resolution_options)
resolution_menu.pack(side="left", expand=True, padx=20, pady=20)

# Frame for Centering Buttons
button_frame = ctk.CTkFrame(app)
button_frame.grid(row=7, column=0, columnspan=4, padx=100, pady=10, sticky="ew")

# Frame for Control Buttons
control_button_frameu = ctk.CTkFrame(app)
control_button_frameu.grid(row=8, column=0, columnspan=4, padx=100, pady=5, sticky="ew")

# Compress Files Checkbox
compress_files_checkbox = ctk.CTkCheckBox(control_button_frameu, text=translations[language_var.get()]["compressed"], variable=compress_files_var)
compress_files_checkbox.pack(side="left", expand=True, padx=20, pady=20)

# Organize into Folders Checkbox
organize_folders_checkbox = ctk.CTkCheckBox(control_button_frameu, text=translations[language_var.get()]["organized"], variable=organize_folders_var)
organize_folders_checkbox.pack(side="left", expand=True, padx=20, pady=20)

# Fetch Playlist Button
fetch_button = ctk.CTkButton(button_frame, text=translations[language_var.get()]["download"], command=fetch_playlist_videos)
fetch_button.pack(side="left", expand=True, padx=10, pady=10)

# Progress Bar
progress_bar = ctk.CTkProgressBar(app, variable=progress_var)
progress_bar.grid(row=9, column=0, columnspan=4, padx=100, pady=10, sticky="ew")

# Speed and ETA Labels
speed_label = ctk.CTkLabel(app, textvariable=speed_var, font=ctk.CTkFont(size=12))
speed_label.grid(row=12, column=0, columnspan=2, padx=100, pady=10, sticky="ew")

eta_label = ctk.CTkLabel(app, textvariable=eta_var, font=ctk.CTkFont(size=12))
eta_label.grid(row=12, column=2, columnspan=2, padx=100, pady=10, sticky="ew")

# Status Label
status_label = ctk.CTkLabel(app, text="", font=ctk.CTkFont(size=12))
status_label.grid(row=11, column=0, columnspan=4, padx=100, pady=10, sticky="ew")

# Frame for Control Buttons
control_button_frame = ctk.CTkFrame(app)
control_button_frame.grid(row=10, column=0, columnspan=4, padx=100, pady=5, sticky="ew")

# Control Buttons
pause_button = ctk.CTkButton(control_button_frame, image=pause_icon, command=pause_download,text="")
pause_button.pack(side="left", expand=True, padx=20, pady=20)

resume_button = ctk.CTkButton(control_button_frame, image=resume_icon, command=resume_download,text="")
resume_button.pack(side="left", expand=True, padx=20, pady=20)

cancel_button = ctk.CTkButton(control_button_frame, image=cancel_icon, command=cancel_download,text="")
cancel_button.pack(side="left", expand=True, padx=20, pady=20)

# Load and apply settings on startup
update_language()

# Run the app
app.mainloop()
