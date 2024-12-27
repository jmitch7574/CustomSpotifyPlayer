import asyncio
import aiohttp
from functools import partial
import io
from dotenv import load_dotenv
import os

from spoti import SpotiPy
import tkinter as tk
from tkinter import ttk
import sv_ttk
from PIL import ImageTk, ImageEnhance, Image

current_song = ""
current_bg_path= ""
current_bg = None
current_cover_path = ""
current_cover = None

images = []

def truncate_string(text, max_length):
    """
    Truncates a string to the specified max_length and appends '...' if truncated.

    :param text: The original string
    :param max_length: The maximum number of characters before truncation
    :return: The truncated string
    """
    if len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text

async def refresh_keys():
    """
    Periodically refresh api keys
    """
    while True:
        await asyncio.sleep(3300000)
        try:
            api.RefreshApiKeys()
        except Exception as e:
            print(f"Error refreshing keys: {e}")

async def fetch_image(url):
    """
    Fetch an image asynchronously from a URL.

    :param url: URL of the image
    :return: BytesIO object containing image data
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return io.BytesIO(await response.read())
            else:
                raise Exception(f"Failed to fetch image: {response.status}")

def dim_image(image, factor):
    """
    Dim an image by reducing its brightness.

    :param image: PIL Image object
    :param factor: Brightness factor (0.0 is black, 1.0 is original brightness)
    :return: Dimmed ImageTk.PhotoImage object
    """
    enhancer = ImageEnhance.Brightness(image)
    dimmed_image = enhancer.enhance(factor)
    return ImageTk.PhotoImage(dimmed_image)

async def update_image(item, image, width, height, dim_factor):
    """
    Update a tkinter widget's image asynchronously.

    :param item: The tkinter widget to update
    :param image: The image to do
    :param width: Desired width
    :param height: Desired height
    :param dim_factor: Brightness adjustment factor
    """
    global track_info
    print(f"image_update: {item}")
    try:
        image = Image.open(image)
        resized_image = image.resize((width, height))
        dimmed_photo = dim_image(resized_image, dim_factor)
        track_info.itemconfig(item, image=dimmed_photo)
        images.append(dimmed_photo)
        
    except Exception as e:
        print(f"Error updating image: {e}")

async def update_cover_art(info):
    """
    Update cover art only if the image URL has changed asynchronously.

    :param info: Dictionary containing cover art info
    """
    global current_cover_path, current_cover, track_cover
    image_url = info.get('item', {}).get('album', {}).get('images', [{}])[0].get('url')
    if not image_url or current_cover_path == image_url:
        return
    else:
        current_cover = await fetch_image(image_url)
        await update_image(track_cover, current_cover, 150, 150, 1.0)
        current_cover_path = image_url

async def update_background(info):
    """
    Update background image only if the URL has changed asynchronously.

    :param info: Dictionary containing playback info
    """
    global current_bg_path, current_bg, track_background
    try:
        background_url = None
        context = info.get('context', {})
        context_type = context.get('type')

        if info.get('item').get('name') == current_song:
            return
        else:
            print(context_type)
            if context_type == 'playlist':
                playlist_info = api.GetPlayListInfo(context.get('href').split('/')[-1])
                if playlist_info:
                    background_url = playlist_info.get('images')[0].get('url')
                current_bg = await fetch_image(background_url)
            if context_type == 'album':
                album_info = api.GetAlbumInfo(context.get('href').split('/')[-1])
                if album_info:
                    background_url = album_info.get('images')[0].get('url')
                current_bg = await fetch_image(background_url)
            if context_type == 'artist':
                artist_info = api.GetArtistInfo(context.get('href').split('/')[-1])
                if artist_info:
                    background_url = artist_info.get('images')[0].get('url')
                current_bg = await fetch_image(background_url)
            await update_image(track_background, current_bg, 480, 245, 0.2)
            current_bg_path = background_url
    except Exception as e:
        print(f"Error updating background: {e}")

async def update_track_text(info):
    """
    
    """
    global track_info, track_name, track_artist, RESOLUTION_X

    if not info.get('item'):
        return
    
    song_name = info.get('item').get('name')
    song_artist = ""
    for artist in info.get('item').get('artists'):
        song_artist += artist.get('name') + "\n"

    track_info.itemconfig(track_name, text=truncate_string(song_name, RESOLUTION_X // 15))
    track_info.itemconfig(track_artist, text=song_artist)
    print(info.get('is_playing'))

async def check_pause_button(info):
    global shuffle_button, pause_button, repeat_button, ICON_CONTROL_PLAY, ICON_CONTROL_PAUSE, ICON_CONTROL_SHUFFLE_TRUE, ICON_CONTROL_SHUFFLE_FALSE, ICON_CONTROL_REPEAT_OFF, ICON_CONTROL_REPEAT_CONTEXT, ICON_CONTROL_REPEAT_TRACK

    new_play_icon = ICON_CONTROL_PAUSE if info.get('is_playing') else ICON_CONTROL_PLAY
    pause_button.configure(image=new_play_icon)
    pause_button.image = new_play_icon

    new_shuffle_icon = ICON_CONTROL_SHUFFLE_TRUE if info.get('shuffle_state') else ICON_CONTROL_SHUFFLE_FALSE
    shuffle_button.configure(image=new_shuffle_icon)
    shuffle_button.image = new_shuffle_icon

    new_repeat_icon = None
    state = info.get('repeat_state')
    if state == 'off':
        new_repeat_icon = ICON_CONTROL_REPEAT_OFF
    elif state == 'context':
        new_repeat_icon = ICON_CONTROL_REPEAT_CONTEXT
    else:
        new_repeat_icon = ICON_CONTROL_REPEAT_TRACK

    repeat_button.configure(image=new_repeat_icon)
    repeat_button.image = new_repeat_icon

async def update_menu():
    """
    Periodically update menu with playback info asynchronously.
    """
    global track_info, current_song
    while True:
        try:
            info = api.GetUserPlaybackInfo()
            if info:
                if (info.get('item').get('name') != current_song):
                    await asyncio.gather(update_cover_art(info), update_background(info), update_track_text(info))
                    current_song = info.get('item').get('name')
                await asyncio.gather(check_pause_button(info))
        except Exception as e:
            print(f"Error in update_menu: {e}")
        await asyncio.sleep(2)

def play_item(item_id):
    api.PlayItem(f"spotify:playlist:{item_id}")
    asyncio.run(update_menu())

def start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def main():
    global api, root, cover_art, track_info, track_cover, track_background, track_name, track_artist, pause_button, repeat_button, shuffle_button, ICON_CONTROL_PAUSE, ICON_CONTROL_PLAY, ICON_CONTROL_REPEAT_OFF, ICON_CONTROL_REPEAT_CONTEXT, ICON_CONTROL_REPEAT_TRACK, ICON_CONTROL_SHUFFLE_FALSE, ICON_CONTROL_SHUFFLE_TRUE, RESOLUTION_X, RESOLUTION_Y

    load_dotenv()

    CONTROL_ROW_HEIGHT = 75

    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")

    if not os.getenv("USER_REFRESH_KEY"):
        print("User not configured")
        return

    USER_REFRESH_KEY = os.getenv("USER_REFRESH_KEY")
    api = SpotiPy(CLIENT_ID, CLIENT_SECRET, USER_REFRESH_KEY)

    RESOLUTION_X = int(os.getenv("RESOLUTION_X"))
    RESOLUTION_Y = int(os.getenv("RESOLUTION_Y"))

    print(RESOLUTION_Y - CONTROL_ROW_HEIGHT)
    if not RESOLUTION_X or not RESOLUTION_Y:
        print("Resolution not configured")
        return

    root = tk.Tk()

    root.geometry(f"{RESOLUTION_X}x{RESOLUTION_Y}")
    root.minsize(RESOLUTION_X, RESOLUTION_Y)
    root.maxsize(RESOLUTION_X, RESOLUTION_Y)

    try:
        if os.getenv("FULLSCREEN"):
            root.attributes("-fullscreen", True)
    except:
        pass

    ICON_CONTROL_PAUSE = ImageTk.PhotoImage(Image.open("icons/control_pause.png").resize((50,50)))
    ICON_CONTROL_PLAY = ImageTk.PhotoImage(Image.open("icons/control_play.png").resize((50, 50)))
    ICON_CONTROL_PREVIOUS = ImageTk.PhotoImage(Image.open("icons/control_previous.png").resize((50, 50)))
    ICON_CONTROL_NEXT = ImageTk.PhotoImage(Image.open("icons/control_next.png").resize((50, 50)))
    ICON_CONTROL_REPEAT_OFF = ImageTk.PhotoImage(Image.open("icons/control_repeat_off.png").resize((50, 50)))
    ICON_CONTROL_REPEAT_CONTEXT = ImageTk.PhotoImage(Image.open("icons/control_repeat_context.png").resize((50, 50)))
    ICON_CONTROL_REPEAT_TRACK = ImageTk.PhotoImage(Image.open("icons/control_repeat_track.png").resize((50, 50)))
    ICON_CONTROL_SHUFFLE_FALSE = ImageTk.PhotoImage(Image.open("icons/control_shuffle_false.png").resize((50, 50)))
    ICON_CONTROL_SHUFFLE_TRUE = ImageTk.PhotoImage(Image.open("icons/control_shuffle_true.png").resize((50, 50)))

    menubar = tk.Menu(root, tearoff=False)

    playlist_menu = tk.Menu(menubar, tearoff=False)
    for playlist in api.GetUserPlaylists()['items']:
        playlist_id = playlist.get('id')
        playlist_menu.add_command(
            label=playlist.get('name'),
            command=partial(api.PlayItem, f"spotify:playlist:{playlist_id}")
        )
    menubar.add_cascade(label="Playlists", menu=playlist_menu)

    album_menu = tk.Menu(menubar, tearoff=False)
    for album in api.GetUserAlbums()['items']:
        album_id = album.get('album').get('id')
        album_menu.add_command(
            label=album.get('album').get('name'),
            command=partial(api.PlayItem, f"spotify:album:{album_id}")
        )
    menubar.add_cascade(label="Albums", menu=album_menu)

    artist_menu = tk.Menu(menubar, tearoff=False)
    for artist in api.GetUserArtists()['items']:
        artist_id = artist.get('uri').split(':')[-1]
        artist_menu.add_command(
            label=artist.get('name'),
            command=partial(api.PlayItem, f"spotify:artist:{artist_id}")
        )
    menubar.add_cascade(label="Artists", menu=artist_menu)

    track_info = tk.Canvas(root, width=RESOLUTION_X, height=RESOLUTION_Y-CONTROL_ROW_HEIGHT, bg="black")
    track_info.place(x=0, y=0, relwidth=1, height=RESOLUTION_Y-CONTROL_ROW_HEIGHT)

    track_section_height = 150
    space_available = (RESOLUTION_Y - CONTROL_ROW_HEIGHT)
    margin = (space_available - track_section_height) / 2

    print(margin)

    track_background = track_info.create_image(0, 0, image=None, anchor='nw')
    track_cover = track_info.create_image(25, margin, image=None, anchor='nw')
    track_name = track_info.create_text(190, margin, anchor=tk.NW, text='SONG_NAME', fill="white", font=("Arial", 15, "bold")) # Font and style
    track_artist = track_info.create_text(190, margin + 25, anchor=tk.NW, text='SONG_ARTIST', fill="white", font=("Arial", 10)) # Font and style

    print(f"track_bg: {track_background}")
    print(f"track_cover: {track_cover}")
    print(f"track_name: {track_name}")
    print(f"track_artist: {track_artist}")

    controls = ttk.Frame(root, height=CONTROL_ROW_HEIGHT)
    controls.place(x=0, y=RESOLUTION_Y-CONTROL_ROW_HEIGHT-20, relwidth=1, height=CONTROL_ROW_HEIGHT)

    shuffle_button = ttk.Button(controls, image=ICON_CONTROL_SHUFFLE_FALSE, command=api.toggle_shuffle)
    shuffle_button.grid(row=0, column=1, sticky='nsew')
    previous_button = ttk.Button(controls, image=ICON_CONTROL_PREVIOUS, command= api.PreviousButtonPressed)
    previous_button.grid(row=0, column=2, sticky='nsew')
    pause_button = ttk.Button(controls, image=ICON_CONTROL_PAUSE, command=api.pause_button_pressed)
    pause_button.grid(row=0, column=3, sticky='nsew')
    next_button = ttk.Button(controls, image=ICON_CONTROL_NEXT, command=api.SkipToNextSong)
    next_button.grid(row=0, column=4, sticky='nsew')
    repeat_button = ttk.Button(controls, image=ICON_CONTROL_REPEAT_OFF, command=api.toggle_repeat)
    repeat_button.grid(row=0, column=5, sticky='nsew')
    
    controls.grid_columnconfigure(1, weight=1)
    controls.grid_columnconfigure(2, weight=1)
    controls.grid_columnconfigure(3, weight=1)
    controls.grid_columnconfigure(4, weight=1)
    controls.grid_columnconfigure(5, weight=1)

    controls.grid_rowconfigure(0, weight=1)

    sv_ttk.set_theme("dark")

    async_loop = asyncio.new_event_loop()
    asyncio.run_coroutine_threadsafe(update_menu(), async_loop)
    asyncio.run_coroutine_threadsafe(refresh_keys(), async_loop)

    root.config(menu=menubar, bg="black")

    # Start asyncio loop in a separate thread
    import threading
    threading.Thread(target=start_async_loop, args=(async_loop,), daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    main()