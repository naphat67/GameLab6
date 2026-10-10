# Astra Character Lab

A small Godot 4 project for the character design and animation exercise. It opens directly into a playable 3D training scene.

## What is included

- **Astra MK-06**, a custom low-poly humanoid modeled and rigged in Blender, with a helmet, luminous chest core, armor, boots, and a training blade. The editable `.blend` source is included.
- A `CharacterBody3D` player that loads the rigged GLB and its idle, locomotion, melee slash, and shooter aim actions in an `AnimationPlayer`.
- A training arena with three practice units, two-hit targets, a status HUD, and a reset control.
- The Mixamo BoneMap and both Melee/Shooter libraries named in the assignment. The demo plays the Blender-authored actions; the supplied libraries remain available for a compatible Godot Humanoid-profile skeleton.
- A three-view character concept sheet and a Blender render at `art/astra_character_sheet.png` and `art/astra_blender_render.png`.
- The Blender source builder at `art/create_astra_blender.py` (run it with Blender 5.2 to regenerate the `.blend`, GLB, and render).
- A web export at `exports/web/index.html`.

## Open and play

Open this folder in Godot 4.7.2 or later, then run the main scene.

- **WASD** or **arrow keys**: move
- **Space** or **Enter**: slash at the closest unit in front of Astra
- **R**: restore all practice units
- Use the on-screen **Pose Library** buttons to play Stand, Walk, Sit, Lie Down, Jump, and Slash. Sit and Lie Down hold until another pose is selected.

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
- `assets/characters/Astra_MK06.glb` — rigged character used in the demo
- `assets/characters/source_blender/Astra_MK06.blend` — editable Blender source (ignored by Godot's importer)
- `export_presets.cfg` — web export configuration

## Play in your browser

GitHub Pages serves the Godot Web export from the docs folder. Once Pages finishes publishing, open [Astra Character Lab](https://naphat67.github.io/GameLab6/). The matching export files are kept in the exports/web folder for Godot project use.
