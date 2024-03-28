# 1. Add link to folder (open folder directly as a temp solution)
# 2. Add instruction when files are not ready(Bingo)
# 3. Allow multiple trimmed files: not urgent, need more design, like save classes
# 4. Wrap as a local app with desktop icon
# What are my assumptions, start with the strongest ones, what do I need to guide my users through

import os
import sys
import time
import threading

import subprocess
import ffmpeg
from audio_offset_finder.audio_offset_finder import find_offset_between_files
import tkinter as tk
from tkinter import scrolledtext
import webbrowser
from moviepy.editor import VideoFileClip, clips_array

class DanceSong:
    def __init__(self, repo_dir, ref_video_name="ref.mp4", my_video_name="me.mp4"):
        self.repo_dir = repo_dir
        if not os.path.exists(self.repo_dir):
            os.makedirs(self.repo_dir)
        
        self.ref_video_name = ref_video_name
        self.ref_video_dir = os.path.join(self.repo_dir, self.ref_video_name)
    
        
        self.my_video_name = my_video_name
        self.my_video_dir = os.path.join(self.repo_dir, self.my_video_name)
        
        self.ref_audio_dir = None
        self.my_audio_dir = None
        
        self.trimmed_dir = []

    def process(self):
        
        self.ref_audio_dir = self._extract_audio_from_video(self.ref_video_dir)
        self.my_audio_dir = self._extract_audio_from_video(self.my_video_dir)

        # Run audio sync command and get the time
        if self.ref_audio_dir != None and self.my_audio_dir != None:
            sync_time = self.run_audio_sync(self.my_audio_dir, self.ref_audio_dir)

        # Trim the video and save
        sync_video_dir = self._trim_video(sync_time)
        self._open_repo_directory()
        self._combine_videos(sync_video_dir)
        
        #TODO: side-by-side video here
        return "Processing complete for " + self.repo_dir

    def _extract_audio_from_video(self, video_file):

        output_audio_file = os.path.join(self.repo_dir, os.path.splitext(os.path.basename(video_file))[0] + '.mp3')

        try:
            # Run ffmpeg command to extract audio
            ffmpeg.input(video_file).output(output_audio_file, acodec='mp3').run(overwrite_output=True)
            return output_audio_file
        except ffmpeg.Error as e:
            print("An error occurred: " + str(e))            
            return None 

    def run_audio_sync(self, my_audio, ref_audio):
        # Find the time offset of my_video within ref_video
        results = find_offset_between_files(my_audio, ref_audio)
        # Return the sync time
        return results["time_offset"]

    def _trim_video(self, sync_time):

        # output name with sync time
        output_video_path = os.path.join(self.repo_dir, 'sync_' + str(sync_time) + '_'+ self.my_video_name)

        try:
            # Run ffmpeg command to trim the video
            ffmpeg.input(self.my_video_dir, ss=sync_time).output(output_video_path).run(overwrite_output=True)

            
            print(f"Trimmed video saved to: {output_video_path}")
            self.trimmed_dir.append(output_video_path)
        except ffmpeg.Error as e:
            print(f"An error occurred while trimming {video_file}: {e}")
        
        return output_video_path
    
    def _combine_videos(self, sync_video_dir):

        # Split the file path into directory (repo) and filename with extension
        directory_path, filename_with_extension = os.path.split(sync_video_dir)
        
        combined_video_dir = os.path.join(directory_path, f"combined_{filename_with_extension}")
        
        # Load the two videos
        video1 = VideoFileClip(self.ref_video_dir)
        video2 = VideoFileClip(sync_video_dir)
        # Determine the minimum height to use for both videos
        min_height = min(video1.size[1], video2.size[1])

        # Calculate target aspect ratio
        target_aspect_ratio = 8 / 10

        video1_resized = video1.resize(height=min_height)
        video2_resized = video2.resize(height=min_height)

        # Calculate original aspect ratios
        aspect_ratio1 = video1_resized.size[0] / min_height
        aspect_ratio2 = video2_resized.size[0] / min_height
        print(aspect_ratio2)

        # Check if any of the videos' original width to the minimum height is <= 8:10
        if aspect_ratio1 <= target_aspect_ratio or aspect_ratio2 <= target_aspect_ratio:

            # Calculate total width for 16:10 aspect ratio with the minimum height; total ratio can change based on target_aspect_ratio
            total_width_for_16_10 = 2 * target_aspect_ratio * min_height

            # Adjust width of videos accordingly
            if aspect_ratio1 <= target_aspect_ratio and aspect_ratio2 <= target_aspect_ratio:
                # If both videos are within the aspect ratio limit, keep original widths
                new_width1 = video1.size[0]
                new_width2 = video2.size[0]
                video1_cropped = video1_resized
                video2_cropped = video2_resized
            elif aspect_ratio1 <= target_aspect_ratio:
                # Adjust video2's width to meet the 16:10 aspect ratio requirement
                new_width1 = video1_resized.size[0]
                new_width2 = total_width_for_16_10 - new_width1
                video2_cropped = video2_resized.crop(x_center=video2_resized.size[0]/2, width=new_width2)
                video1_cropped = video1_resized
            else:
                # Adjust video1's width to meet the 16:10 aspect ratio requirement
                new_width2 = video2_resized.size[0]
                new_width1 = total_width_for_16_10 - new_width2
                video1_cropped = video1_resized.crop(x_center=video1_resized.size[0]/2, width=new_width1)
                video2_cropped = video2_resized
        else:
            # If neither video is within the aspect ratio limit, resize both to minimum height without cropping
            new_width = min_height * target_aspect_ratio

            # Crop both videos symmetrically to the target aspect ratio
            video1_cropped = video1_resized.crop(x_center=video1_resized.size[0]/2, width=new_width)
            video2_cropped = video2_resized.crop(x_center=video2_resized.size[0]/2, width=new_width)


        # Combine the resized (and possibly width-adjusted) videos side by side
        final_clip = clips_array([[video1_cropped.set_audio(video1.audio), video2_cropped]])

        # Determine the highest fps from both videos
        highest_fps = max(video1.fps, video2.fps)

        # Write the result to a file with the highest fps and original audio from video 1
        
        final_clip.write_videofile(combined_video_dir, codec="libx264", fps=highest_fps)

    
    def _open_repo_directory(self):
        global dir_open
        """ Open the repository directory. """
        if os.path.exists(self.repo_dir) and dir_open == False:
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(self.repo_dir)
                elif os.name == 'posix':  # macOS, Linux
                    subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', self.repo_dir])
                dir_open = True
            except Exception as e:
                print(f"Error opening directory: {e}")
    
#     def _open_directory(event, path):
#         print(path)
#         """ Function to open a given directory """
#         index = chat_display.index("@%s,%s" % (event.x, event.y))
#         tag_indices = chat_display.tag_ranges('link')
#         for start, end in zip(tag_indices[0::2], tag_indices[1::2]):
#             if chat_display.compare(start, '<=', index) and chat_display.compare(index, '<', end):
#                 path = chat_display.get(start, end)
#                 if os.path.exists(path):
#                     try:
#                         subprocess.Popen(['open', path])
#                     except PermissionError as e:
#                         print(f"Error: {e}")
#                         print("Please grant permission to access the directory.\n1. Open System Preferences\n2. Go to Security & Privacy\n3. Grant the necessary permissions to this application.")
#                         # show_permission_instructions()

#                     # TODO: test on different systems
#                     # try:
#                     # Change the command based on the operating system
#     #                 if os.name == 'nt':  # for Windows
#     #                     os.startfile(path)
#     #                 elif os.name == 'posix':  # for macOS, Linux
#     #                     subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', path])
#     #             except Exception as e:
#     #                 messagebox.showerror("Error", f"Unable to open the directory: {e}")

#                 else:
#                     messagebox.showwarning("Warning", "Directory does not exist.")
                
#     def _make_directory_clickable(self, path):
#         chat_history.config(state="normal")
#         chat_history.insert('end', path + '\n')
#         chat_history.tag_add("link", "end - 1 lines linestart", "end - 1 lines lineend")
#         chat_history.tag_config("link", foreground="blue", underline=True)
#         chat_history.tag_bind("link", "<Button-1>", lambda event, path=path: self._open_directory(event, path))
#         chat_history.config(state="disabled")


class DanceSongMonitor:
    def __init__(self, repo_dir, ready_event, ref_video_name="ref.mp4", my_video_name="me.mp4"):
        self.repo_dir = repo_dir
        self.ready_event = ready_event
        self.ref_video_name = ref_video_name
        self.my_video_name = my_video_name

    def is_file_ready(self, filename):
        """Check if a specified file exists and is not being written to."""
        file_path = os.path.join(self.repo_dir, filename)
        if not os.path.exists(file_path):
            return False
        try:
            with open(file_path, 'a'):
                pass
            return True
        except IOError:
            return False
        
    def _open_repo_directory(self):
        """ Open the repository directory. """
        global dir_open
        if os.path.exists(self.repo_dir) and dir_open == False:
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(self.repo_dir)
                elif os.name == 'posix':  # macOS, Linux
                    subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', self.repo_dir])
                dir_open = True
            except Exception as e:
                print(f"Error opening directory: {e}")
    
    def start_monitoring(self):
        count = 0
        instructions_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        try:
            while True:
                if all(self.is_file_ready(file_name) for file_name in [self.ref_video_name, self.my_video_name]):
                    self.ready_event.set()  # Signal that files are ready
                    
                    instructions_label.config(text="Video files are ready. Processing...")  # Update instructions
                     # Set the color of the instruction label
                    instructions_label.config(fg="white", bg="green")  # fg is foreground color, bg is background color

                    break
                
                # show instructions only once
                if count < 1:
                    instructions_text = (f"Please put your dance reference video '{self.ref_video_name}'\n"
                     f"and your own dance video '{self.my_video_name}'\n"
                     f"into the directory: '{self.repo_dir}'")
                    
                    instructions_label.config(text=instructions_text)  # Show instructions

                    # Set the color of the instruction label
                    instructions_label.config(fg="white", bg="red")  # fg is foreground color, bg is background color
                    self._open_repo_directory()
                    count += 1              
                time.sleep(1)
        except KeyboardInterrupt:
            print("Monitoring interrupted.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def start_monitoring_thread(self):
        monitoring_thread = threading.Thread(target=self.start_monitoring)
        monitoring_thread.start()

def process_files():
    global repo_dir
    
    dance_song = DanceSong(repo_dir)
    
    ready_event = threading.Event()
    dance_song_monitor = DanceSongMonitor(repo_dir, ready_event)
    dance_song_monitor.start_monitoring_thread()

    ready_event.wait()
    result = dance_song.process()
    add_message(result, is_user=False)
    # dance_song._make_directory_clickable(dance_song.repo_dir)
    
    # Destroy the instruction label after the files are ready
    instructions_label.destroy()

def get_response():
    global repo_dir
    repo_dir = input_entry.get()
    add_message(repo_dir, is_user=True)
    # Start processing files in a new thread
    processing_thread = threading.Thread(target=process_files)
    processing_thread.start()

# Bingo
def add_message(message, is_user=False):
    global chat_history
    if chat_history.winfo_exists():  # Check if the widget still exists
        if is_user:
            chat_history.insert(tk.END, "\n" + "You: " + message + "\n\n", 'user_message')
        else:
            chat_history.insert(tk.END, "\n" + "QQBot: " + message + "\n\n", 'chatbot_message')
    
    # Scroll to the end to display the latest message
    chat_history.see(tk.END)
    
    input_entry.delete(0, tk.END)


# Bingo
# Main logic for the Tkinter window
window = tk.Tk()
def main():
    global chat_history, input_entry, instructions_label
    global dir_open
    dir_open = False
    # Create the main window
    window.title("Dance Self Starter")

    chat_width=40
    chat_height=20

    # Create a scrolled text widget to display the chat history
    chat_history = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=chat_width, height=chat_height)
    chat_history.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    # Create an entry widget for user input
    input_entry = tk.Entry(window, width=40)
    input_entry.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    ## Display the initial chatbot message
    # add_message("Input the name of your dance ξ( ✿＞◡')", is_user=False)

    # Create a button to send user input
    send_button = tk.Button(window, text="Send", command=get_response)
    send_button.grid(row=1, column=1, padx=10, pady=10, sticky="e")

    # Define colors and styles for user and chatbot messages
    chat_history.tag_configure('chatbot_message', background='#363534')
    # Make the chat history area expand with the window
    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)

    # Bind the Enter key to the "Send" button's command
    window.bind('<Return>', lambda event=None: send_button.invoke())

    # Calculate the screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate the window position to center it on the screen
    x = (screen_width - window.winfo_reqwidth()) // 3
    y = 0

    # Set the window's position and size
    window.geometry(f"{chat_width * 10}x{chat_height * 20}+{x}+{y}")
    
    # Create a label for instructions
    instructions_label = tk.Label(window, text="")
    
    # Add initial hint message
    add_message("Enter your dance name to start ʕ•̀ o • ʔ", is_user=False)

    # Start the Tkinter main event loop
    window.mainloop()

if __name__ == "__main__":
    main()