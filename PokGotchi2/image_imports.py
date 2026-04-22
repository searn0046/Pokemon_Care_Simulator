"""Resource initialization and asset preloading for PokGotchi2.

This module handles:
- Pygame initialization and window setup
- Image asset loading and scaling for all backgrounds
- Preloading all Pokémon species sprites into IMAGE_DICT for quick access
- Display of intro splash screen on import

Module-level code runs once at import time, establishing the game window dimensions
based on desktop resolution.
"""

import os
from pygame import RESIZABLE, WINDOWMAXIMIZED, display, image, init, transform

os.environ["SDL_VIDEO_CENTERED"] = "1"
init()

# Background and UI image paths.
INTRO_IMG = "images/pokgotchi.png"
STARTUP_IMG = "images/pokgotchi_no_buttons.jpg"
GENERIC_BG = "images/generic_background.jpg"
NIGHT_BG = "images/night_background.jpg"
POKEBALL_IMG = "images/pokeball.png"
GRAVESTONE_IMG = "images/gravestone.png"

# Load startup visuals and show intro splash once at import time.
intro_bg = image.load(INTRO_IMG)
STARTUP_W = intro_bg.get_width()
STARTUP_H = intro_bg.get_height()
intro_bg = transform.scale(intro_bg, (STARTUP_W, STARTUP_H))

# Display intro splash screen. This window is replaced with main game window in main.py.
intro_window = display.set_mode((STARTUP_W, STARTUP_H), RESIZABLE | WINDOWMAXIMIZED)
intro_window.blit(intro_bg, (0, 0))
display.flip()

startup_bg = image.load(STARTUP_IMG)
startup_bg = transform.scale(startup_bg, (STARTUP_W, STARTUP_H))

# Calculate main game window dimensions as 80% of desktop size (allows room for taskbar/borders).
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
CHARMELEON_IMG = "images/charmeleon.png"
CHARMELEON_SLEEPING = "images/charmeleon_sleeping.png"
CHARIZARD_IMG = "images/charizard.png"
CHARIZARD_SLEEPING = "images/charizard_sleeping.png"

GROWLITHE_IMG = "images/growlithe.png"
GROWLITHE_SLEEPING = "images/growlithe_sleeping.png"
ARCANINE_IMG = "images/arcanine.png"
ARCANINE_SLEEPING = "images/arcanine_sleeping.png"

# Fire-type species paths.
VULPIX_IMG = "images/vulpix.png"
VULPIX_SLEEPING = "images/vulpix_sleeping.png"
NINETALES_IMG = "images/ninetales.png"
NINETALES_SLEEPING = "images/ninetales_sleeping.png"

####################
# Water-type species paths.

SQUIRTLE_IMG = "images/squirtle.png"
SQUIRTLE_SLEEPING = "images/squirtle_sleeping.png"
WARTORTLE_IMG = "images/wartortle.png"
WARTORTLE_SLEEPING = "images/wartortle_sleeping.png"
BLASTOISE_IMG = "images/blastoise.png"
BLASTOISE_SLEEPING = "images/blastoise_sleeping.png"

PSYDUCK_IMG = "images/psyduck.png"
PSYDUCK_SLEEPING = "images/psyduck_sleeping.png"
GOLDUCK_IMG = "images/golduck.png"
GOLDUCK_SLEEPING = "images/golduck_sleeping.png"

MAGIKARP_IMG = "images/magikarp.png"
MAGIKARP_SLEEPING = "images/magikarp_sleeping.png"
GYARADOS_IMG = "images/gyarados.png"
GYARADOS_SLEEPING = "images/gyarados_sleeping.png"

####################
# Electric-type species paths.

PICHU_IMG = "images/pichu.png"
PICHU_SLEEPING = "images/pichu_sleeping.png"
PIKACHU_IMG = "images/pikachu.png"
PIKACHU_SLEEPING = "images/pikachu_sleeping.png"
RAICHU_IMG = "images/raichu.png"
RAICHU_SLEEPING = "images/raichu_sleeping.png"


MAGNEMITE_IMG = "images/magnemite.png"
MAGNEMITE_SLEEPING = "images/magnemite_sleeping.png"
MAGNETON_IMG = "images/magneton.png"
MAGNETON_SLEEPING = "images/magneton_sleeping.png"
MAGNEZONE_IMG = "images/magnezone.png"
MAGNEZONE_SLEEPING = "images/magnezone_sleeping.png"

ELEKID_IMG = "images/elekid.png"
ELEKID_SLEEPING = "images/elekid_sleeping.png"
ELECTABUZZ_IMG = "images/electabuzz.png"
ELECTABUZZ_SLEEPING = "images/electabuzz_sleeping.png"
ELECTIVIRE_IMG = "images/electivire.png"
ELECTIVIRE_SLEEPING = "images/electivire_sleeping.png"

####################
# Rock-type species paths.

GEODUDE_IMG = "images/geodude.png"
GEODUDE_SLEEPING = "images/geodude_sleeping.png"
GRAVELER_IMG = "images/graveler.png"
GRAVELER_SLEEPING = "images/graveler_sleeping.png"
GOLEM_IMG = "images/golem.png"
GOLEM_SLEEPING = "images/golem_sleeping.png"

RHYHORN_IMG = "images/rhyhorn.png"
RHYHORN_SLEEPING = "images/rhyhorn_sleeping.png"
RHYDON_IMG = "images/rhydon.png"
RHYDON_SLEEPING = "images/rhydon_sleeping.png"
RHYPERIOR_IMG = "images/rhyperior.png"
RHYPERIOR_SLEEPING = "images/rhyperior_sleeping.png"

LARVITAR_IMG = "images/larvitar.png"
LARVITAR_SLEEPING = "images/larvitar_sleeping.png"
PUPITAR_IMG = "images/pupitar.png"
PUPITAR_SLEEPING = "images/pupitar_sleeping.png"
TYRANITAR_IMG = "images/tyranitar.png"
TYRANITAR_SLEEPING = "images/tyranitar_sleeping.png"

# All Pokémon species sprites preloaded for fast lookup.
# Dictionary is keyed by species name with both awake and sleeping variants.
# Used by main.py UI for displaying Pokémon previews in selection menu and status panels.
IMAGE_DICT = {
    "Charmander": image.load(CHARMANDER_IMG).convert_alpha(),
    "Charmander_Sleeping": image.load(CHARMANDER_SLEEPING).convert_alpha(),
    "Charmeleon": image.load(CHARMELEON_IMG).convert_alpha(),
    "Charmeleon_Sleeping": image.load(CHARMELEON_SLEEPING).convert_alpha(),
    "Charizard": image.load(CHARIZARD_IMG).convert_alpha(),
    "Charizard_Sleeping": image.load(CHARIZARD_SLEEPING).convert_alpha(),
    "Growlithe": image.load(GROWLITHE_IMG).convert_alpha(),
    "Growlithe_Sleeping": image.load(GROWLITHE_SLEEPING).convert_alpha(),
    "Arcanine": image.load(ARCANINE_IMG).convert_alpha(),
    "Arcanine_Sleeping": image.load(ARCANINE_SLEEPING).convert_alpha(),
    "Vulpix": image.load(VULPIX_IMG).convert_alpha(),
    "Vulpix_Sleeping": image.load(VULPIX_SLEEPING).convert_alpha(),
    "Ninetales": image.load(NINETALES_IMG).convert_alpha(),
    "Ninetales_Sleeping": image.load(NINETALES_SLEEPING).convert_alpha(),
    "Squirtle": image.load(SQUIRTLE_IMG).convert_alpha(),
    "Squirtle_Sleeping": image.load(SQUIRTLE_SLEEPING).convert_alpha(),
    "Wartortle": image.load(WARTORTLE_IMG).convert_alpha(),
    "Wartortle_Sleeping": image.load(WARTORTLE_SLEEPING).convert_alpha(),
    "Blastoise": image.load(BLASTOISE_IMG).convert_alpha(),
    "Blastoise_Sleeping": image.load(BLASTOISE_SLEEPING).convert_alpha(),
    "Psyduck": image.load(PSYDUCK_IMG).convert_alpha(),
    "Psyduck_Sleeping": image.load(PSYDUCK_SLEEPING).convert_alpha(),
    "Golduck": image.load(GOLDUCK_IMG).convert_alpha(),
    "Golduck_Sleeping": image.load(GOLDUCK_SLEEPING).convert_alpha(),
    "Magikarp": image.load(MAGIKARP_IMG).convert_alpha(),
    "Magikarp_Sleeping": image.load(MAGIKARP_SLEEPING).convert_alpha(),
    "Gyarados": image.load(GYARADOS_IMG).convert_alpha(),
    "Gyarados_Sleeping": image.load(GYARADOS_SLEEPING).convert_alpha(),
    "Pichu": image.load(PICHU_IMG).convert_alpha(),
    "Pichu_Sleeping": image.load(PICHU_SLEEPING).convert_alpha(),
    "Pikachu": image.load(PIKACHU_IMG).convert_alpha(),
    "Pikachu_Sleeping": image.load(PIKACHU_SLEEPING).convert_alpha(),
    "Raichu": image.load(RAICHU_IMG).convert_alpha(),
    "Raichu_Sleeping": image.load(RAICHU_SLEEPING).convert_alpha(),
    "Magnemite": image.load(MAGNEMITE_IMG).convert_alpha(),
    "Magnemite_Sleeping": image.load(MAGNEMITE_SLEEPING).convert_alpha(),
    "Magneton": image.load(MAGNETON_IMG).convert_alpha(),
    "Magneton_Sleeping": image.load(MAGNETON_SLEEPING).convert_alpha(),
    "Magnezone": image.load(MAGNEZONE_IMG).convert_alpha(),
    "Magnezone_Sleeping": image.load(MAGNEZONE_SLEEPING).convert_alpha(),
    "Elekid": image.load(ELEKID_IMG).convert_alpha(),
    "Elekid_Sleeping": image.load(ELEKID_SLEEPING).convert_alpha(),
    "Electabuzz": image.load(ELECTABUZZ_IMG).convert_alpha(),
    "Electabuzz_Sleeping": image.load(ELECTABUZZ_SLEEPING).convert_alpha(),
    "Electivire": image.load(ELECTIVIRE_IMG).convert_alpha(),
    "Electivire_Sleeping": image.load(ELECTIVIRE_SLEEPING).convert_alpha(),
    "Geodude": image.load(GEODUDE_IMG).convert_alpha(),
    "Geodude_Sleeping": image.load(GEODUDE_SLEEPING).convert_alpha(),
    "Graveler": image.load(GRAVELER_IMG).convert_alpha(),
    "Graveler_Sleeping": image.load(GRAVELER_SLEEPING).convert_alpha(),
    "Golem": image.load(GOLEM_IMG).convert_alpha(),
    "Golem_Sleeping": image.load(GOLEM_SLEEPING).convert_alpha(),
    "Rhyhorn": image.load(RHYHORN_IMG).convert_alpha(),
    "Rhyhorn_Sleeping": image.load(RHYHORN_SLEEPING).convert_alpha(),
    "Rhydon": image.load(RHYDON_IMG).convert_alpha(),
    "Rhydon_Sleeping": image.load(RHYDON_SLEEPING).convert_alpha(),
    "Rhyperior": image.load(RHYPERIOR_IMG).convert_alpha(),
    "Rhyperior_Sleeping": image.load(RHYPERIOR_SLEEPING).convert_alpha(),
    "Larvitar": image.load(LARVITAR_IMG).convert_alpha(),
    "Larvitar_Sleeping": image.load(LARVITAR_SLEEPING).convert_alpha(),
    "Pupitar": image.load(PUPITAR_IMG).convert_alpha(),
    "Pupitar_Sleeping": image.load(PUPITAR_SLEEPING).convert_alpha(),
    "Tyranitar": image.load(TYRANITAR_IMG).convert_alpha(),
    "Tyranitar_Sleeping": image.load(TYRANITAR_SLEEPING).convert_alpha()
}