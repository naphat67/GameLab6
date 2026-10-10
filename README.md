# Astra Character Lab

A small Godot 4 project for the character design and animation exercise. It opens directly into a playable 3D training scene.

## What is included

- **Astra MK-06**, a custom low-poly humanoid assembled from meshes in Godot, with a helmet, luminous chest core, armor, boots, and a training blade.
- A `CharacterBody3D` player with idle, locomotion, melee slash, and shooter aim animations in an `AnimationPlayer` library.
- A training arena with three practice units, two-hit targets, a status HUD, and a reset control.
- The Mixamo BoneMap and the Melee/Shooter animation libraries named in the assignment, kept under `assets/` for use with compatible Mixamo-rigged models.
- A three-view character concept sheet at `art/astra_character_sheet.png`.
- A web export at `exports/web/index.html`.

## Open and play

Open this folder in Godot 4.7.2 or later, then run the main scene.

- **WASD** or **arrow keys**: move
- **Space** or **Enter**: slash at the closest unit in front of Astra
- **R**: restore all practice units

Each unit takes two hits. Walk toward a unit and face it before attacking.

## Web export

The project includes a `Web` export preset. Install the matching Godot export templates, then export the preset to `exports/web/index.html`. The included build is single-threaded for straightforward static hosting.

## Animation library attribution

`MeleeLib.res`, `ShooterLib.res`, and `Mixamo BoneMap.tres` are from [catprisbrey/Godot4-OpenAnimationLibraries](https://github.com/catprisbrey/Godot4-OpenAnimationLibraries), the source requested by the assignment. The libraries are intended for compatible skeletons; this demo's custom-built operator uses its own scene-specific clips. Check the upstream repository for current usage and licensing details before redistributing those resources separately.

## Project files

- `scenes/arena.tscn` — demo scene entry point
- `scripts/arena.gd` — arena, character, controls, animations, and HUD
- `assets/bone_maps/` — Mixamo bone map
- `assets/libraries/Humanoid/` — melee and shooter libraries
- `export_presets.cfg` — web export configuration
