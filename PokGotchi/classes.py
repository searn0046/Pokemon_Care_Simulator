from abc import ABC, abstractmethod
from random import randint
from time import time

from image_imports import *
from pygame import sprite, rect
from pygame_gui import elements

# Shared runtime state.
SPAWNPOINT = (int(window_w * 0.7), int(window_h * 0.85))
pokemon_names = []
pokemon_group = []
pokemon_dict = {}
POKEMON_LIMIT = 10
MAX_NAME_LENGTH = 40
ENERGY_DONATION_COOLDOWN = 30  # In seconds.
display_msg = False

class Skip(Exception):
    """Alternative to a goto-style early exit for intro flow."""

    pass

class LabeledProgressBar(elements.UIProgressBar):
    """UIProgressBar that always displays a label and integer progress values."""

    def __init__(self, *args, label="", **kwargs):
        self.label = label
        super().__init__(*args, **kwargs)

    def set_current_progress(self, progress: float):
        self.current_progress = progress
        if self.maximum_progress <= 0:
            self.percent_full = 0.0
        else:
            self.percent_full = max(0.0, min(1.0, progress / self.maximum_progress))

    def status_text(self):
        return f"{self.label}: {int(self.current_progress)} / {int(self.maximum_progress)}"

class Pokemon(sprite.Sprite, ABC):
    """Base pokemon behavior shared by all species and elemental types."""

    @abstractmethod
    def __init__(self):
        super().__init__()

        pokemon_names.append(self.name)

        # Load and scale awake sprite.
        self.image = image.load(self.image_name).convert_alpha()
        self.image = transform.scale(
            self.image,
            (
                int(self.image.get_width() * self.scale_factor),
                int(self.image.get_height() * self.scale_factor),
            ),
        )
        self.orig_image = self.image

        self.img_w = self.image.get_width()
        self.img_h = self.image.get_height()

        # Load and scale sleeping sprite.
        self.image_sleeping = image.load(self.image_sleeping).convert_alpha()
        self.image_sleeping = transform.scale(
            self.image_sleeping,
            (
                int(self.image_sleeping.get_width() * self.sleeping_scale_factor),
                int(self.image_sleeping.get_height() * self.sleeping_scale_factor),
            ),
        )

        self.x = SPAWNPOINT[0] - self.img_w // 2
        self.y = SPAWNPOINT[1] - self.img_h
        self.rect = rect.Rect(self.x, self.y, self.img_w, self.img_h)
        self.anchor = self.rect.midbottom
        print(f"Spawned {self.species} at {self.rect.midbottom}")
        self.speed_x = 0
        self.speed_y = 0

        self.exact_age = 0
        self.age = 0
        self.spawn_time = time()
        self.is_alive = True
        self.is_awake = True

        self.__nutrition = randint(80, 100)
        self.__energy = randint(80, 100)
        self.__happiness = randint(80, 100)
        self.__level = 1
        self.curr_mood = "undefined"
        self.moods = ["critical", "unsettled", "neutral", "content", "satisfied"]
        self.top_mood_score = 3 * 100
        self.mood_score = self.nutrition + self.energy + self.happiness
        self.last_energy_donation = -ENERGY_DONATION_COOLDOWN

        pokemon_group.append(self)
        pokemon_dict[self.__str__()] = self

    @property
    def nutrition(self):
        return self.__nutrition

    @property
    def energy(self):
        return self.__energy

    @property
    def happiness(self):
        return self.__happiness
    
    @property
    def level(self):
        return self.__level

    def __clamp_percentage(self, value: int):
        return max(0, min(100, value))

    def __set_nutrition(self, value: int):
        self.__nutrition = self.__clamp_percentage(value)

    def __set_energy(self, value: int):
        self.__energy = self.__clamp_percentage(value)

    def __set_happiness(self, value: int):
        self.__happiness = self.__clamp_percentage(value)

    def __set_level(self, value: int):
        self.__level = self.__clamp_percentage(value)

    def __change_nutrition(self, delta: int):
        self.__set_nutrition(self.__nutrition + delta)

    def __change_energy(self, delta: int):
        self.__set_energy(self.__energy + delta)

    def __change_happiness(self, delta: int):
        self.__set_happiness(self.__happiness + delta)

    def print_status(self, nutrition_change: int, energy_change: int, happiness_change: int):
        # Uncomment to get diagnostics in the terminal.
        '''
        if self.age % 5 == 0:
            print(f"\n\x1b[1;3m{self.name}\x1b[0m\
                    \nAge: \x1b[1m{self.age}\x1b[0ms\
                    \nMood score: \x1b[1m{self.mood_score}\x1b[0m\
                    \nMood: {self.curr_mood}\
                    \n\nNutrition: \x1b[1m{self.nutrition}\x1b[0m% {nutrition_change}\
                    \nEnergy: \x1b[1m{self.energy}\x1b[0m% {energy_change}\
                    \nHappiness: \x1b[1m{self.happiness}\x1b[0m% {happiness_change}\n")
        '''
        pass

    def update(self, ticks_passed: int, framerate: int):
        if self.is_alive:

            # Age is tracked in seconds.
            self.exact_age = time() - self.spawn_time
            self.age = round(self.exact_age)
            if self.set_mood() == "died":
                return "died"

            # Decay rates are per minute (60s).
            if self.is_awake:
                if ticks_passed % (60 * framerate // self.nutrition_decay) == 0:
                    self.__change_nutrition(-1)
                    self.print_status("\x1b[1;31m-1\x1b[0m", "", "")

                if ticks_passed % (60 * framerate // self.energy_decay) == 0:
                    self.__change_energy(-1)
                    self.print_status("", "\x1b[1;31m-1\x1b[0m", "")

                if ticks_passed % (60 * framerate // self.happiness_decay) == 0:
                    self.__change_happiness(-1)
                    self.print_status("", "", "\x1b[1;31m-1\x1b[0m")
            else:  # If sleeping, nutrition decays more slowly and energy regenerates.
                if ticks_passed % (120 * framerate // self.nutrition_decay) == 0:
                    self.__change_nutrition(-1)
                    self.print_status("\x1b[1;31m-1\x1b[0m", "", "")

                if ticks_passed % (15 * framerate // self.energy_decay) == 0:
                    old_energy = self.energy
                    self.__change_energy(1)
                    if self.energy > old_energy:
                        self.print_status("", "\x1b[1;32m+1\x1b[0m", "")

                    if self.energy >= 100:
                        self.wake_up()

    def set_mood(self):
        # This should only be called while the pokemon is alive.

        self.mood_score = self.nutrition + self.energy + self.happiness
        levels = [self.nutrition, self.energy, self.happiness]
        lowest = min(levels)
        avg = self.mood_score / 3

        if lowest <= 0:
            self.curr_mood = "-"
            return self.die()

        if lowest < 15:
            self.curr_mood = self.moods[0]
        elif lowest < 30:
            self.curr_mood = self.moods[1]
        elif avg > 85:
            self.curr_mood = self.moods[4]
        elif avg > 70:
            self.curr_mood = self.moods[3]
        elif avg > 50:
            self.curr_mood = self.moods[2]
        elif avg > 35:
            self.curr_mood = self.moods[1]
        elif lowest > 0:
            self.curr_mood = self.moods[0]

    def give_energy(self):
        if self.is_alive:
            energy = randint(20, 30)
            if self.energy + energy > 100:
                overload = self.energy + energy - 100
                energy -= overload
            self.__change_energy(energy)
            self.print_status("", f"\x1b[1;32m+{energy}\x1b[0m", "")

    def sleep(self):
        if self.is_alive:
            self.is_awake = False
            anchor = self.rect.midbottom
            self.image = self.image_sleeping
            self.rect = self.image.get_rect(midbottom=anchor)
            self.x, self.y = self.rect.topleft

    def feed(self):
        meal = randint(10, 20)
        energy_status = ""
        overload = 0
        # Any overload of feeding points are deducted from energy.
        if self.nutrition + meal > 100:
            overload = self.nutrition + meal - 100
            meal -= overload
            self.__change_energy(-overload)
            energy_status = f"\x1b[1;31m-{overload}\x1b[0m"

        self.__change_nutrition(meal)
        self.print_status(f"\x1b[1;32m+{meal}\x1b[0m", energy_status, "")

    def wake_up(self):
        if self.is_alive:  # Remove this 'if'?
            self.is_awake = True
            if self.energy > 100:
                self.__set_energy(100)  # In case it went over 100.
            anchor = self.rect.midbottom
            self.image = self.orig_image
            self.move_to(anchor)
            self.x, self.y = self.rect.topleft

    def play(self):
        if self.is_alive:
            fun = randint(20, 30)
            energy_status = ""
            overload = 0
            # Any overload of feeding points are deducted from energy.
            if self.happiness + fun > 100:
                overload = self.happiness + fun - 100
                fun -= overload
                self.__change_energy(-overload)
                energy_status = f"\x1b[1;31m-{overload}\x1b[0m"

            self.__change_happiness(fun)
            self.print_status("", energy_status, f"\x1b[1;32m+{fun}\x1b[0m")

    def die(self):
        self.__set_nutrition(0)
        self.__set_happiness(0)
        self.__set_energy(0)
        self.is_alive = False
        self.image = gravestone
        pokemon_names.remove(self.name)
        pokemon_group.remove(self)
        del pokemon_dict[self.__str__()]
        print(f"\n{self.name} \x1b[0;31mdied\x1b[0m.\n")
        return "died"

    def move_to(self, bottom_center_pos: tuple[int, int]):
        # Place the pokemon using bottom-center coordinates.
        self.rect = self.image.get_rect(midbottom=bottom_center_pos)
        self.x, self.y = self.rect.topleft
#        print(f"Moved {self.name} to {self.rect.midbottom}")

    def __str__(self):
        return f"{self.name} ({self.species})"


class FireType(Pokemon):
    """Shared behavior for fire-type pokemon."""
    @abstractmethod
    def __init__(self):
        self.nutrition_decay = randint(4, 6)
        self.energy_decay = randint(6, 10)
        self.happiness_decay = randint(5, 9)

        self.type = "Fire"
        self.energy_source = "FOSSIL FUEL"
        super().__init__()


class WaterType(Pokemon):
    """Shared behavior for water-type pokemon."""
    @abstractmethod
    def __init__(self):
        self.nutrition_decay = randint(6, 10)
        self.energy_decay = randint(8, 12)
        self.happiness_decay = randint(6, 10)

        self.type = "Water"
        self.energy_source = "ELECTROLYTES"
        super().__init__()


class ElectricType(Pokemon):
    """Shared behavior for electric-type pokemon."""
    @abstractmethod
    def __init__(self):
        self.nutrition_decay = randint(2, 4)
        self.energy_decay = randint(10, 14)
        self.happiness_decay = randint(8, 12)

        self.type = "Electric"
        self.energy_source = "BATTERY"
        super().__init__()


class RockType(Pokemon):
    """Shared behavior for rock-type pokemon."""
    @abstractmethod
    def __init__(self):
        self.nutrition_decay = randint(4, 6)
        self.energy_decay = randint(6, 10)
        self.happiness_decay = randint(6, 10)

        self.type = "Rock"
        self.energy_source = "CRYSTAL"
        super().__init__()


########################################

    # Fire-type species.

class Charmander(FireType):
    def __init__(self, name):
        self.name = name
        self.species = "Charmander"
        self.image_name = CHARMANDER_IMG
        self.image_sleeping = CHARMANDER_SLEEPING
        self.scale_factor = 0.2
        self.sleeping_scale_factor = 0.2
        super().__init__()

class Growlithe(FireType):
    def __init__(self, name):
        self.name = name
        self.species = "Growlithe"
        self.image_name = GROWLITHE_IMG
        self.image_sleeping = GROWLITHE_SLEEPING
        self.scale_factor = 0.2
        self.sleeping_scale_factor = 0.2
        super().__init__()

class Vulpix(FireType):
    def __init__(self, name):
        self.name = name
        self.species = "Vulpix"
        self.image_name = VULPIX_IMG
        self.image_sleeping = VULPIX_SLEEPING
        self.scale_factor = 0.25
        self.sleeping_scale_factor = 0.25
        super().__init__()

####################

# Water-type species.

class Squirtle(WaterType):
    def __init__(self, name):
        self.name = name
        self.species = "Squirtle"
        self.image_name = SQUIRTLE_IMG
        self.image_sleeping = SQUIRTLE_SLEEPING
        self.scale_factor = 0.2
        self.sleeping_scale_factor = 0.2
        super().__init__()

class Psyduck(WaterType):
    def __init__(self, name):
        self.name = name
        self.species = "Psyduck"
        self.image_name = PSYDUCK_IMG
        self.image_sleeping = PSYDUCK_SLEEPING
        self.scale_factor = 0.2
        self.sleeping_scale_factor = 0.3
        super().__init__()

class Magikarp(WaterType):
    def __init__(self, name):
        self.name = name
        self.species = "Magikarp"
        self.image_name = MAGIKARP_IMG
        self.image_sleeping = MAGIKARP_SLEEPING
        self.scale_factor = 0.25
        self.sleeping_scale_factor = 0.25
        super().__init__()

####################

# Electric-type species.

class Pichu(ElectricType):
    def __init__(self, name):
        self.name = name
        self.species = "Pichu"
        self.image_name = PICHU_IMG
        self.image_sleeping = PICHU_SLEEPING
        self.scale_factor = 0.23
        self.sleeping_scale_factor = 0.23
        super().__init__()

class Magnemite(ElectricType):
    def __init__(self, name):
        self.name = name
        self.species = "Magnemite"
        self.image_name = MAGNEMITE_IMG
        self.image_sleeping = MAGNEMITE_SLEEPING
        self.scale_factor = 0.3
        self.sleeping_scale_factor = 0.3
        super().__init__()

class Elekid(ElectricType):
    def __init__(self, name):
        self.name = name
        self.species = "Elekid"
        self.image_name = ELEKID_IMG
        self.image_sleeping = ELEKID_SLEEPING
        self.scale_factor = 0.3
        self.sleeping_scale_factor = 0.2
        super().__init__()

####################

# Rock-type species.

class Geodude(RockType):
    def __init__(self, name):
        self.name = name
        self.species = "Geodude"
        self.image_name = GEODUDE_IMG
        self.image_sleeping = GEODUDE_SLEEPING
        self.scale_factor = 0.45
        self.sleeping_scale_factor = 0.3
        super().__init__()

class Rhyhorn(RockType):
    def __init__(self, name):
        self.name = name
        self.species = "Rhyhorn"
        self.image_name = RHYHORN_IMG
        self.image_sleeping = RHYHORN_SLEEPING
        self.scale_factor = 0.3
        self.sleeping_scale_factor = 0.3
        super().__init__()

class Larvitar(RockType):
    def __init__(self, name):
        self.name = name
        self.species = "Larvitar"
        self.image_name = LARVITAR_IMG
        self.image_sleeping = LARVITAR_SLEEPING
        self.scale_factor = 0.2
        self.sleeping_scale_factor = 0.18
        super().__init__()