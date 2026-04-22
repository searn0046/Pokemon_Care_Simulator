import os
from pygame import RESIZABLE, WINDOWMAXIMIZED, display, image, init, transform

os.environ["SDL_VIDEO_CENTERED"] = "1"
init()

INTRO_IMG = "images/pokgotchi.png"
STARTUP_IMG = "images/pokgotchi_no_buttons.jpg"
GENERIC_BG = "images/generic_background.jpg"
NIGHT_BG = "images/night_background.jpg"
POKEBALL_IMG = "images/pokeball.png"
GRAVESTONE_IMG = "images/gravestone.png"

# Load startup visuals and show intro splash once at import.
intro_bg = image.load(INTRO_IMG)
STARTUP_W = intro_bg.get_width()
STARTUP_H = intro_bg.get_height()
intro_bg = transform.scale(intro_bg, (STARTUP_W, STARTUP_H))

intro_window = display.set_mode((STARTUP_W, STARTUP_H), RESIZABLE | WINDOWMAXIMIZED)
intro_window.blit(intro_bg, (0, 0))
display.flip()

startup_bg = image.load(STARTUP_IMG)
startup_bg = transform.scale(startup_bg, (STARTUP_W, STARTUP_H))

# Main game window dimensions based on desktop size.
window_w = int(display.get_desktop_sizes()[0][0] * 0.8)
window_h = int(display.get_desktop_sizes()[0][1] * 0.8)

background = image.load(GENERIC_BG)
background = transform.scale(background, (window_w, window_h))

night_background = image.load(NIGHT_BG)
night_background = transform.scale(night_background, (window_w, window_h))

gravestone = image.load(GRAVESTONE_IMG)
gravestone = transform.scale(
    gravestone, (gravestone.get_width() // 2, gravestone.get_height() // 2)
)

CHARMANDER_IMG = "images/charmander.png"
CHARMANDER_SLEEPING = "images/charmander_sleeping.png"

GROWLITHE_IMG = "images/growlithe.png"
GROWLITHE_SLEEPING = "images/growlithe_sleeping.png"

# Fire-type species paths.
VULPIX_IMG = "images/vulpix.png"
VULPIX_SLEEPING = "images/vulpix_sleeping.png"

####################
# Water-type species paths.

SQUIRTLE_IMG = "images/squirtle.png"
SQUIRTLE_SLEEPING = "images/squirtle_sleeping.png"

PSYDUCK_IMG = "images/psyduck.png"
PSYDUCK_SLEEPING = "images/psyduck_sleeping.png"

MAGIKARP_IMG = "images/magikarp.png"
MAGIKARP_SLEEPING = "images/magikarp_sleeping.png"

####################
# Electric-type species paths.

PICHU_IMG = "images/pichu.png"
PICHU_SLEEPING = "images/pichu_sleeping.png"


MAGNEMITE_IMG = "images/magnemite.png"
MAGNEMITE_SLEEPING = "images/magnemite_sleeping.png"

ELEKID_IMG = "images/elekid.png"
ELEKID_SLEEPING = "images/elekid_sleeping.png"

####################
# Rock-type species paths.

GEODUDE_IMG = "images/geodude.png"
GEODUDE_SLEEPING = "images/geodude_sleeping.png"

RHYHORN_IMG = "images/rhyhorn.png"
RHYHORN_SLEEPING = "images/rhyhorn_sleeping.png"

LARVITAR_IMG = "images/larvitar.png"
LARVITAR_SLEEPING = "images/larvitar_sleeping.png"

# Preloaded alpha surfaces for quick access throughout the UI.
IMAGE_DICT = {
    "Charmander": image.load(CHARMANDER_IMG).convert_alpha(),
    "Charmander_Sleeping": image.load(CHARMANDER_SLEEPING).convert_alpha(),
    "Growlithe": image.load(GROWLITHE_IMG).convert_alpha(),
    "Growlithe_Sleeping": image.load(GROWLITHE_SLEEPING).convert_alpha(),
    "Vulpix": image.load(VULPIX_IMG).convert_alpha(),
    "Vulpix_Sleeping": image.load(VULPIX_SLEEPING).convert_alpha(),
    "Squirtle": image.load(SQUIRTLE_IMG).convert_alpha(),
    "Squirtle_Sleeping": image.load(SQUIRTLE_SLEEPING).convert_alpha(),
    "Psyduck": image.load(PSYDUCK_IMG).convert_alpha(),
    "Psyduck_Sleeping": image.load(PSYDUCK_SLEEPING).convert_alpha(),
    "Magikarp": image.load(MAGIKARP_IMG).convert_alpha(),
    "Magikarp_Sleeping": image.load(MAGIKARP_SLEEPING).convert_alpha(),
    "Pichu": image.load(PICHU_IMG).convert_alpha(),
    "Pichu_Sleeping": image.load(PICHU_SLEEPING).convert_alpha(),
    "Magnemite": image.load(MAGNEMITE_IMG).convert_alpha(),
    "Magnemite_Sleeping": image.load(MAGNEMITE_SLEEPING).convert_alpha(),
    "Elekid": image.load(ELEKID_IMG).convert_alpha(),
    "Elekid_Sleeping": image.load(ELEKID_SLEEPING).convert_alpha(),
    "Geodude": image.load(GEODUDE_IMG).convert_alpha(),
    "Geodude_Sleeping": image.load(GEODUDE_SLEEPING).convert_alpha(),
    "Rhyhorn": image.load(RHYHORN_IMG).convert_alpha(),
    "Rhyhorn_Sleeping": image.load(RHYHORN_SLEEPING).convert_alpha(),
    "Larvitar": image.load(LARVITAR_IMG).convert_alpha(),
    "Larvitar_Sleeping": image.load(LARVITAR_SLEEPING).convert_alpha(),
}