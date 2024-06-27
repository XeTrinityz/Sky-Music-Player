import sys
import json
import time
import threading
import keyboard
import os

# Dictionary mapping placeholder keys to actual keys
key_mapping = {
    "1Key0": "Y",
    "1Key1": "U",
    "1Key2": "I",
    "1Key3": "O",
    "1Key4": "P",
    "1Key5": "H",
    "1Key6": "J",
    "1Key7": "K",
    "1Key8": "L",
    "1Key9": ";",
    "1Key10": "N",
    "1Key11": "M",
    "1Key12": ",",
    "1Key13": ".",
    "1Key14": "/",
    "Key0": "Y",
    "Key1": "U",
    "Key2": "I",
    "Key3": "O",
    "Key4": "P",
    "Key5": "H",
    "Key6": "J",
    "Key7": "K",
    "Key8": "L",
    "Key9": ";",
    "Key10": "N",
    "Key11": "M",
    "Key12": ",",
    "Key13": ".",
    "Key14": "/",
}

# Function to calculate delay based on BPM
def bpm_to_delay(bpm):
    return 60 / bpm

# Function to preprocess song notes and group them by time
def preprocess_notes(song_data):
    notes_by_time = {}
    for note in song_data[0]['songNotes']:
        time_key = note['time']
        if time_key not in notes_by_time:
            notes_by_time[time_key] = []
        notes_by_time[time_key].append(note['key'])
    return notes_by_time

# Function to simulate key press based on the preprocessed notes
def play_song(song_data, bpm):
    global playing, paused, current_time_key
    delay = bpm_to_delay(bpm)
    notes_by_time = preprocess_notes(song_data)
    start_time = time.time()

    time_keys = sorted(notes_by_time.keys())
    while playing and current_time_key < len(time_keys):
        if paused:
            time.sleep(0.1)
            continue
        
        time_key = time_keys[current_time_key]
        notes = notes_by_time[time_key]
        
        press_time = start_time + time_key / 1000
        wait_time = press_time - time.time()
        if wait_time > 0:
            time.sleep(min(wait_time, 0.01))
            continue
        
        for note in notes:
            key = key_mapping.get(note, None)
            if key:
                keyboard.press(key)
        time.sleep(delay)
        for note in notes:
            key = key_mapping.get(note, None)
            if key:
                keyboard.release(key)
        
        current_time_key += 1
    playing = False

# Function to toggle song playing
def toggle_song(hotkey):
    global playing, current_bpm, current_time_key
    if hotkey in song_threads and song_threads[hotkey].is_alive():
        playing = False
        song_threads[hotkey].join()
        del song_threads[hotkey]
        display_songs()
        print(f"Stopped playing song #{hotkey}.")
        sys.stdout.flush()
    else:
        stop_all_songs()
        if hotkey in song_hotkeys:
            playing = True
            current_time_key = 0
            song_data_path = song_hotkeys[hotkey]
            try:
                with open(song_data_path) as file:
                    song_data = json.load(file)
            except FileNotFoundError:
                print(f"Error: File not found at path: {song_data_path}")
                return
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON format in file: {song_data_path}")
                return
            thread = threading.Thread(target=play_song, args=(song_data, current_bpm))
            song_threads[hotkey] = thread
            thread.start()
            display_songs()
            print(f"Playing song #{hotkey} at {current_bpm} BPM.")
            sys.stdout.flush()

# Function to stop all playing songs
def stop_all_songs():
    global playing
    playing = False
    for thread in song_threads.values():
        if thread.is_alive():
            thread.join()
    song_threads.clear()
    display_songs()
    print("All songs stopped.")
    sys.stdout.flush()

# Function to display the song list
def display_songs():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Sky Music Player by XeTrinityz \n------------------------------")
    print("\nPlay Song: 1-9 | Stop Song: Backspace | Cycle Songs: -/=\n")
    print("Songs")
    print("--------------------------------------------------")
    for i, song_path in enumerate(next_songs, start=1):
        hotkey = str(i)
        song_hotkeys[hotkey] = song_path
        song_data = json.load(open(song_path))
        default_bpm = song_data[0].get('bpm', 'Unknown')
        print(f"Hotkey {hotkey}: {os.path.basename(song_path)} (Default BPM: {default_bpm})")
    print("--------------------------------------------------")

# Function to cycle through available songs forward
def cycle_songs_forward():
    global current_song_index, next_songs
    next_songs = music_sheets[current_song_index:current_song_index + 9]
    if len(next_songs) < 9:
        next_songs += music_sheets[:9 - len(next_songs)]
    current_song_index = (current_song_index + 9) % len(music_sheets)
    display_songs()

# Function to cycle through available songs backward
def cycle_songs_backward():
    global current_song_index, next_songs
    current_song_index = (current_song_index - 9) % len(music_sheets)
    next_songs = music_sheets[current_song_index:current_song_index + 9]
    if len(next_songs) < 9:
        next_songs = music_sheets[-(9 - len(next_songs)):] + next_songs
    display_songs()

# Function to decrease BPM by 10
def decrease_bpm():
    global current_bpm
    current_bpm = max(10, current_bpm - 10)
    display_songs()
    print(f"BPM decreased to {current_bpm}.")
    sys.stdout.flush()

# Function to increase BPM by 10
def increase_bpm():
    global current_bpm
    current_bpm += 10
    display_songs()
    print(f"BPM increased to {current_bpm}.")
    sys.stdout.flush()

# Scan the directory for music sheet files
music_sheet_dir = "./Music Sheets/"
music_sheets = [os.path.join(music_sheet_dir, file) for file in os.listdir(music_sheet_dir) if file.endswith('.json')]

# Initialize variables
song_hotkeys = {}
next_songs = []
song_threads = {}
playing = False
paused = False
current_song_index = 0
current_bpm = 530

# Create song hotkeys for the first 9 songs
next_songs = music_sheets[:9]
display_songs()

# Register the hotkeys
for hotkey in song_hotkeys.keys():
    keyboard.add_hotkey(hotkey, toggle_song, args=(hotkey,))

# Register the hotkey to stop all songs
keyboard.add_hotkey('backspace', stop_all_songs)

# Register the hotkeys to cycle through songs
keyboard.add_hotkey('-', cycle_songs_backward)
keyboard.add_hotkey('=', cycle_songs_forward)

# Register the hotkey to decrease BPM
keyboard.add_hotkey('[', decrease_bpm)

# Register the hotkey to increase BPM
keyboard.add_hotkey(']', increase_bpm)

# Keep the program running
keyboard.wait('F5')