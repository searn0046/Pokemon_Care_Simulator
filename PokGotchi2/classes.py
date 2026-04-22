"""Domain model for PokGotchi2 evolution extension.

Defines the Pokemon class hierarchy with type specializations (Fire, Water, Electric, Rock)
and 12 species with 3-/2-stage evolution chains. Implements:
- Need decay simulation (nutrition, energy, happiness)
- Mood system based on need levels
- Level progression and evolution mechanics
- Dynamic attribute mutation for evolution instance transformation
"""

from abc import ABC, abstractmethod
from random import randint, choice
from time import time
from math import sqrt
from image_imports import *
from pygame import sprite, rect
from pygame_gui import elements

# Shared runtime state: tracks all active pokemon instances and game constraints.
spawnpoint = (int(window_w * 0.75), int(window_h * 0.95))  # Default spawn location for new pokemon.
pokemon_names = []  # List of all active pokemon names (used for uniqueness validation).
pokemon_group = []  # List containing all active pokemon sprite instances (for rendering/updates).
pokemon_dict = {}  # Lookup dict: {\"name (species)\" -> pokemon_instance} for quick access.
POKEMON_LIMIT = 10  # Maximum concurrent pokemon allowed (spawn disabled at limit).
MAX_NAME_LENGTH = 20  # Character limit for pokemon nicknames.
ONLY_FIRST_STAGE = True  # Spawn pool constraint: if True, only base-stage pokemon spawn.
ENERGY_DONATION_COOLDOWN = 1  # Minimum seconds between consecutive energy donations (per pokemon).

class Skip(Exception):
    """Alternative to a goto-style early exit for intro flow."""
    pass

class LabeledProgressBar(elements.UIProgressBar):
    """UIProgressBar that always displays a label and integer progress values.
    
    Custom progress bar widget that shows:
    - Label text (e.g. \"level\", \"nutrition\")
    - Current and max values as integers (e.g. \"level: 5 / 10\")
    
    Inherits from pygame_gui's UIProgressBar for styling and behavior, but overrides the following methods:
    """

    def __init__(self, *args, label="", maximum_progress=100, **kwargs):
        self.label = label
        super().__init__(*args, **kwargs)
        self.maximum_progress = maximum_progress

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

    def __init__(self):
        super().__init__()

        pokemon_names.append(self.name)

        self.x = spawnpoint[0] - self.img_w // 2
        self.y = spawnpoint[1] - self.img_h
        self.rect = rect.Rect(self.x, self.y, self.img_w, self.img_h)
        self.anchor = self.rect.midbottom
        self.speed_x = 0
        self.speed_y = 0

        self.exact_age = 0  # In seconds with decimals.
        self.age = 0        # In seconds rounded to an integer.
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

    def __set_nutrition(self, value: int):
        self.__nutrition = self.__clamp_percentage(value)

    def __set_energy(self, value: int):
        self.__energy = self.__clamp_percentage(value)

    def __set_happiness(self, value: int):
        self.__happiness = self.__clamp_percentage(value)

    def __set_level(self, value: int):
        self.__level = value

    def __change_nutrition(self, delta: int):
        self.__set_nutrition(self.__nutrition + delta)

    def __change_energy(self, delta: int):
        self.__set_energy(self.__energy + delta)

    def __change_happiness(self, delta: int):
        self.__set_happiness(self.__happiness + delta)

    def __change_level(self, delta: int):
        self.__set_level(self.__level + delta)

    def __clamp_percentage(self, value: int):
        return max(0, min(100, value))
        
    @abstractmethod
    def set_images(self, awake_img_name, sleeping_img_name):
        pass

    def load_images(self, awake_img_name, sleeping_img_name):
        # Load and scale awake sprite.
        self.img = image.load(awake_img_name).convert_alpha()
        self.img = transform.scale(
            self.img,
            (
                int(self.img.get_width() * self.scale_factor),
                int(self.img.get_height() * self.scale_factor),
            ),
        )
        self.orig_image = self.img
        self.img_w = self.img.get_width()
        self.img_h = self.img.get_height()

        # Load and scale sleeping sprite.
        self.img_sleeping = image.load(sleeping_img_name).convert_alpha()
        self.img_sleeping = transform.scale(
            self.img_sleeping,
            (
                int(self.img_sleeping.get_width() * self.sleeping_scale_factor),
                int(self.img_sleeping.get_height() * self.sleeping_scale_factor),
            ),
        )

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

                if ticks_passed % (30 * framerate // self.energy_decay) == 0:
                    old_energy = self.energy
                    self.__change_energy(1)
                    if self.energy > old_energy:
                        self.print_status("", "\x1b[1;32m+1\x1b[0m", "")

                    if self.energy >= 100:
                        self.wake_up()

    def set_mood(self):
        """Update mood based on needs and check for death condition.
        
        Moods: critical -> unsettled -> neutral -> content -> satisfied
        
        Rules:
        - If any need drops to 0 or below, the Pokémon dies immediately.
        - If any need is < 15, mood is critical.
        - If any need is < 30, mood is unsettled.
        - Otherwise, mood depends on average need level.
        
        Returns 'died' if pokemon dies; otherwise returns None.
        """

        self.mood_score = self.nutrition + self.energy + self.happiness
        levels = [self.nutrition, self.energy, self.happiness]
        lowest = min(levels)
        avg = self.mood_score / len(levels)

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
            energy = 25
            if self.energy + energy > 100:
                self.__set_energy(100)
                return self.level_up()
            self.__change_energy(energy)
            self.print_status("", f"\x1b[1;32m+{energy}\x1b[0m", "")

    def sleep(self):
        if self.is_alive:
            self.is_awake = False
            anchor = self.rect.midbottom
            self.img = self.img_sleeping
            self.rect = self.img.get_rect(midbottom=anchor)
            self.x, self.y = self.rect.topleft

    def feed(self):
        meal = randint(5, 10)
        energy_status = ""
        happiness_status = ""
        overload = 0
        # Any overload of feeding points are deducted from energy and happiness.
        if self.nutrition + meal > 100:
            overload = self.nutrition + meal - 100
            self.__change_energy(-overload // 2)
            energy_status = f"\x1b[1;31m-{overload // 2}\x1b[0m"
            self.__change_happiness(-overload // 2)
            happiness_status = f"\x1b[1;31m-{overload // 2}\x1b[0m"
        else:
            self.__change_energy(meal // 2)
            energy_status = f"\x1b[1;32m+{meal // 2}\x1b[0m"

        self.__change_nutrition(meal)
        self.print_status(f"\x1b[1;32m+{meal}\x1b[0m", energy_status, happiness_status)

    def wake_up(self):
        if self.is_alive:
            self.is_awake = True            
            # Keeping the same mid-bottom position.
            anchor = self.rect.midbottom
            self.img = self.orig_image
            self.move_to(anchor)
            self.x, self.y = self.rect.topleft

    def play(self):
        if self.is_alive:
            fun = randint(10, 20)
            energy_status = ""
            nutrition_status = ""
            overload = 0
            # Any overload of playing points are deducted from energy and nutrition.
            if self.happiness + fun > 100:
                overload = self.happiness + fun - 100
                self.__change_energy(-overload // 2)
                self.__change_nutrition(-overload // 2)
                energy_status = f"\x1b[1;31m-{overload // 2}\x1b[0m"
                nutrition_status = f"\x1b[1;31m-{overload // 2}\x1b[0m"

            self.__change_happiness(fun)
            self.print_status(nutrition_status, energy_status, f"\x1b[1;32m+{fun}\x1b[0m")

    def die(self):
        self.__set_nutrition(0)
        self.__set_happiness(0)
        self.__set_energy(0)
        self.is_alive = False
        self.img = gravestone
        self.move_to(self.anchor)
        pokemon_names.remove(self.name)
        pokemon_group.remove(self)
        del pokemon_dict[self.__str__()]
        return "died"

    def move_to(self, bottom_center_pos: tuple[int, int]):
        # Place the pokemon using bottom-center coordinates.
        self.rect = self.img.get_rect(midbottom=bottom_center_pos)
        self.x, self.y = self.rect.topleft
        self.anchor = bottom_center_pos

    def level_up(self):
        """Increment level and trigger evolution or decay reduction.
        
        Evolution takes priority: if level == 11 and evolution is available,
        calls evolve() and returns success message.
        
        Otherwise, if level is divisible by 10, randomly reduces one decay rate
        (nutrition, energy, or happiness) by ~10%, making the Pokémon easier to care for.
        
        Returns: message string describing the level-up effect.
        """
        self.__change_level(1)
        details = ""
        if self.evolve():
            return 'Evolved!'
        # Random decay improvement on milestones (level 10, 20, 30, etc.) if not evolving.
        decays = [('nutrition_decay', "Nutrition decay"),
                    ('energy_decay', "Energy decay"),
                    ('happiness_decay', "Happiness decay")]
        while self.level % 10 == 0 and self.next_stage is None:
            decay_choice = choice(decays)
            self.print_info()
            prev_decay = getattr(self, decay_choice[0])
            setattr(self, decay_choice[0], int(prev_decay // 1.1))
            if prev_decay != getattr(self, decay_choice[0]):
                details = f"\n{decay_choice[1]}: -{int(prev_decay)}/min -> -{int(getattr(self, decay_choice[0]))}/min"
                self.print_info()
                break
            else:
                del decays[decays.index(decay_choice)]
        return f'Leveled Up!{details}'

    def evolve(self):
        """Transform Pokémon instance into its evolved form.
        
        Implements same-instance mutation strategy: the original instance's attributes
        are replaced in-place rather than creating a new instance. This preserves:
        - The pokemon's unique name (nickname)
        - Its position on screen
        - Its history (age, mood history)
        
        Evolution triggers when level == 11 and next_stage is defined (not None).
        
        On evolution:
        - Remove from pokemon_dict and pokemon_group temporarily
        - Call next_stage(self) to mutate species/stage/image attributes
        - Reduce decay rates by ~10% per stage (easier care as Pokémon matures)
        - Re-add to pokemon_dict and pokemon_group to continue tracking
        
        Returns: True if evolution occurred; False if not eligible.
        """
        if self.level == 11 and self.next_stage is not None:
            del pokemon_dict[self.__str__()]
            pokemon_group.remove(self)
            prev_pos = self.anchor
            self.__set_level(1)
            self.next_stage(self)

            self.nutrition_decay = int(self.nutrition_decay / sqrt(self.stage))
            self.energy_decay = int(self.energy_decay / sqrt(self.stage))
            self.happiness_decay = int(self.happiness_decay / sqrt(self.stage))

            self.move_to(prev_pos)
            pokemon_dict[self.__str__()] = self
            pokemon_group.append(self)
            return True
        return False

    def print_info(self):
        print(f"\n\x1b[1;3m{self.name}\x1b[0m\
                \nSpecies: {self.species}\
                \nType: {self.type}\
                \nLevel: {self.level}\
                \nStage: {self.stage if self.stage else 'None'}\
                \nNext stage: {self.next_stage}\
                \nAge: \x1b[1m{self.age}\x1b[0ms\
                \nMood score: \x1b[1m{self.mood_score}\x1b[0m\
                \nMood: {self.curr_mood}\
                \n\nNutrition: \x1b[1m{self.nutrition}\x1b[0m% | ( -{self.nutrition_decay}/min )\
                \nEnergy: \x1b[1m{self.energy}\x1b[0m% | ( -{self.energy_decay}/min )\
                \nHappiness: \x1b[1m{self.happiness}\x1b[0m% | ( -{self.happiness_decay}/min )\n")

    def __str__(self):
        return f"{self.name} ({self.species})"


class FireType(Pokemon):
    """Fire-type pokemon with balanced decay rates.
    
    Characteristics:
    - Moderate nutrition decay (30-35/min)
    - High energy decay (60-70/min) - fire burns energy quickly
    - Low happiness decay (20-25/min) - enthusiastic Pokémon
    
    Energy source: FOSSIL FUEL
    """
    def __init__(self):
        self.nutrition_decay = randint(30, 35) // sqrt(self.stage)
        self.energy_decay = randint(60, 70) // sqrt(self.stage)
        self.happiness_decay = randint(20, 25) // sqrt(self.stage)
        self.type = "Fire"
        self.energy_source = "FOSSIL FUEL"
        super().__init__()


class WaterType(Pokemon):
    """Water-type pokemon with emphasis on nutrition and mood.
    
    Characteristics:
    - High nutrition decay (40-45/min) - water types are hungry
    - Moderate energy decay (40-50/min)
    - High happiness decay (30-35/min) - sensitive to loneliness
    
    Energy source: ELECTROLYTES
    """
    def __init__(self):
        self.nutrition_decay = randint(40, 45) // sqrt(self.stage)
        self.energy_decay = randint(40, 50) // sqrt(self.stage)
        self.happiness_decay = randint(30, 35) // sqrt(self.stage)

        self.type = "Water"
        self.energy_source = "ELECTROLYTES"
        super().__init__()


class ElectricType(Pokemon):
    """Electric-type pokemon with low nutrition but high mood needs.
    
    Characteristics:
    - Low nutrition decay (25-30/min) - efficient eaters
    - Moderate energy decay (50-60/min)
    - High happiness decay (35-40/min) - need frequent interaction
    
    Energy source: BATTERY
    """
    def __init__(self):
        self.nutrition_decay = randint(25, 30) // sqrt(self.stage)
        self.energy_decay = randint(50, 60) // sqrt(self.stage)
        self.happiness_decay = randint(35, 40) // sqrt(self.stage)

        self.type = "Electric"
        self.energy_source = "BATTERY"
        super().__init__()


class RockType(Pokemon):
    """Rock-type pokemon with balanced but high overall decay.
    
    Characteristics:
    - Moderate nutrition decay (30-35/min)
    - High energy decay (55-65/min) - heavy and tiring to move
    - Moderate happiness decay (25-30/min)
    
    Energy source: CRYSTAL
    """
    def __init__(self):
        self.nutrition_decay = randint(30, 35) // sqrt(self.stage)
        self.energy_decay = randint(55, 65) // sqrt(self.stage)
        self.happiness_decay = randint(25, 30) // sqrt(self.stage)

        self.type = "Rock"
        self.energy_source = "CRYSTAL"
        super().__init__()


########################################
# SPECIES DEFINITIONS: 4 types × 3 species families, with 3 or 2
# evolution stages, totaling in 32 different Pokémon.
#
# Evolution Chain Pattern:
# - Stage 1: constructor takes name string, creates new instance
# - Stage 2: constructor takes name string OR instance from stage 1
# - Stage 3: constructor takes name string OR instance from stage 1 or 2
#
# During evolution, 'self.next_stage(self)' is called to mutate the instance.
# The 'isinstance()' call determines whether to initialize a new Pokémon, or update the existing one.
# The instance type remains the same after evolution, but is identified as a different species with 'self.species'.

# Fire-type species.

class Charmander(FireType):
    def __init__(self, name):
        self.name = name
        self.species = "Charmander"
        self.scale_factor = 0.2
        self.sleeping_scale_factor = 0.2
        self.set_images(CHARMANDER_IMG, CHARMANDER_SLEEPING)
        self.stage = 1
        self.next_stage = Charmeleon
        super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

class Charmeleon(FireType):
    def __init__(self, name_or_instance: str | Charmander):
        if isinstance(name_or_instance, Charmander):
            self = name_or_instance
        self.species = "Charmeleon"
        self.scale_factor = 0.32
        self.sleeping_scale_factor = 0.28
        self.set_images(CHARMELEON_IMG, CHARMELEON_SLEEPING)
        self.stage = 2
        self.next_stage = Charizard
        if isinstance(name_or_instance, str):
            self.name = name_or_instance
            super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

class Charizard(FireType):
    def __init__(self, name_or_instance: str | Charmander| Charmeleon):
        if isinstance(name_or_instance, Charmeleon) or isinstance(name_or_instance, Charmander):
            self = name_or_instance
        self.species = "Charizard"
        self.scale_factor = 0.65
        self.sleeping_scale_factor = 0.5
        self.set_images(CHARIZARD_IMG, CHARIZARD_SLEEPING)
        self.stage = 3
        self.next_stage = None
        if isinstance(name_or_instance, str):
            self.name = name_or_instance
            super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

##########

class Growlithe(FireType):
    def __init__(self, name):
        self.name = name
        self.species = "Growlithe"
        self.scale_factor = 0.2
        self.sleeping_scale_factor = 0.2
        self.set_images(GROWLITHE_IMG, GROWLITHE_SLEEPING)
        self.stage = 1
        self.next_stage = Arcanine
        super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

class Arcanine(FireType):
    def __init__(self, name_or_instance: str | Growlithe):
        if isinstance(name_or_instance, Growlithe):
            self = name_or_instance
        self.species = "Arcanine"
        self.scale_factor = 0.4
        self.sleeping_scale_factor = 0.3
        self.set_images(ARCANINE_IMG, ARCANINE_SLEEPING)
        self.stage = 2
        self.next_stage = None
        if isinstance(name_or_instance, str):
            self.name = name_or_instance
            super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

##########

class Vulpix(FireType):
    def __init__(self, name):
        self.name = name
        self.species = "Vulpix"
        self.scale_factor = 0.25
        self.sleeping_scale_factor = 0.25
        self.set_images(VULPIX_IMG, VULPIX_SLEEPING)
        self.stage = 1
        self.next_stage = Ninetales
        super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

class Ninetales(FireType):
    def __init__(self, name_or_instance: str | Vulpix):
        if isinstance(name_or_instance, Vulpix):
            self = name_or_instance
        self.species = "Ninetales"
        self.scale_factor = 0.4
        self.sleeping_scale_factor = 0.4
        self.set_images(NINETALES_IMG, NINETALES_SLEEPING)
        self.stage = 2
        self.next_stage = None
        if isinstance(name_or_instance, str):
            self.name = name_or_instance
            super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

####################

# Water-type species.

class Squirtle(WaterType):
    def __init__(self, name: str):
        self.name = name
        self.species = "Squirtle"
        self.scale_factor = 0.2
        self.sleeping_scale_factor = 0.2
        self.set_images(SQUIRTLE_IMG, SQUIRTLE_SLEEPING)
        self.stage = 1
        self.next_stage = Wartortle
        super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

class Wartortle(WaterType):
    def __init__(self, name_or_instance: str | Squirtle):
        if isinstance(name_or_instance, Squirtle):
            self = name_or_instance
        self.species = "Wartortle"
        self.scale_factor = 0.3
        self.sleeping_scale_factor = 0.3
        self.set_images(WARTORTLE_IMG, WARTORTLE_SLEEPING)
        self.stage = 2
        self.next_stage = Blastoise
        if isinstance(name_or_instance, str):
            self.name = name_or_instance
            super().__init__()  # Also calls 'self.load_images()'.

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

class Blastoise(WaterType):
    def __init__(self, name_or_instance: str | Squirtle | Wartortle):
        if isinstance(name_or_instance, Wartortle | Squirtle):
            self = name_or_instance
        self.species = "Blastoise"
        self.scale_factor = 0.42
        self.sleeping_scale_factor = 0.42
        self.set_images(BLASTOISE_IMG, BLASTOISE_SLEEPING)
        self.stage = 3
        self.next_stage = None
        if isinstance(name_or_instance, str):
            self.name = name_or_instance
            super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

##########

class Psyduck(WaterType):
    def __init__(self, name: str):
        self.name = name
        self.species = "Psyduck"
        self.scale_factor = 0.2
        self.sleeping_scale_factor = 0.28
        self.set_images(PSYDUCK_IMG, PSYDUCK_SLEEPING)
        self.stage = 1
        self.next_stage = Golduck
        super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

class Golduck(WaterType):
    def __init__(self, name_or_instance: str | Psyduck):
        if isinstance(name_or_instance, Psyduck):
            self = name_or_instance
        self.species = "Golduck"
        self.scale_factor = 0.4
        self.sleeping_scale_factor = 0.3
        self.set_images(GOLDUCK_IMG, GOLDUCK_SLEEPING)
        self.stage = 2
        self.next_stage = None
        if isinstance(name_or_instance, str):
            self.name = name_or_instance
            super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

##########

class Magikarp(WaterType):
    def __init__(self, name: str):
        self.name = name
        self.species = "Magikarp"
        self.scale_factor = 0.2
        self.sleeping_scale_factor = 0.2
        self.set_images(MAGIKARP_IMG, MAGIKARP_SLEEPING)
        self.stage = 1
        self.next_stage = Gyarados
        super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

class Gyarados(WaterType):
    def __init__(self, name_or_instance: str | Magikarp):
        if isinstance(name_or_instance, Magikarp):
            self = name_or_instance
        self.species = "Gyarados"
        self.scale_factor = 0.6
        self.sleeping_scale_factor = 0.6
        self.set_images(GYARADOS_IMG, GYARADOS_SLEEPING)
        self.stage = 2
        self.next_stage = None
        if isinstance(name_or_instance, str):
            self.name = name_or_instance
            super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

####################

# Electric-type species.

class Pichu(ElectricType):
    def __init__(self, name):
        self.name = name
        self.species = "Pichu"
        self.scale_factor = 0.2
        self.sleeping_scale_factor = 0.2
        self.set_images(PICHU_IMG, PICHU_SLEEPING)
        self.stage = 1
        self.next_stage = Pikachu
        super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

class Pikachu(ElectricType):
    def __init__(self, name_or_instance: str | Pichu):
        if isinstance(name_or_instance, Pichu):
            self = name_or_instance
        self.species = "Pikachu"
        self.scale_factor = 0.25
        self.sleeping_scale_factor = 0.25
        self.set_images(PIKACHU_IMG, PIKACHU_SLEEPING)
        self.stage = 2
        self.next_stage = Raichu
        if isinstance(name_or_instance, str):
            self.name = name_or_instance
            super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

class Raichu(ElectricType):
    def __init__(self, name_or_instance: str | Pichu | Pikachu):
        if isinstance(name_or_instance, Pikachu) or isinstance(name_or_instance, Pichu):
            self = name_or_instance
        self.species = "Raichu"
        self.scale_factor = 0.3
        self.sleeping_scale_factor = 0.28
        self.set_images(RAICHU_IMG, RAICHU_SLEEPING)
        self.stage = 3
        self.next_stage = None
        if isinstance(name_or_instance, str):
            self.name = name_or_instance
            super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

##########

class Magnemite(ElectricType):
    def __init__(self, name):
        self.name = name
        self.species = "Magnemite"
        self.scale_factor = 0.25
        self.sleeping_scale_factor = 0.25
        self.set_images(MAGNEMITE_IMG, MAGNEMITE_SLEEPING)
        self.stage = 1
        self.next_stage = Magneton
        super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

class Magneton(ElectricType):
    def __init__(self, name_or_instance: str | Magnemite):
        if isinstance(name_or_instance, Magnemite):
            self = name_or_instance
        self.species = "Magneton"
        self.scale_factor = 0.4
        self.sleeping_scale_factor = 0.4
        self.set_images(MAGNETON_IMG, MAGNETON_SLEEPING)
        self.stage = 2
        self.next_stage = Magnezone
        if isinstance(name_or_instance, str):
            self.name = name_or_instance
            super().__init__()
                                
    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

class Magnezone(ElectricType):
    def __init__(self, name_or_instance: str | Magnemite | Magneton):
        if isinstance(name_or_instance, Magneton) or isinstance(name_or_instance, Magnemite):
            self = name_or_instance
        self.species = "Magnezone"
        self.scale_factor = 0.5
        self.sleeping_scale_factor = 0.5
        self.set_images(MAGNEZONE_IMG, MAGNEZONE_SLEEPING)
        self.stage = 3
        self.next_stage = None
        if isinstance(name_or_instance, str):
            self.name = name_or_instance
            super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

##########

class Elekid(ElectricType):
    def __init__(self, name):
        self.name = name
        self.species = "Elekid"
        self.scale_factor = 0.3
        self.sleeping_scale_factor = 0.2
        self.set_images(ELEKID_IMG, ELEKID_SLEEPING)
        self.stage = 1
        self.next_stage = Electabuzz
        super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

class Electabuzz(ElectricType):
    def __init__(self, name_or_instance: str | Elekid):
        if isinstance(name_or_instance, Elekid):
            self = name_or_instance
        self.species = "Electabuzz"
        self.scale_factor = 0.4
        self.sleeping_scale_factor = 0.35
        self.set_images(ELECTABUZZ_IMG, ELECTABUZZ_SLEEPING)
        self.stage = 2
        self.next_stage = Electivire
        if isinstance(name_or_instance, str):
            self.name = name_or_instance
            super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

class Electivire(ElectricType):
    def __init__(self, name_or_instance: str | Elekid | Electabuzz):
        if isinstance(name_or_instance, Electabuzz) or isinstance(name_or_instance, Elekid):
            self = name_or_instance
        self.species = "Electivire"
        self.scale_factor = 0.5
        self.sleeping_scale_factor = 0.45
        self.set_images(ELECTIVIRE_IMG, ELECTIVIRE_SLEEPING)
        self.stage = 3
        self.next_stage = None
        if isinstance(name_or_instance, str):
            self.name = name_or_instance
            super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)


####################


# Rock-type species.

class Geodude(RockType):
    def __init__(self, name: str):
        self.name = name
        self.species = "Geodude"
        self.scale_factor = 0.45
        self.sleeping_scale_factor = 0.28
        self.set_images(GEODUDE_IMG, GEODUDE_SLEEPING)
        self.stage = 1
        self.next_stage = Graveler
        super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

class Graveler(RockType):
    def __init__(self, name_or_instance: str | Geodude):
        if isinstance(name_or_instance, Geodude):
            self = name_or_instance
        self.species = "Graveler"
        self.scale_factor = 0.45
        self.sleeping_scale_factor = 0.55
        self.set_images(GRAVELER_IMG, GRAVELER_SLEEPING)
        self.stage = 2
        self.next_stage = Golem
        if isinstance(name_or_instance, str):
            self.name = name_or_instance
            super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

class Golem(RockType):
    def __init__(self, name_or_instance: str | Geodude | Graveler):
        if isinstance(name_or_instance, Graveler) or isinstance(name_or_instance, Geodude):
            self = name_or_instance
        self.species = "Golem"
        self.scale_factor = 0.5
        self.sleeping_scale_factor = 0.48
        self.set_images(GOLEM_IMG, GOLEM_SLEEPING)
        self.stage = 3
        self.next_stage = None
        if isinstance(name_or_instance, str):
            self.name = name_or_instance
            super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

##########

class Rhyhorn(RockType):
    def __init__(self, name):
        self.name = name
        self.species = "Rhyhorn"
        self.scale_factor = 0.25
        self.sleeping_scale_factor = 0.25
        self.set_images(RHYHORN_IMG, RHYHORN_SLEEPING)
        self.stage = 1
        self.next_stage = Rhydon
        super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

class Rhydon(RockType):
    def __init__(self, name_or_instance: str | Rhyhorn):
        if isinstance(name_or_instance, Rhyhorn):
            self = name_or_instance
        self.species = "Rhydon"
        self.scale_factor = 0.4
        self.sleeping_scale_factor = 0.4
        self.set_images(RHYDON_IMG, RHYDON_SLEEPING)
        self.stage = 2
        self.next_stage = Rhyperior
        if isinstance(name_or_instance, str):
            self.name = name_or_instance
            super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

class Rhyperior(RockType):
    def __init__(self, name_or_instance: str | Rhyhorn | Rhydon):
        if isinstance(name_or_instance, Rhydon) or isinstance(name_or_instance, Rhyhorn):
            self = name_or_instance
        self.species = "Rhyperior"
        self.scale_factor = 0.7
        self.sleeping_scale_factor = 0.4
        self.set_images(RHYPERIOR_IMG, RHYPERIOR_SLEEPING)
        self.stage = 3
        self.next_stage = None
        if isinstance(name_or_instance, str):
            self.name = name_or_instance
            super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

##########

class Larvitar(RockType):
    def __init__(self, name):
        self.name = name
        self.species = "Larvitar"
        self.scale_factor = 0.2
        self.sleeping_scale_factor = 0.21
        self.set_images(LARVITAR_IMG, LARVITAR_SLEEPING)
        self.stage = 1
        self.next_stage = Pupitar
        super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

class Pupitar(RockType):
    def __init__(self, name_or_instance: str | Larvitar):
        if isinstance(name_or_instance, Larvitar):
            self = name_or_instance
        self.species = "Pupitar"
        self.scale_factor = 0.3
        self.sleeping_scale_factor = 0.3
        self.set_images(PUPITAR_IMG, PUPITAR_SLEEPING)
        self.stage = 2
        self.next_stage = Tyranitar
        if isinstance(name_or_instance, str):
            self.name = name_or_instance
            super().__init__()
    
    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)

class Tyranitar(RockType):
    def __init__(self, name_or_instance: str | Larvitar | Pupitar):
        if isinstance(name_or_instance, Pupitar) or isinstance(name_or_instance, Larvitar):
            self = name_or_instance
        self.species = "Tyranitar"
        self.scale_factor = 0.48
        self.sleeping_scale_factor = 0.48
        self.set_images(TYRANITAR_IMG, TYRANITAR_SLEEPING)
        self.stage = 3
        self.next_stage = None
        if isinstance(name_or_instance, str):
            self.name = name_or_instance
            super().__init__()

    def set_images(self, awake_img_name, sleeping_img_name):
        super().load_images(awake_img_name, sleeping_img_name)