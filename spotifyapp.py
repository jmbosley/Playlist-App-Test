# Author: Thomas Southards

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import csv
import os

import zmq

context = zmq.Context()
#  Socket to talk to server
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:8000")

class PlaylistApp:
    def __init__(self, master):
        self.master = master
        master.title("Playlist Manager")
        master.geometry("700x500")
        master.configure(background="#f0f0f0")
        
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 12))
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), foreground="#333")
        style.configure("TButton", font=("Helvetica", 10), padding=5)
        
        # File for storing data
        self.playlist_file = "playlists.csv"
        # Dictionary mapping playlist names to a list of songs
        self.playlists = {}
        self.load_data()
        
        # Create a container to hold two frames: the Home Page and the Main App
        self.container = ttk.Frame(master)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Configure the container's grid so that its children expand to fill the space
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Create the two frames
        self.home_frame = ttk.Frame(self.container)
        self.main_frame = ttk.Frame(self.container)
        
        # Stack the frames on top of each other
        for frame in (self.home_frame, self.main_frame):
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Build the Home Page UI and the Main UI
        self.build_home_page()
        self.build_main_ui()
        
        # Start with the Home Page visible
        self.show_frame(self.home_frame)
    
    def show_frame(self, frame):
        """Raises the given frame to the top."""
        frame.tkraise()
    
    def build_home_page(self):
        """Builds the UI for the home page."""
        # Music icon (using a Unicode character)
        music_icon_label = ttk.Label(self.home_frame, text="🎵", font=("Helvetica", 64))
        music_icon_label.pack(pady=20)
        
        # Welcome title
        title_label = ttk.Label(self.home_frame, text="Welcome to Playlist Manager", style="Header.TLabel")
        title_label.pack(pady=10)
        
        # Help button shows a short summary and Q&A
        help_button = ttk.Button(self.home_frame, text="Help", command=self.show_help)
        help_button.pack(pady=5)
        
        # Button to enter the main playlist manager UI
        enter_button = ttk.Button(self.home_frame, text="Enter App", command=lambda: self.show_frame(self.main_frame))
        enter_button.pack(pady=20)
    
    def show_help(self):
        """Displays a pop-up with a brief explanation and Q&A."""
        help_text = (
            "Welcome to the Playlist Manager App!\n\n"
            "How it works:\n"
            " - Create playlists and add songs to them.\n"
            " - Select a playlist to view its songs.\n"
            " - Remove songs from a playlist if needed.\n\n"
            "Q&A:\n"
            "Q: How do I create a playlist?\n"
            "A: Click the 'Create Playlist' button.\n\n"
            "Q: How do I add a song?\n"
            "A: Select a playlist and click the 'Add Song' button.\n\n"
            "Q: How do I remove a song?\n"
            "A: Select the song and click 'Remove Song'."
        )
        messagebox.showinfo("Help", help_text)
    
    def build_main_ui(self):
        """Builds the main playlist manager UI inside the main_frame."""
        # Header Section
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        header_label = ttk.Label(header_frame, text="Playlist Manager", style="Header.TLabel")
        header_label.pack()
        
        # Content Section divided into left (playlists) and right (songs) panels
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left Panel: Playlists with scrollbar
        self.left_frame = ttk.Frame(content_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        playlist_label = ttk.Label(self.left_frame, text="Playlists")
        playlist_label.pack(anchor=tk.W)
        
        playlist_box_frame = ttk.Frame(self.left_frame)
        playlist_box_frame.pack(fill=tk.BOTH, expand=True)
        # Set exportselection to False so the selection isn't lost when focus changes
        self.playlist_listbox = tk.Listbox(playlist_box_frame, bg="white", font=("Helvetica", 10),
                                           bd=2, relief="sunken", exportselection=False)
        self.playlist_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        playlist_scroll = ttk.Scrollbar(playlist_box_frame, orient=tk.VERTICAL, command=self.playlist_listbox.yview)
        playlist_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.playlist_listbox.config(yscrollcommand=playlist_scroll.set)
        self.playlist_listbox.bind("<<ListboxSelect>>", self.on_playlist_select)
        
        # Right Panel: Songs with scrollbar
        self.right_frame = ttk.Frame(content_frame)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        song_label = ttk.Label(self.right_frame, text="Songs")
        song_label.pack(anchor=tk.W)
        
        song_box_frame = ttk.Frame(self.right_frame)
        song_box_frame.pack(fill=tk.BOTH, expand=True)
        self.song_listbox = tk.Listbox(song_box_frame, bg="white", font=("Helvetica", 10), bd=2, relief="sunken")
        self.song_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        song_scroll = ttk.Scrollbar(song_box_frame, orient=tk.VERTICAL, command=self.song_listbox.yview)
        song_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.song_listbox.config(yscrollcommand=song_scroll.set)
        
        # Bottom Section: Control Buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=10)
        ttk.Button(self.button_frame, text="Create Playlist", command=self.create_playlist).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Add Song", command=self.add_song).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Replace Song", command=self.replace_song).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Remove Song", command=self.remove_song).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Delete Playlist", command=self.delete_playlist).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Go Back", command=lambda: self.show_frame(self.home_frame)).pack(side=tk.LEFT, padx=5)
        
        self.update_playlist_listbox()
    
    def load_data(self):
        """Loads playlists and songs from the CSV file into the dictionary."""
        if not os.path.exists(self.playlist_file):
            return
        with open(self.playlist_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                playlist = row["playlist"]
                song = row["song"]
                if playlist not in self.playlists:
                    self.playlists[playlist] = []
                if song and song not in self.playlists[playlist]:
                    self.playlists[playlist].append(song)
    
    def save_data(self):
        """Saves the current playlists and songs to the CSV file."""
        with open(self.playlist_file, "w", newline='', encoding='utf-8') as csvfile:
            fieldnames = ["playlist", "song"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for playlist, songs in self.playlists.items():
                if songs:
                    for song in songs:
                        writer.writerow({"playlist": playlist, "song": song})
                else:
                    writer.writerow({"playlist": playlist, "song": ""})
    
    def update_playlist_listbox(self):
        """Refreshes the playlist listbox."""
        self.playlist_listbox.delete(0, tk.END)
        for playlist in sorted(self.playlists.keys()):
            self.playlist_listbox.insert(tk.END, playlist)
    
    def update_song_listbox(self, playlist):
        """Refreshes the song listbox for a given playlist."""
        self.song_listbox.delete(0, tk.END)
        for song in self.playlists.get(playlist, []):
            self.song_listbox.insert(tk.END, song)
    
    def on_playlist_select(self, event):
        """Called when the user selects a playlist; updates the song listbox."""
        selection = self.playlist_listbox.curselection()
        if selection:
            index = selection[0]
            playlist = self.playlist_listbox.get(index)
            self.update_song_listbox(playlist)
        else:
            self.song_listbox.delete(0, tk.END)
    
    def create_playlist(self):
        """Prompts the user for a playlist name and creates a new empty playlist."""
        playlist_name = simpledialog.askstring("Create Playlist", "Enter playlist name:")
        if playlist_name:
            if playlist_name in self.playlists:
                messagebox.showerror("Error", "Playlist already exists!")
            else:
                self.playlists[playlist_name] = []
                self.update_playlist_listbox()
                self.save_data()
    
    def add_song(self):
        """Adds a song to the currently selected playlist."""
        selection = self.playlist_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a playlist first!")
            return
        playlist = self.playlist_listbox.get(selection[0])
        song_name = simpledialog.askstring("Add Song", "Enter song name:")
        if song_name:
            if song_name in self.playlists[playlist]:
                messagebox.showerror("Error", "Song already exists in the playlist!")
            else:
                self.playlists[playlist].append(song_name)
                self.update_song_listbox(playlist)
                self.save_data()
    
    def remove_song(self):
        """Removes the selected song from the selected playlist."""
        pl_selection = self.playlist_listbox.curselection()
        if not pl_selection:
            messagebox.showerror("Error", "Please select a playlist first!")
            return
        playlist = self.playlist_listbox.get(pl_selection[0])
        song_selection = self.song_listbox.curselection()
        if not song_selection:
            messagebox.showerror("Error", "Please select a song to remove!")
            return
        song = self.song_listbox.get(song_selection[0])
        if messagebox.askyesno("Confirm", f"Remove song '{song}' from playlist '{playlist}'?"):
            self.playlists[playlist].remove(song)
            self.update_song_listbox(playlist)
            self.save_data()
    
    def delete_playlist(self):
        """Deletes the selected playlist (and its songs) after confirmation."""
        selection = self.playlist_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a playlist to delete!")
            return
        playlist = self.playlist_listbox.get(selection[0])
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete the playlist '{playlist}'?"):
            del self.playlists[playlist]
            self.update_playlist_listbox()
            self.song_listbox.delete(0, tk.END)
            self.save_data()

    def replace_song(self):
        """
        Calls the replaceSongInPlaylist Microservice
        :return:
        """
        pl_selection = self.playlist_listbox.curselection()
        song_selection = self.song_listbox.curselection()

        if not pl_selection:
            messagebox.showerror("Error", "Please select a playlist first!")
            return
        if not song_selection:
            messagebox.showerror("Error", "Please select a song to replace!")
            return

        playlist = self.playlist_listbox.get(pl_selection[0])
        songA = self.song_listbox.get(song_selection[0])

        songB = simpledialog.askstring("New Song", "Enter song name:")
        if songB:
            if songB in self.playlists[playlist]:
                messagebox.showerror("Error", "Song already exists in the playlist!")
            else:
                message = (playlist +":"+ songA +":"+ songB).encode("utf-8")
                socket.send(message)

                #  Get the reply.
                message = socket.recv()
        # Reload Display
        self.playlists = {}
        self.load_data()


if __name__ == "__main__":
    root = tk.Tk()
    app = PlaylistApp(root)
    root.mainloop()
