"""UI layer for PokGotchi2 - pygame_gui based interactive Pokemon care sim.

Handles:
- Game loop and event processing (50/60 FPS)
- Intro and startup flow (showing splash screens)
- Widget creation and management (pygame_gui UIManager)
- Pokémon action dispatch (feed, play, sleep, give energy)
- Pokémon selection menu and switching
- Real-time display updates (needs, mood, age, level, evolution status)
- Configuration flag for spawn pool (ONLY_FIRST_STAGE)

Key Configuration:
- ONLY_FIRST_STAGE (set in classes.py): if True, only spawn base-stage Pokémon.
  Set to False to spawn any evolution stage (for testing/tweaking evolved forms).
"""

from classes import *
from pygame import (
    KEYDOWN,
    K_ESCAPE,
    QUIT,
    RESIZABLE,
    VIDEORESIZE,
    Rect,
    event as pygame_event,
    quit,
    surface,
    time,
)
from pygame_gui import (
    UI_BUTTON_PRESSED,
    UI_TEXT_ENTRY_FINISHED,
    UIManager,
)

# Core timing values.
FRAMERATE = 60  # In fps.
INTRO_FRAMERATE = 30  # In fps.
DISPLAY_MSG_DURATION = 5  # In seconds.

# Reused layout dimensions.
start_button_w = int(STARTUP_W * 0.35)
start_button_h = int(STARTUP_H * 0.2)
ST_PADDING = 4

button_panel_w = window_w // 2 - 2 * ST_PADDING
button_panel_h = int(window_h * 0.22)
button_w = button_panel_w // 2 - 4 * ST_PADDING
button_h = button_panel_h // 2 - 4 * ST_PADDING
big_button_panel_w = button_panel_w
big_button_panel_h = int(button_panel_h / 2 * 3)
pokedex_button_h = button_h
pokedex_button_w = int(pokedex_button_h * (275 / 220))

selection_panel_w = button_panel_w
selection_panel_h = window_h - big_button_panel_h - 4 * ST_PADDING
sel_button_w = selection_panel_w // 3 - 3 * ST_PADDING
sel_button_h = selection_panel_h // 3 - 3 * ST_PADDING

info_panel_w = button_panel_w
info_panel_h = button_panel_h
info_text_h = info_panel_h // 1.8
status_text_w = info_panel_w // 2
status_text_h = info_panel_h - info_text_h - ST_PADDING
status_bar_w = info_panel_w // 2 - 4 * ST_PADDING
status_bar_h = int(info_panel_h // 6)
entry_line_w = int(info_panel_w * 0.9)
entry_line_h = info_text_h // 3

msg_textbox_w = info_panel_w
msg_textbox_h = status_bar_h * 4
display_msg = False
msg_display_timer = 0

if ONLY_FIRST_STAGE:
    starting_pokemon = [
        Charmander,
        Growlithe,
        Vulpix,
        Squirtle,
        Psyduck,
        Magikarp,
        Pichu,
        Magnemite,
        Elekid,
        Geodude,
        Rhyhorn,
        Larvitar,
    ]
else:
    starting_pokemon = [
        Charmander,
        Charmeleon,
        Charizard, 
        Growlithe, 
        Arcanine,  
        Vulpix,    
        Ninetales, 
        Squirtle,  
        Wartortle, 
        Blastoise, 
        Psyduck,   
        Golduck,   
        Magikarp,  
        Gyarados,
        Pichu,  
        Pikachu,
        Raichu, 
        Magnemite,  
        Magneton,   
        Magnezone,  
        Elekid,     
        Electabuzz, 
        Electivire, 
        Geodude,    
        Graveler,   
        Golem,      
        Rhyhorn,    
        Rhydon,     
        Rhyperior,
        Larvitar,
        Pupitar,
        Tyranitar
    ]

display.set_caption("PokGotchi")
clock = time.Clock()


def scale_to_fit(image: surface.Surface, container_size: tuple[int, int]) -> surface.Surface:
    """Scale an image to fit inside a bounding box while preserving aspect ratio.
    
    Used for Pokémon preview thumbnails in selection menu to maintain
    proportions despite varying Pokémon sizes.
    """
    img_w = image.get_width()
    img_h = image.get_height()
    cont_w, cont_h = container_size

    resize_factor = min(cont_w / img_w, cont_h / img_h)
    return transform.scale(
        image, (int(img_w * resize_factor), int(img_h * resize_factor))
    )

def show_message(msg_textbox: elements.UITextBox, message: str):
    """Display a timed status message in msg_textbox and clear display timer.
    
    Used to provide user feedback for actions:
    - 'Leveled Up!' / 'Evolved!' when level changes
    - '+25 Energy' etc. for action confirmations
    
    Uses a shadow effect for contrast. Removes scrollbar if present.
    """
    global display_msg, msg_display_timer
    if message is not None:
        display_msg = True
        msg_display_timer = 0
        msg_textbox.set_text(f"<shadow color='#000000'>{message}</shadow>")
        msg_textbox.scroll_bar.kill() if msg_textbox.scroll_bar is not None else None
        msg_textbox.show()

def start() -> bool:
    """Display startup screen and button loop until player presses START.
    
    Shows the intro screen with a START button. Blocks until user clicks
    START or closes the window (which exits the program).

    Returns: Bool (currently always True if function completes normally).
    Raises: Skip() exception on window close to exit intro flow.
    """
    starting = False

    start_window = display.set_mode((STARTUP_W, STARTUP_H))
    manager = UIManager((STARTUP_W, STARTUP_H), "theme.json")

    start_button = elements.UIButton(
        relative_rect=Rect(
            (
                STARTUP_W // 2 - start_button_w // 2,
                int(STARTUP_H * 0.84) - start_button_h // 2,
            ),
            (start_button_w, start_button_h),
        ),
        text="START",
        object_id="#start_button",
        manager=manager,
    )

    try:
        ticks_passed = 0
        while not starting:
            time_delta = clock.tick(INTRO_FRAMERATE) / 1000.0
            start_window.blit(startup_bg, (0, 0))

            for event in pygame_event.get():
                if event.type == QUIT:
                    quit()
                    raise Skip()

                manager.process_events(event)

                if event.type == UI_BUTTON_PRESSED and event.ui_element == start_button:
                    starting = True
                    print("\nStarting...\n")

            # Blink START button by briefly hiding it each second.
            if ticks_passed % INTRO_FRAMERATE == 0:
                start_button.hide()  # Button is unclickable for one tick per second.
            else:
                start_button.show()

            if ticks_passed % INTRO_FRAMERATE in range(0, INTRO_FRAMERATE // 2):
                manager.update(time_delta)
                manager.draw_ui(start_window)

            display.update()
            ticks_passed += 1
    except Skip:
        pass

    return starting

def colored_text(text: str, html=True) -> str:
    """Format mood/type text with color codes for display.
    
    Provides visual distinction for:
    - Mood states: satisfied (green) -> critical (red)
    - Pokemon types: Fire (red), Water (blue), Electric (yellow), Rock (gray)
    - Death state: died (red)
    
    Args:
        text: Mood or type name to color
        html: If True, use HTML color tags (for pygame_gui display);
              if False, use ANSI terminal escape codes (for console debugging)
    
    Returns: Formatted text with color markup.
    """
    if html:
        text_colors = {
            "satisfied": "#00FF00",
            "content": "#7FFF00",
            "neutral": "#FFFF00",
            "unsettled": "#FF7F00",
            "critical": "#FF0000",
            "Fire": "#FF7300",
            "Water": "#1E90FF",
            "Electric": "#FFFB00",
            "Rock": "#888787",
            "died": "#DB0000",
        }
        color = text_colors.get(text, "#FFFFFF")
        return f'<font color="{color}">{text.upper()}</font>'

    text_colors = {
        "satisfied": "\x1b[32m",
        "content": "\x1b[92m",
        "neutral": "\x1b[93m",
        "unsettled": "\x1b[91m",
        "critical": "\x1b[31m",
        "Fire": "\x1b[31m",
        "Water": "\x1b[34m",
        "Electric": "\x1b[33m",
        "Rock": "\x1b[37m",
        "died": "\x1b[31m",
    }
    color = text_colors.get(text, "\x1b[37m")
    return f"{color}{text.upper()}\x1b[0m"

def selection_menu(manager: UIManager, pokemon_lookup: dict, curr_pokemon: Pokemon = None) -> tuple[elements.UIPanel, list[elements.UIButton]]:
    """Create a 3-column grid of buttons for switching to another active pokemon.
    
    Displays all pokemon except the current one. Each button shows:
    - Poémon's nickname as button text
    - Poémon's sprite image scaled to fit button
    - Preset image states (normal/hover/click/disabled all show same sprite)
    
    Args:
        manager: pygame_gui UIManager for creating widgets
        pokemon_lookup: Dict of all active pokemon {name (species) -> instance}
        curr_pokemon: Currently selected pokemon to exclude from menu
    
    Returns: Tuple of (selection_panel, pokemon_buttons list)
    """
    global pokemon_buttons

    pokemon_buttons = []
    other_pokemon = [
        pokemon_obj
        for pokemon_obj in pokemon_lookup.items()
        if pokemon_obj[1] is not curr_pokemon
    ]

    selection_panel = elements.UIPanel(
        relative_rect=Rect(
            (ST_PADDING, big_button_panel_h + 2 * ST_PADDING),
            (selection_panel_w, selection_panel_h),
        ),
        object_id="#selection_panel",
        manager=manager,
    )
    selection_panel.show()

    for index, pokemon_obj in enumerate(other_pokemon):
        column = index % 3
        row = index // 3
        x_pos = ST_PADDING + (column * (sel_button_w + ST_PADDING))
        y_pos = ST_PADDING + (row * (sel_button_h + ST_PADDING))

        sel_button = elements.UIButton(
            relative_rect=Rect((x_pos, y_pos), (sel_button_w, sel_button_h)),
            text=pokemon_obj[1].name,
            object_id="#selection_button",
            container=selection_panel,
            manager=manager,
        )
        sel_button.pokemon = pokemon_obj[1]

        pokemon_image = IMAGE_DICT.get(pokemon_obj[1].species)
        if pokemon_image is not None:
            alphachanneled_img = pokemon_image.convert_alpha()
            scaled_img = scale_to_fit(alphachanneled_img, (sel_button_w, sel_button_h))

            # Keep the preview visible across all button interaction states.
            sel_button.set_image(scaled_img)
            sel_button.normal_images = [scaled_img]
            sel_button.hovered_images = [scaled_img]
            sel_button.clicked_images = [scaled_img]
            sel_button.selected_images = [scaled_img]
            sel_button.disabled_images = [scaled_img]
            sel_button.rebuild()

        pokemon_buttons.append(sel_button)
        sel_button.show()

    return selection_panel, pokemon_buttons

def update_info(info_text: elements.UITextBox, curr_pokemon: Pokemon):
    """Refresh info panel with current pokemon's name, species, and type.
    
    Displays in the top-right corner. Type name is color-coded by pokemon type.
    """
    info_text.set_text(
    f"<font pixel_size=\"{status_bar_h // 1.1}\"><shadow size=\"1\" color=\"#000000CC\">"
    f"NAME: {curr_pokemon.name if curr_pokemon.name != 'Nameless' else ''}"
    f"\nSPECIES: {curr_pokemon.species}"
    f"\nTYPE: {colored_text(curr_pokemon.type)}</font></shadow>"
    )

def update_status(status_text: elements.UITextBox, curr_pokemon: Pokemon, level_bar: LabeledProgressBar, level_text: elements.UITextBox):
    """Refresh status panel with age, mood, and level/evolution info.
    
    Logic:
    - If pokemon has evolved into final form (next_stage is None):
      Show level number in colored box; hide progress bar
    - If pokemon can still evolve (next_stage exists):
      Show progress bar tracking level toward next evolution; hide level box
    - Age is displayed in seconds or minutes depending on magnitude
    """
    status_text.set_text(
        f"<font pixel_size=\"{status_bar_h // 1.1}\" color=\"#FFFFFF\"><shadow size=\"1\" color=\"#000000CC\">"
        f"AGE: {curr_pokemon.age if curr_pokemon.age < 60 else curr_pokemon.age // 60} "
        f"{' seconds' if curr_pokemon.age < 10 else ('seconds' if curr_pokemon.age < 60 else ('minute ' if curr_pokemon.age // 60 == 1 else 'minutes'))}"
        f"\nMOOD: {colored_text(curr_pokemon.curr_mood)}</font></shadow>"
    )
    # Show evolution progress bar for pokemon that can still evolve, fixed level for final forms.
    if curr_pokemon.next_stage is None:
        level_bar.hide()
        level_text.set_text(f"<shadow size=\"1\" color=\"#000000CC\">level: <font pixel_size=\"{entry_line_h // 1.5}\" color=\"#{curr_pokemon.level % 6 + 4}A3498\">{curr_pokemon.level}</font></shadow>")
        level_text.show()
    else:
        level_bar.show()
        level_text.hide()

def create_widgets(manager):
    """Initialize all pygame_gui widgets for the main game interface.
    
    Layout (left to right):
    - Left: big_button_panel (give energy, play, sleep, feed, new pokemon, pokedex)
    - Center: selection_menu (grid of inactive pokemon)
    - Right: info_panel (name, species, type, age, mood, needs bars, level)
    
    Bottom: message display box for action feedback (temporary pop-ups)
    
    All global widget references are updated for access throughout event loop.
    """

    global big_button_panel, button_panel, give_energy_button, play_button
    global sleep_button, feed_button, new_pokemon_button, pokedex_button
    global info_panel, info_text, entry_line, status_text, level_text
    global level_bar, nutrition_bar, happiness_bar, energy_bar, msg_textbox

    big_button_panel = elements.UIPanel(
        relative_rect=Rect((ST_PADDING, ST_PADDING), (big_button_panel_w, big_button_panel_h)),
        object_id="#big_button_panel",
        manager=manager,
    )
    big_button_panel.show()

    button_panel = elements.UIPanel(
        relative_rect=Rect((0, 0), (button_panel_w, button_panel_h)),
        object_id="#button_panel",
        container=big_button_panel,
        manager=manager,
    )

    give_energy_button = elements.UIButton(
        relative_rect=Rect((ST_PADDING, ST_PADDING), (button_w, button_h)),
        text="GIVE ENERGY",
        object_id="#give_energy_button",
        container=button_panel,
        manager=manager,
    )

    play_button = elements.UIButton(
        relative_rect=Rect((button_panel_w // 2, ST_PADDING), (button_w, button_h)),
        text="PLAY",
        object_id="#play_button",
        container=button_panel,
        manager=manager,
    )

    sleep_button = elements.UIButton(
        relative_rect=Rect((ST_PADDING, button_panel_h // 2), (button_w, button_h)),
        text="PUT TO SLEEP",
        object_id="#sleep_button",
        container=button_panel,
        manager=manager,
    )

    feed_button = elements.UIButton(
        relative_rect=Rect((button_panel_w // 2, button_panel_h // 2), (button_w, button_h)),
        text="FEED",
        object_id="#feed_button",
        container=button_panel,
        manager=manager,
    )

    new_pokemon_button = elements.UIButton(
        relative_rect=Rect(
            (ST_PADDING + (button_w // 2 - button_h) // 2, button_panel_h + ST_PADDING),
            (button_h, button_h),
        ),
        text="",
        object_id="#new_pokemon_button",
        container=big_button_panel,
        manager=manager,
    )

    pokedex_button = elements.UIButton(
        relative_rect=Rect(
            (ST_PADDING + button_w - (button_w // 2 - pokedex_button_w // 2), button_panel_h + ST_PADDING),
            (pokedex_button_w, pokedex_button_h),
        ),
        text="",
        object_id="#pokedex_button",
        container=big_button_panel,
        manager=manager,
    )

    # Right side status and naming UI.
    info_panel = elements.UIPanel(
        relative_rect=Rect(
            (window_w - info_panel_w - ST_PADDING, ST_PADDING),
            (info_panel_w, info_panel_h),
        ),
        object_id="#info_panel",
        manager=manager,
    )

    info_text = elements.UITextBox(
        relative_rect=Rect((0, 0),
                           (info_panel_w, info_text_h)),
        object_id="#info_text",
        html_text="",
        container=info_panel,
        manager=manager,
    )

    entry_line = elements.UITextEntryLine(
        relative_rect=Rect(
            (info_panel_w - entry_line_w - ST_PADDING, ST_PADDING),
            (entry_line_w, entry_line_h),
        ),
        object_id="#entry_line",
        initial_text="",
        container=info_panel,
        manager=manager,
    )
    entry_line.set_text_length_limit(MAX_NAME_LENGTH)
    entry_line.set_allowed_characters(
        list(
            " #$&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_`"
            "abcdefghijklmnopqrstuvwxyz{|}~¡¢£¥¦¨«±´µ·¸»¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×"
            "ØÙÚÛÜÝßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýÿŒœŠšŸƒˆ˜–—‘’‚“”„†‡•…‰‹›"
        )
    )
    entry_line.hide()

    status_text = elements.UITextBox(
        relative_rect=Rect(
            (0, info_panel_h // 2),
            (status_text_w, status_text_h),
            ),
        object_id="#status_text",
        html_text="",
        container=info_panel,
        manager=manager
    )
    status_text.scroll_bar_width = 0
    status_text.hide()

    level_text = elements.UITextBox(
        relative_rect=Rect(
            (info_panel_w // 2, info_panel_h // 6),
            (status_bar_w, 2 * status_bar_h),
        ),
        object_id="#level_text",
        html_text="level",
        container=info_panel,
        manager=manager
    )
    level_text.set_tooltip("Increases only if energy is > 75.", wrap_width=230)
    level_text.scroll_bar_width = 0
    level_text.hide()

    level_bar = LabeledProgressBar(
        relative_rect=Rect(
            (info_panel_w // 2, (info_panel_h - 4 * status_bar_h) - status_bar_h // 1.5),
            (status_bar_w, status_bar_h),
        ),
        object_id="#level_bar",
        container=info_panel,
        label="level",
        maximum_progress=10,
        manager=manager,
    )
    level_bar.set_tooltip("Increases only if energy is > 75.", wrap_width=230)

    nutrition_bar = LabeledProgressBar(
        relative_rect=Rect(
            (info_panel_w // 2, (info_panel_h - 3 * status_bar_h) - status_bar_h // 1.5),
            (status_bar_w, status_bar_h),
        ),
        object_id="#nutrition_bar",
        container=info_panel,
        label="nutrition",
        manager=manager,
    )

    happiness_bar = LabeledProgressBar(
        relative_rect=Rect(
            (info_panel_w // 2, (info_panel_h - 2 * status_bar_h) - status_bar_h // 1.5),
            (status_bar_w, status_bar_h),
        ),
        object_id="#happiness_bar",
        container=info_panel,
        label="happiness",
        manager=manager,
    )

    energy_bar = LabeledProgressBar(
        relative_rect=Rect(
            (info_panel_w // 2, (info_panel_h - status_bar_h) - status_bar_h // 1.5),
            (status_bar_w, status_bar_h),
        ),
        object_id="#energy_bar",
        container=info_panel,
        label="energy",
        manager=manager,
    )

    msg_textbox = elements.UITextBox(
        relative_rect=Rect((window_w - msg_textbox_w - 2 * ST_PADDING, window_h - msg_textbox_h - ST_PADDING),
                           (msg_textbox_w, msg_textbox_h)),
        object_id="#msg_textbox",
        html_text="",
        manager=manager
    )
    msg_textbox.hide()

def main():
    """Main game loop
    
    Initialization:
    - Set up main window and pygame_gui UIManager
    - Create all UI widgets
    - Initialize current_pokemon as None
    
    Game Loop (runs at 60 FPS):
    1. Event handling:
       - Window close/ESC: exit program
       - Window resize: scale backgrounds and UI
       - Button presses: trigger pokemon actions (feed, play, sleep, give energy)
       - Pokémon selection: switch current Pokémon via menu buttons
       - Text entry: validate and set pokemon nickname on ENTER
    
    2. Pokémon updates:
       - Call update() on all active Pokémon (decay, mood, age, level progression)
       - Trigger level_up() if energy > 75
       - Handle evolution and level-related status messages
    
    3. Display updates:
       - Render active Pokémon sprite (normal or sleeping based on state)
       - Refresh info/status panels with current Pokémon data
       - Update need progress bars (nutrition, energy, happiness)
       - Render timed status messages (fade after DISPLAY_MSG_DURATION)
       - Swap between day/night backgrounds based on awake/sleep state
    
    4. UI updates:
       - Enable/disable buttons based on game state (e.g., disable \"new_pokemon\" at POKEMON_LIMIT)
       - Show/hide widgets as needed
    """

    global background, night_background, display_msg, msg_display_timer
    curr_pokemon = None
    selection_panel = None
    pokemon_buttons = []

    window = display.set_mode((window_w, window_h), RESIZABLE)
    manager = UIManager((window_w, window_h), "theme.json")
    create_widgets(manager)

    ticks_passed = 0
    while True:
        # Clear screen each frame to avoid stale pixels.
        window.fill((0, 0, 0))
        time_delta = clock.tick(FRAMERATE) / 1000.0

        for event in pygame_event.get():
            if (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return

            manager.process_events(event)

            if event.type == VIDEORESIZE:
                window_width, window_height = event.w, event.h
                window = display.set_mode((window_width, window_height), RESIZABLE)
                background = transform.scale(background, (window_width, window_height))
                night_background = transform.scale(night_background, (window_width, window_height))
                manager.set_window_resolution((window_width, window_height))

            if event.type == UI_BUTTON_PRESSED:
                if event.ui_element == new_pokemon_button:
                    big_button_panel.disable()

                    new_pokemon = choice(starting_pokemon)
                    curr_pokemon = new_pokemon("Nameless")
                    show_message(msg_textbox, f"Enter nickname for {curr_pokemon.species}.")
                    
                    give_energy_button.set_text(f"GIVE {curr_pokemon.energy_source}")
                    entry_line.show()
                    entry_line.focus()

                # Pokémon selection from menu.
                if selection_panel is not None and selection_panel.visible:
                    for button in pokemon_buttons:
                        if event.ui_element == button:
                            curr_pokemon = button.pokemon
                            update_info(info_text, curr_pokemon)
                            give_energy_button.set_text(
                                f"GIVE {curr_pokemon.energy_source}"
                            )
                            break
                elif selection_panel is not None:
                    selection_panel.hide()
                    selection_panel = None

                if event.ui_element == pokedex_button:
                    if selection_panel is not None and selection_panel.visible:
                        selection_panel.hide()
                        selection_panel = None
                        for button in pokemon_buttons:
                            button.hide()
                        pokemon_buttons = []
                    else:
                        selection_panel, pokemon_buttons = selection_menu(
                            manager, pokemon_dict,
                            curr_pokemon
                        )
                elif selection_panel is not None:
                    selection_panel.hide()
                    selection_panel = None

                # No use feeding a dead pet.
                if curr_pokemon is not None and curr_pokemon.is_alive:

                    update_info(info_text, curr_pokemon)

                    if event.ui_element == feed_button:
                        curr_pokemon.feed()
                    elif event.ui_element == give_energy_button:
                        show_message(msg_textbox, curr_pokemon.give_energy())
                        curr_pokemon.last_energy_donation = curr_pokemon.age
                        update_info(info_text, curr_pokemon)
                    elif event.ui_element == sleep_button:
                        if curr_pokemon.is_awake:
                            curr_pokemon.sleep()
                            big_button_panel.disable()
                            sleep_button.set_text("WAKE UP")
                            sleep_button.enable()
                            pokedex_button.enable()
                        else:
                            curr_pokemon.wake_up()
                            big_button_panel.enable()
                            sleep_button.set_text("PUT TO SLEEP")
                    elif event.ui_element == play_button:
                        curr_pokemon.play()

            if event.type == UI_TEXT_ENTRY_FINISHED and event.ui_element == entry_line:
                name = event.text

                if name in pokemon_names:
                    show_message(
                        msg_textbox,
                        f"<font color = \"#1E90FF\">{name}</font> already exists."
                    )
                    
                elif len(name) > 0 and name != "Nameless":
                    pokemon_names.remove(curr_pokemon.name)
                    del pokemon_dict[str(curr_pokemon)]
                    curr_pokemon.name = name
                    pokemon_names.append(name)
                    pokemon_dict[str(curr_pokemon)] = curr_pokemon
                    big_button_panel.enable()
                    entry_line.set_text("")
                    entry_line.unfocus()
                    entry_line.hide()
                    update_info(info_text, curr_pokemon)

                elif len(pokemon_names) >= POKEMON_LIMIT:
                    show_message(
                        msg_textbox,
                        f"\nYou have reached the Pokémon limit of {POKEMON_LIMIT}.",
                    )

        if curr_pokemon is not None and not curr_pokemon.is_awake:
            curr_background = night_background
        else:
            curr_background = background
        window.blit(curr_background, (0, 0))

        if curr_pokemon is not None:
            level_bar.set_current_progress(curr_pokemon.level)
            nutrition_bar.set_current_progress(curr_pokemon.nutrition)
            energy_bar.set_current_progress(curr_pokemon.energy)
            happiness_bar.set_current_progress(curr_pokemon.happiness)
            info_panel.show()
            update_status(status_text, curr_pokemon, level_bar, level_text)

            if not curr_pokemon.is_awake and curr_pokemon.energy >= 100:
                curr_pokemon.wake_up()

            if curr_pokemon.is_awake:
                big_button_panel.enable()
                sleep_button.set_text("PUT TO SLEEP")

                if (
                    curr_pokemon.age - curr_pokemon.last_energy_donation
                    < ENERGY_DONATION_COOLDOWN
                ):
                    give_energy_button.disable()
                else:
                    give_energy_button.enable()
            else:
                # Keep only wake-up action available while sleeping.
                big_button_panel.disable()
                sleep_button.set_text("WAKE UP")
                sleep_button.enable()
                pokedex_button.enable()

            window.blit(curr_pokemon.img, curr_pokemon.rect.topleft)

            for pokemon in pokemon_group:
                if pokemon.update(ticks_passed, FRAMERATE) == "died":
                    show_message(
                        msg_textbox,
                        f"{pokemon.name} {colored_text('died')}.",
                    )
        else:
            info_panel.hide()
            big_button_panel.disable()

        if len(pokemon_names) >= POKEMON_LIMIT:
            new_pokemon_button.disable()
        else:
            new_pokemon_button.enable()

        if entry_line.visible:
            big_button_panel.disable()

        if display_msg:
            msg_textbox.show()
            msg_display_timer += 1
            if msg_display_timer >= DISPLAY_MSG_DURATION * FRAMERATE:
                display_msg = False
                msg_display_timer = 0
                msg_textbox.set_text("")
                msg_textbox.hide()

        ticks_passed += 1

        manager.update(time_delta)
        manager.draw_ui(window)
        display.update()


# Entry point: show intro screen, then run main game loop.
if __name__ == "__main__" and start():

    main()

    quit()
    print("\nQuitting...\n")