from nicegui import APIRouter, Client, app, ui
from nicegui.events import KeyEventArguments
from fastapi.responses import FileResponse
import os

# Create a router that serves media files
router = APIRouter(prefix="/music")

# Convert float timestamps to more readable m:s timestamps
def float_to_timestamp(val: float) -> str:
    minutes, seconds = divmod(int(val), 60)
    return f"{minutes}:{seconds:02d}"

# Load and run JavaScript files for audio and visuals
def load_js() -> None:
    audio_js = open("audio.js", "r").read()
    visuals_js = open("visuals.js", "r").read()
    ui.run_javascript(audio_js)
    ui.run_javascript(visuals_js)

# Get the current time of the audio element
async def get_audio_current_time() -> float:
    try:
        time = await ui.run_javascript("""(() => { return document.getElementsByClassName("audio")[0].currentTime })()""")
    except:
        time = 0
    return float(time)

# Get the duration of the audio element
async def get_audio_duration() -> float:
    duration = await ui.run_javascript("""(() => { return document.getElementsByClassName("audio")[0].duration })()""")
    return float(duration) if duration else 100

# Check if the audio element is paused
async def audio_paused() -> bool:
    paused = await ui.run_javascript("""(() => { return document.getElementsByClassName("audio")[0].paused })()""")
    return paused

# Set the volume of the audio element
async def set_audio_volume(vol: float) -> None:
    await ui.run_javascript("""(() => { return document.getElementsByClassName("audio")[0].volume = """ + str(vol) + """; })()""")

# Define the route for the index page
@ui.page("/")
async def index(client: Client) -> None:
    # Add a script tag to load the Wave.js library
    ui.add_head_html("""<script src="https://cdn.jsdelivr.net/gh/foobar404/wave.js/dist/bundle.js"></script>""")
    
    # Define a function to update the slider and time label
    async def update_slider() -> None:
        try:
            current_time = await get_audio_current_time()
            slider.value = current_time
            time_label.text = float_to_timestamp(current_time)
            
            # Update slider max value if the duration has changed
            if (duration := await get_audio_duration()) != slider._props["max"]:
                slider._props["max"] = duration
                slider.update()
        except Exception as e:
            print(repr(e))
            pass
    
    # Define functions to seek backward and forward in the audio
    async def play_backwards() -> None:
        audio.seek((await get_audio_current_time()) - 10)
    
    async def play_forward() -> None:
        audio.seek((await get_audio_current_time()) + 10)
    
    # Define functions to seek to the start and end of the audio
    async def seek_to_end() -> None:
        audio.seek(await get_audio_duration())
    
    async def seek_to_start() -> None:
        audio.seek(0)
    
    # Define a function to toggle play/pause of the audio
    async def toggle_audio() -> None:
        paused = await audio_paused()
        if paused:
            audio.play()
            btn_play_pause._props["icon"] = "pause"
        else:
            audio.pause()
            btn_play_pause._props["icon"] = "play_arrow"
        btn_play_pause.update()
    
    # Define a function to change the volume
    async def change_volume() -> None:
        await set_audio_volume(volume.value / 100)
    
    # Define a function to handle audio playback end
    def audio_ended() -> None:
        if not app.storage.user["repeat"]:
            ui.notify("Playback has ended with no repeat enabled...")
            btn_play_pause._props["icon"] = "play_arrow"
            btn_play_pause.update()
        else:
            ui.notify("Playback has ended with repeat enabled...")
            audio.seek(0)
            audio.play()
    
    # Define a function to toggle repeat mode
    def toggle_repeat() -> None:
        if "repeat" in app.storage.user:
            app.storage.user["repeat"] = not app.storage.user["repeat"]
        else:
            app.storage.user["repeat"] = False
        
        btn_repeat._props["color"] = "red" if app.storage.user["repeat"] else "primary"
        btn_repeat.update()
    
    # Wait for the client to connect
    await client.connected()

    # Create the UI layout
    with ui.column().classes("absolute-center items-center"):
        with ui.card().classes("content-card"):
            # Header and image
            ui.label("NiceGUI Audio Player (press h/? for help)")
            ui.image(source="https://i.ytimg.com/vi/7S85apx0_EI/maxresdefault.jpg")

            # Audio player and controls
            audio = ui.audio(src="/music/test.mp3", controls=False).classes("audio")
            slider = ui.slider(min=0, max=await get_audio_duration(), value=0)

            # Time, volume, and duration row
            with ui.row().classes("w-full"):
                time_label = ui.label(text=float_to_timestamp(await get_audio_current_time())).classes("mb-auto mt-auto")
                ui.icon(name="volume_down", size="large").classes("mt-auto mb-auto ml-auto")
                volume = ui.slider(min=0, max=100, value=100, on_change=change_volume).classes("w-6/12 ml-auto mr-auto mt-auto mb-auto")
                ui.icon(name="volume_up", size="large").classes("mt-auto mb-auto mr-auto")
                ui.label(text=float_to_timestamp(await get_audio_duration())).classes("ml-auto mt-auto mb-auto")

            # Playback control row
            with ui.row().classes("w-full justify-center"):
                btn_prev = ui.button(icon="first_page", on_click=seek_to_start).props("flat")
                btn_back = ui.button(icon="chevron_left", on_click=play_backwards).props("flat")
                btn_play_pause = ui.button(icon="play_arrow", on_click=toggle_audio).classes("play-pause").props("flat")
                btn_forw = ui.button(icon="chevron_right", on_click=play_forward).props("flat")
                btn_next = ui.button(icon="last_page", on_click=seek_to_end).props("flat")
                btn_repeat = ui.button(icon="repeat", on_click=toggle_repeat, color="red" if app.storage.user.get("repeat", False) else "primary").props("flat")
                

            # Song information
            ui.markdown(content="""Song: T & Sugah - For You (ft. Snnr) [NCS Release]<br>
                Music provided by NoCopyrightSounds<br>
                Free Download/Stream: -<br>
                Watch: -<br>
                Thumbnail: YouTube
            """).classes("italic")

            # Animation canvas
            ui.element("canvas").classes("animation-canvas position-absolute w-1400 absolute-center")

            # Event handlers for audio player
            audio.on("ended", handler=audio_ended)
            audio.on("timeupdate", handler=update_slider)
            
            
            # Define a function to handle keyboard events
            async def handle_key(e: KeyEventArguments) -> None:
                if not e.action.keyup:
                    return
                
                # Handle different keyboard events
                if e.key == " ":
                    await toggle_audio()
                elif e.key == "p":
                    await seek_to_start()
                elif e.key == "n":
                    await seek_to_end()
                elif e.key == "h" or e.key == "?":
                    help_dialog.open()
                elif e.key == "r":
                    toggle_repeat()
                elif e.key == "m":
                    # Toggle volume between 0 and 100
                    volume.value = 0 if volume.value != 0 else 100
                    await change_volume()
                elif e.key.arrow_left:
                    await play_backwards()
                elif e.key.arrow_right:
                    await play_forward()
                elif e.key.arrow_down:
                    # Decrease volume by 10, but not below 0
                    volume.value = volume.value - 10 if volume.value >= 10 else 0
                    await change_volume()
                elif e.key.arrow_up:
                    # Increase volume by 10, but not above 100
                    volume.value = volume.value + 10 if volume.value <= 90 else 100
                    await change_volume()

            # Create a keyboard element with the defined event handler
            keyboard = ui.keyboard(on_key=handle_key)

            # Create a dialog for displaying help information
            with ui.dialog() as help_dialog, ui.card():
                ui.label("Help").classes("font-bold text-2xl")
                ui.label("Capturing of Media Keys is enabled. Press any of these keys on your keyboard to interact with the audio player: ⏯︎ ⏮ ⏭")
                ui.label("Keystrokes for interacting with the audio player are also enabled. Press any of the following keys: p, n, m, r, ←, →")
                ui.markdown("""
                            - p/⏮: jump back to start / previous song
                            - n/⏭: jump to the end / next song
                            - m: toggle mute (does not store previous volume)
                            - r: toggle repeat
                            - space/⏯︎: toggle play
                            - ←/→: seek 10s forward or backward
                            - ↓/↑: increase/decrease volume
                            - h/?: show this help dialog
                """)
                ui.button("Close", on_click=help_dialog.close)

    # Load JavaScript files
    load_js()


# Define a route to serve audio files
@router.page("/{song}")
def get_song(song: str):
    # Return the requested audio file as a FileResponse
    return FileResponse(f"./music/{song}", media_type="audio/mp3")


if __name__ in {"__main__", "__mp_main__"}:
    # Include the router in the app
    app.include_router(router)

    # Run the NiceGUI app with dark mode
    ui.run(dark=True, storage_secret=os.urandom(128))