# INF-1400 Mandatory Assignment 2

Pokemon Care Simulator built with Python, pygame, and pygame_gui.

Full assignment brief: [assignment_instruction/assignment.md](assignment_instruction/assignment.md)

## Project Layout

This repository currently contains two implementations:

- Base-case version: [PokGotchi](PokGotchi)
- Extension version (Evolution): [PokGotchi2](PokGotchi2)

## UML Class Diagrams

- Base-case UML: [UML_BaseCase.mmd](UML_BaseCase.mmd)
- Evolution extension UML: [UML_Extension_Evolution.mmd](UML_Extension_Evolution.mmd)

Both diagrams are Mermaid class diagrams.

## Requirements

- Python 3.12+
- Dependencies in [requirements.txt](requirements.txt)

## Setup

1. Open terminal in _PokGotchi_ or _PokGotchi2_.
2. Create and activate a virtual environment:

### MacOS/Linux
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
### Windows
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\\requirements.txt
```

Important dependency note:
- Install from [requirements.txt](requirements.txt) only.
- Do not install `pygame` separately alongside `pygame_gui`, as this may introduce a runtime conflict depending on install order.

## Run

```bash
python main.py
```

## Features Summary

Base-case ([PokGotchi](PokGotchi)):
- Multiple types and species
- Unique nickname and age
- Need decay (nutrition, energy, happiness)
- Mood system
- Death at need = 0
- GUI actions and selection menu

Evolution extension ([PokGotchi2](PokGotchi2)):
- Adds evolution chains (for all included families)
- Adds level progression and evolve trigger in domain model
- Updates species/stage/visuals when evolve logic is triggered
- Uses ABC contract in the extension model with abstract `set_images(...)` in [PokGotchi2/classes.py](PokGotchi2/classes.py)

## Requirement Self-Check

### Domain model requirements (base-case folder: [PokGotchi](PokGotchi))

1. Different types (>=3): pass (Fire, Water, Electric, Rock)
2. Different species (>=3): pass
3. Unique identifier (nickname + age): pass
4. Needs 0-100 with decay variation: pass
5. Needs increase via user actions: pass
6. Mood from all three needs: pass
7. Death when any need hits 0, no revive: pass
8. No evolution in base-case: pass

### Simulation/UI requirements (base-case folder: [PokGotchi](PokGotchi))

1. Runnable [main.py](PokGotchi/main.py): pass
2. Visualize current pokemon: pass (active sprite + selection panel previews)
3. Display state (type/species/name/age/needs/mood): pass
4. Max concurrent pokemon: pass (`POKEMON_LIMIT`)
5. Visual death indication: pass (gravestone image)
6. Add pokemon via UI: pass
7. Dispatch need-affecting actions: pass
8. Actions through buttons/keyboard: pass (buttons + ESC)

### Extension requirements (evolution folder: [PokGotchi2](PokGotchi2))

1. Evolution chains implemented: pass
2. Conditions for evolution implemented: pass (level threshold logic)
3. Effects of evolution (species/stage/visual changes): pass
4. Design decision about instance lifecycle: pass (same-instance mutation strategy)
5. Every pokemon starts at base stage: pass (configurable via `ONLY_FIRST_STAGE` flag in [PokGotchi2/classes.py](PokGotchi2/classes.py))

**Configuration note:** By default, `ONLY_FIRST_STAGE = True` ensures only base-stage Pokémon spawn when clicking "New". 
Set `ONLY_FIRST_STAGE = False` to allow any evolution stage to spawn (for testing evolved forms).

## Notes for TA

- Base-case inspection target: [PokGotchi](PokGotchi)
- Extension inspection target (Evolution): [PokGotchi2](PokGotchi2)
- Evolution behavior is primarily implemented in [PokGotchi2/classes.py](PokGotchi2/classes.py) (`level_up()` and `evolve()`).
- Current ABC strategy in extension: concrete constructors (`__init__`) plus required abstract `set_images(...)` implementation per species.
