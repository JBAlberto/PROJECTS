import tkinter as tk
from tkinter import messagebox
import pygame
import os
import threading

# Initialize pygame mixer
pygame.mixer.init()

# Function to load and play music
def play_music(file, loop=False, start_pos=0):
    loops = -1 if loop else 0  # Loops the Songh if loop is True, Else play once
    pygame.mixer.music.load(file)
    pygame.mixer.music.play(loops=loops, start=start_pos)

# Function to pause the music
def pause_music():
    pygame.mixer.music.pause()  # Pauses the music

# Function to stop the music
def stop_music():
    pygame.mixer.music.stop()  # Stops the music completely
    pygame.mixer.music.load("")  # Optionally clear the current music

# Function to list all audio files in a directory and return them in a hash table (dictionary)
def list_audio_files(directory):
    return {filename.lower(): os.path.join(directory, filename) 
            for filename in os.listdir(directory) 
            if filename.endswith(('.wav', '.mp3'))}

# Node class for the circular linked list
class SongNode:
    def __init__(self, song_name, song_path):
        self.song_name = song_name
        self.song_path = song_path
        self.next = None

# Circular Linked List class
class CircularLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def add_song(self, song_name, song_path):
        new_node = SongNode(song_name, song_path)
        if not self.head:
            self.head = new_node
            self.tail = new_node
            self.tail.next = self.head
        else:
            self.tail.next = new_node
            self.tail = new_node
            self.tail.next = self.head

    def get_next_song(self, current_node):
        return current_node.next

    def get_previous_song(self, current_node):
        # To find the previous song, we need to traverse the list from head to current
        temp = self.head
        while temp.next != current_node:
            temp = temp.next
        return temp

    def get_first_song(self):
        return self.head

    def is_empty(self):
        return self.head is None

class MusicPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Music")
        root.iconbitmap('logo.ico')
        
        # Set the directory where music files are stored
        self.music_directory = './MUSIC'  # Current directory
        self.audio_files = list_audio_files(self.music_directory)

        if not self.audio_files:
            messagebox.showerror("Error", "No audio files found in the directory.")
            self.root.quit()
            return

        self.loop_music = False
        self.current_song = None
        self.is_playing = False  # Track the play state
        self.song_list = CircularLinkedList()
        self.paused_position = 0  # Variable to store the position when paused

        # Add songs to the circular linked list
        for song, path in self.audio_files.items():
            self.song_list.add_song(song, path)

        # GUI components
        self.play_image = tk.PhotoImage(file="play.png")  # Load play image
        self.pause_image = tk.PhotoImage(file="pause.png")  # Load pause image
        self.next_image = tk.PhotoImage(file="next.png")
        self.prev_image = tk.PhotoImage(file="prev.png")

        self.search_entry = tk.Entry(self.root, font=("Arial", 12))
        self.search_entry.grid(row=0, column=0, padx=20, pady=20, columnspan=3)

        self.search_button = tk.Button(self.root, text="Search", command=self.search, font=("Arial", 12))
        self.search_button.grid(row=0, column=3, padx=10, pady=20)

        self.song_listbox = tk.Listbox(self.root, height=10, width=40, selectmode=tk.SINGLE, font=("Arial", 12))
        self.song_listbox.grid(row=1, column=0, padx=20, pady=20, rowspan=1, columnspan=5)
        self.load_song_list()

        self.current_song_label = tk.Label(self.root, text="No song playing", font=("Arial", 10), anchor='w')
        self.current_song_label.grid(row=4, column=0, columnspan=5, padx=20, pady=20)

        self.prev_button = tk.Button(self.root, image=self.prev_image, command=self.prev_song)
        self.prev_button.grid(row=5, column=1, padx=0, pady=0)

        self.play_pause_button = tk.Button(self.root, image=self.play_image, command=self.toggle_play_pause)
        self.play_pause_button.grid(row=5, column=2, padx=0, pady=0)

        self.next_button = tk.Button(self.root, image=self.next_image, command=self.next_song)
        self.next_button.grid(row=5, column=3, padx=0, pady=0, columnspan=1)

        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop, font=("Arial", 12))
        self.stop_button.grid(row=5, column=4, padx=0, pady=0)

        # Bind the Listbox click event to the function that plays the song
        self.song_listbox.bind("<ButtonRelease-1>", self.on_song_click)

        # Call update function to check the music status
        self.root.after(100, self.update_music_status)

    def play_music_thread(self, song_path, loop=False, start_pos=0):
        # Run play_music in a separate thread to avoid blocking Tkinter
        threading.Thread(target=play_music, args=(song_path, loop, start_pos)).start()

    def toggle_play_pause(self):
        if self.current_song is None:
            messagebox.showwarning("No Song Selected", "Please select a song first!")
            return  # Prevent play if no song is selected

        if self.is_playing:
            # Pause the music and save the current position
            self.paused_position = pygame.mixer.music.get_pos() / 1000  # Convert milliseconds to seconds
            pause_music()  # Pause the music
            self.play_pause_button.config(image=self.play_image)  # Change button image to play
        else:
            # If music is paused, unpause it from the saved position
            if pygame.mixer.music.get_busy():  # If music is already playing
                pygame.mixer.music.unpause()  # Unpause the music
            else:
                # Start the music from the saved position
                self.play_music_thread(self.current_song.song_path, self.loop_music, self.paused_position)
                
            self.play_pause_button.config(image=self.pause_image)  # Change button image to pause

        self.is_playing = not self.is_playing  # Toggle play state

    def stop(self):
        if self.current_song:
            stop_music()
            self.is_playing = False  # Reset play state
            self.play_pause_button.config(image=self.play_image)  # Reset button to play
            self.update_current_song_label("No song playing")  # Reset label
        else:
            messagebox.showwarning("No Song Selected", "Please select a song first!")

    def next_song(self):
        if self.current_song:
            next_song_node = self.song_list.get_next_song(self.current_song)
            self.current_song = next_song_node
            self.play_music_thread(self.current_song.song_path, self.loop_music)
            self.update_current_song_label(self.current_song.song_name)
        else:
            messagebox.showwarning("No Song Selected", "Please select a song first!")

    def prev_song(self):
        if self.current_song:
            prev_song_node = self.song_list.get_previous_song(self.current_song)
            self.current_song = prev_song_node
            self.play_music_thread(self.current_song.song_path, self.loop_music)
            self.update_current_song_label(self.current_song.song_name)
        else:
            messagebox.showwarning("No Song Selected", "Please select a song first!")

    def search(self):
        search_query = self.search_entry.get().strip().lower()

        # Using the hash table (dictionary) to search for the song
        matching_songs = {song: path for song, path in self.audio_files.items() if search_query in song}

        if matching_songs:
            self.song_listbox.delete(0, tk.END)
            for song in matching_songs:
                self.song_listbox.insert(tk.END, song)
        else:
            messagebox.showinfo("No matches", "No matching songs found.")

    def on_song_click(self, event):
        selected_song_idx = self.song_listbox.curselection()
        if selected_song_idx:
            selected_song = self.song_listbox.get(selected_song_idx)
            # Find the song node
            current_node = self.song_list.get_first_song()
            while current_node:
                if current_node.song_name == selected_song:
                    self.current_song = current_node
                    self.play_music_thread(self.current_song.song_path, self.loop_music)
                    self.is_playing = True
                    self.play_pause_button.config(image=self.pause_image)  # Change button to "Pause"
                    self.update_current_song_label(self.current_song.song_name)  # Update song label
                    break
                current_node = current_node.next
                if current_node == self.song_list.get_first_song():
                    break

            self.load_song_list()

    def load_song_list(self):
        self.song_listbox.delete(0, tk.END)
        current_node = self.song_list.get_first_song()
        while current_node:
            self.song_listbox.insert(tk.END, current_node.song_name)
            current_node = current_node.next
            if current_node == self.song_list.get_first_song():
                break

    def update_current_song_label(self, song_name):
        self.current_song_label.config(text=f"Playing: {song_name}")

    def update_music_status(self):
        if not pygame.mixer.music.get_busy() and self.is_playing:
            # Music has finished playing, stop playback
            self.is_playing = False
            self.play_pause_button.config(image=self.play_image)  # Reset button image to play
            self.update_current_song_label("No song playing")
        
        # Call this function again after 100 ms
        self.root.after(100, self.update_music_status)

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayerApp(root)
    root.mainloop()
