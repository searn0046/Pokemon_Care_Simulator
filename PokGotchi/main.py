from random import choice
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
DISPLAY_MSG_DURATION = 3  # In seconds.

# Reused layout dimensions.
START_BUTTON_W = int(STARTUP_W * 0.35)
START_BUTTON_H = int(STARTUP_H * 0.2)
ST_PADDING = 4

msg_display_timer = 0

button_panel_w = window_w // 2 - 8 * ST_PADDING
button_panel_h = int(window_h * 0.3)
button_w = button_panel_w // 2 - 3 * ST_PADDING
button_h = button_panel_h // 2 - 3 * ST_PADDING
big_button_panel_w = button_panel_w
big_button_panel_h = int(button_panel_h / 2 * 3)
pokedex_button_h = button_h
pokedex_button_w = int(pokedex_button_h * (275 / 220))

selection_panel_w = button_panel_w
selection_panel_h = window_h - big_button_panel_h - 4 * ST_PADDING
sel_button_w = selection_panel_w // 3 - 3 * ST_PADDING
sel_button_h = selection_panel_h // 3 - 3 * ST_PADDING

status_panel_w = button_panel_w
status_panel_h = button_panel_h
status_bar_w = status_panel_w - 4 * ST_PADDING
status_bar_h = int(status_panel_h // 8)
entry_line_w = int(status_panel_w * 0.9)
entry_line_h = status_bar_h

msg_textbox_w = status_bar_w
msg_textbox_h = status_bar_h * 3

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

display.set_caption("PokGotchi")
clock = time.Clock()


def scale_to_fit(image: surface.Surface, container_size: tuple[int, int]) -> surface.Surface:
    """Scale an image to fit inside a bounding box while preserving aspect ratio."""
    img_w = image.get_width()
    img_h = image.get_height()
    cont_w, cont_h = container_size

    resize_factor = min(cont_w / img_w, cont_h / img_h)
    return transform.scale(
        image, (int(img_w * resize_factor), int(img_h * resize_factor))
    )

def show_message(msg_textbox: elements.UITextBox, message: str):
    """Show a timed status message in msg_textbox and reset its display timer."""
    global display_msg, msg_display_timer
    display_msg = True
    msg_display_timer = 0
    msg_textbox.set_text(f"<shadow color='#000000'>{message}</shadow>")
    msg_textbox.show()


def start() -> bool:
    """Show intro screen and wait until the player presses START."""
    starting = False

    start_window = display.set_mode((STARTUP_W, STARTUP_H))
    manager = UIManager((STARTUP_W, STARTUP_H), "theme.json")

    start_button = elements.UIButton(
        relative_rect=Rect(
            (
                STARTUP_W // 2 - START_BUTTON_W // 2,
                int(STARTUP_H * 0.84) - START_BUTTON_H // 2,
            ),
            (START_BUTTON_W, START_BUTTON_H),
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


def colored_text(text: str, html: bool) -> str:
    """Return mood/type text with either HTML color tags or terminal ANSI color codes."""
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


def selection_menu(manager: UIManager, pokemon_lookup: dict):
    """Create a panel of buttons for switching to another active pokemon."""
    global curr_pokemon
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


if __name__ == "__main__" and start():
    running = True

    window = display.set_mode((window_w, window_h), RESIZABLE)
    manager = UIManager((window_w, window_h), "theme.json")

    # Left side controls.
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
        text="SLEEP",
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
            (button_panel_w // 4 - button_h // 2, button_panel_h),
            (button_h, button_h),
        ),
        text="",
        object_id="#new_pokemon_button",
        container=big_button_panel,
        manager=manager,
    )

    pokedex_button = elements.UIButton(
        relative_rect=Rect(
            (button_panel_w // 4 * 3 - pokedex_button_w // 2, button_panel_h),
            (pokedex_button_w, pokedex_button_h),
        ),
        text="",
        object_id="#pokedex_button",
        container=big_button_panel,
        manager=manager,
    )

    # Right side status and naming UI.
    status_panel = elements.UIPanel(
        relative_rect=Rect(
            (window_w - status_panel_w - 2 * ST_PADDING, 2 * ST_PADDING),
            (status_panel_w, status_panel_h),
        ),
        object_id="#status_panel",
        manager=manager,
    )

    info_text = elements.UITextBox(
        relative_rect=Rect((ST_PADDING, 0), (status_bar_w, int(status_bar_h * 2.4))),
        object_id="#info_text",
        html_text="",
        container=status_panel,
        manager=manager,
    )

    status_text = elements.UITextBox(
        relative_rect=Rect(
            (ST_PADDING, int(status_bar_h * 2.4)),
            (status_bar_w, status_bar_h * 2 + 2 * ST_PADDING),
        ),
        object_id="#status_text",
        html_text="",
        container=status_panel,
        manager=manager,
    )
    status_text.scroll_bar_width = 10
    status_text.hide()

    nutrition_bar = LabeledProgressBar(
        relative_rect=Rect(
            (0, int(status_bar_h * 2.4) + status_bar_h * 2 + 2 * ST_PADDING),
            (status_bar_w, status_bar_h),
        ),
        object_id="#nutrition_bar",
        container=status_panel,
        label="nutrition",
        manager=manager,
    )
    nutrition_bar.hide()

    happiness_bar = LabeledProgressBar(
        relative_rect=Rect(
            (0, int(status_bar_h * 2.4) + status_bar_h * 3 + 2 * ST_PADDING),
            (status_bar_w, status_bar_h),
        ),
        object_id="#happiness_bar",
        container=status_panel,
        label="happiness",
        manager=manager,
    )
    happiness_bar.hide()

    energy_bar = LabeledProgressBar(
        relative_rect=Rect(
            (0, int(status_bar_h * 2.4) + status_bar_h * 4 + 2 * ST_PADDING),
            (status_bar_w, status_bar_h),
        ),
        object_id="#energy_bar",
        container=status_panel,
        label="energy",
        manager=manager,
    )
    energy_bar.hide()

    entry_line = elements.UITextEntryLine(
        relative_rect=Rect(
            (status_panel_w - entry_line_w - ST_PADDING, ST_PADDING),
            (entry_line_w, entry_line_h),
        ),
        object_id="#entry_line",
        container=status_panel,
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

    msg_textbox = elements.UITextBox(
        relative_rect=Rect((window_w - msg_textbox_w - 2 * ST_PADDING, window_h - msg_textbox_h - ST_PADDING),
                           (msg_textbox_w, msg_textbox_h)),
        object_id="#msg_textbox",
        html_text="",
        manager=manager,
    )
    msg_textbox.hide()

    curr_pokemon = None
    selection_panel = None
    pokemon_buttons = []

    ticks_passed = 0
    while running:
        # Clear screen each frame to avoid stale pixels.
        window.fill((0, 0, 0))
        time_delta = clock.tick(FRAMERATE) / 1000.0

        for event in pygame_event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False

            manager.process_events(event)

            if event.type == VIDEORESIZE:
                window_width, window_height = event.w, event.h
                window = display.set_mode((window_width, window_height), RESIZABLE)
                background = transform.scale(background, (window_width, window_height))
                manager.set_window_resolution((window_width, window_height))

            if event.type == UI_BUTTON_PRESSED:
                if event.ui_element == new_pokemon_button:
                    big_button_panel.disable()

                    new_pokemon = choice(starting_pokemon)
                    curr_pokemon = new_pokemon("Nameless")

                    info_text.set_text(
                        f"<shadow size=\"1\" color=\"#000000CC\">"
                        f"NAME: {curr_pokemon.name if curr_pokemon.name != 'Nameless' else ''}"
                        f"\nSPECIES: {curr_pokemon.species} "
                        f"({colored_text(curr_pokemon.type, html=True)} type)</shadow>"
                    )
                    show_message(msg_textbox, f"Enter nickname for {curr_pokemon.species}.")
                    
                    sleep_button.set_text("SLEEP")
                    give_energy_button.set_text(f"GIVE {curr_pokemon.energy_source}")
                    entry_line.show()
                    entry_line.focus()

                # Pokémon selection from menu.
                if selection_panel is not None and selection_panel.visible:
                    for button in pokemon_buttons:
                        if event.ui_element == button:
                            curr_pokemon = button.pokemon
                            info_text.set_text(
                                f"<shadow size=\"1\" color=\"#000000CC\">"
                                f"NAME: {curr_pokemon.name if curr_pokemon.name != 'Nameless' else ''}"
                                f"\nSPECIES: {curr_pokemon.species} "
                                f"({colored_text(curr_pokemon.type, html=True)} type)</shadow>"
                            )
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
                            manager, pokemon_dict
                        )
                elif selection_panel is not None:
                    selection_panel.hide()
                    selection_panel = None

                # No use feeding a dead pet.
                if curr_pokemon is not None and curr_pokemon.is_alive:
                    if event.ui_element == feed_button:
                        curr_pokemon.feed()
                    elif event.ui_element == give_energy_button:
                        curr_pokemon.give_energy()
                        curr_pokemon.last_energy_donation = curr_pokemon.age
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
                            sleep_button.set_text("SLEEP")
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
                    del pokemon_dict[str(curr_pokemon)]  # Try without this.
                    curr_pokemon.name = name
                    pokemon_names.append(name)
                    pokemon_dict[str(curr_pokemon)] = curr_pokemon
                    big_button_panel.enable()
                    entry_line.set_text("")
                    entry_line.unfocus()
                    entry_line.hide()

                    info_text.set_text(
                        f"<shadow size=\"1\" color=\"#000000CC\">"
                        f"NAME: {curr_pokemon.name if curr_pokemon.name != 'Nameless' else ''}"
                        f"\nSPECIES: {curr_pokemon.species} "
                        f"({colored_text(curr_pokemon.type, html=True)} type)</shadow>"
                    )
#                    print("\n\x1b[4mAll current Pokémon\x1b[0;1m")
#                    for pokemon in pokemon_names:
#                        print(pokemon)
#                    print("\x1b[0m")

                if len(pokemon_names) >= POKEMON_LIMIT:
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
            status_panel.show()
            nutrition_bar.set_current_progress(round(curr_pokemon.nutrition, 3))
            energy_bar.set_current_progress(curr_pokemon.energy)
            happiness_bar.set_current_progress(curr_pokemon.happiness)
            status_text.set_text(
                f"<shadow size=\"1\" color=\"#000000CC\">"
                f"AGE: {curr_pokemon.age // 60} "
                f"{'minute' if curr_pokemon.age // 60 == 1 else 'minutes'}"
                f"\nMOOD: {colored_text(curr_pokemon.curr_mood, html=True)}</shadow>"
            )

            if not curr_pokemon.is_awake and curr_pokemon.energy >= 100:
                curr_pokemon.wake_up()

            if curr_pokemon.is_awake:
                big_button_panel.enable()
                sleep_button.set_text("SLEEP")

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

            window.blit(curr_pokemon.image, curr_pokemon.rect.topleft)

            for pokemon in pokemon_group:
                if pokemon.update(ticks_passed, FRAMERATE) == "died":
                    show_message(
                        msg_textbox,
                        f"{pokemon.name} {colored_text('died', html=True)}.",
                    )
        else:
            status_panel.hide()
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

quit()
print("\nQuitting...\n")
