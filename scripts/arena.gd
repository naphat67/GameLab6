extends Node3D

const PLAYER_SPEED := 4.1
const SWING_DURATION := 0.42

var player: CharacterBody3D
var rig: Node3D
var animation_player: AnimationPlayer
var camera: Camera3D
var skeleton: Skeleton3D
var swing_time := 0.0
var attack_cooldown := 0.0
var action_mode := "Idle"
var action_time := 0.0
var walk_button_active := false
var action_tween: Tween
var target_nodes: Array[Node3D] = []
var target_hp: Array[int] = []
var hit_count := 0
var status_label: Label
var hp_label: Label
var hint_label: Label
var action_label: Label

func _ready() -> void:
	_ready_input_map()
	_build_arena()
	_build_player()
	_build_targets()
	_build_camera()
	_build_hud()
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE


func _process(delta: float) -> void:
	attack_cooldown = maxf(0.0, attack_cooldown - delta)
	if swing_time > 0.0:
		swing_time = maxf(0.0, swing_time - delta)
	if action_mode == "Jump":
		action_time = maxf(0.0, action_time - delta)
		if action_time <= 0.0:
			_set_action("Idle")
	elif action_mode == "Walk":
		if animation_player.current_animation != "Locomotion":
			animation_player.play("Locomotion")
		var moving := Vector2(Input.get_action_strength("move_right") - Input.get_action_strength("move_left"), Input.get_action_strength("move_back") - Input.get_action_strength("move_forward")).length() > 0.1
		if not moving and not walk_button_active:
			_set_action("Idle")
	elif action_mode == "Slash":
		if swing_time <= 0.0:
			_set_action("Idle")
	elif action_mode == "Idle":
		var moving := Vector2(Input.get_action_strength("move_right") - Input.get_action_strength("move_left"), Input.get_action_strength("move_back") - Input.get_action_strength("move_forward")).length() > 0.1
		var desired_animation := "Locomotion" if moving else "Idle"
		if animation_player.current_animation != desired_animation:
			animation_player.play(desired_animation)
		if moving:
			action_mode = "Walk"
			walk_button_active = false
	if Input.is_action_just_pressed("attack") and attack_cooldown <= 0.0:
		_start_attack()
	_update_hud()


func _physics_process(_delta: float) -> void:
	var input_dir := Vector3(
		Input.get_action_strength("move_right") - Input.get_action_strength("move_left"),
		0.0,
		Input.get_action_strength("move_back") - Input.get_action_strength("move_forward")
	)
	if input_dir.length() > 1.0:
		input_dir = input_dir.normalized()
	if action_mode == "Sit" or action_mode == "Lie":
		if input_dir.length() > 0.08:
			_set_action("Walk")
		else:
			player.velocity = Vector3.ZERO
			return
	player.velocity.x = input_dir.x * PLAYER_SPEED
	player.velocity.z = input_dir.z * PLAYER_SPEED
	if input_dir.length() > 0.08:
		rig.rotation.y = lerp_angle(rig.rotation.y, atan2(input_dir.x, -input_dir.z), 0.18)
	player.move_and_slide()
	player.global_position.x = clampf(player.global_position.x, -8.0, 8.0)
	player.global_position.z = clampf(player.global_position.z, -6.0, 6.0)


func _unhandled_key_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	if event is InputEventKey and event.pressed and event.keycode == KEY_R:
		_reset_targets()


func _build_arena() -> void:
	var world := WorldEnvironment.new()
	var environment := Environment.new()
	environment.background_mode = Environment.BG_SKY
	var sky := Sky.new()
	var sky_mat := ProceduralSkyMaterial.new()
	sky_mat.sky_top_color = Color("111b36")
	sky_mat.sky_horizon_color = Color("334967")
	sky_mat.ground_bottom_color = Color("10182a")
	sky_mat.ground_horizon_color = Color("334967")
	sky.sky_material = sky_mat
	environment.sky = sky
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color("93a9c8")
	environment.ambient_light_energy = 0.6
	world.environment = environment
	add_child(world)

	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-44, -28, 0)
	sun.light_color = Color("d6e5ff")
	sun.light_energy = 1.5
	sun.shadow_enabled = true
	add_child(sun)

	var key := OmniLight3D.new()
	key.position = Vector3(0.0, 3.2, -2.0)
	key.light_color = Color("5de7dc")
	key.light_energy = 1.6
	key.omni_range = 8.0
	add_child(key)

	var ground := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(30.0, 30.0)
	ground.mesh = plane
	ground.material_override = _mat(Color("18243b"), 0.15, 0.7)
	ground.position.y = -0.04
	add_child(ground)

	for i in range(-7, 8):
		var line := MeshInstance3D.new()
		var mesh := BoxMesh.new()
		mesh.size = Vector3(0.018, 0.009, 30.0)
		line.mesh = mesh
		line.material_override = _mat(Color("37506b"), 0.18, 0.35)
		line.position = Vector3(float(i) * 2.0, -0.025, 0.0)
		add_child(line)
		var cross := MeshInstance3D.new()
		var cross_mesh := BoxMesh.new()
		cross_mesh.size = Vector3(30.0, 0.009, 0.018)
		cross.mesh = cross_mesh
		cross.material_override = line.material_override
		cross.position = Vector3(0.0, -0.024, float(i) * 2.0)
		add_child(cross)

	var dais := MeshInstance3D.new()
	var dais_mesh := CylinderMesh.new()
	dais_mesh.top_radius = 1.9
	dais_mesh.bottom_radius = 2.05
	dais_mesh.height = 0.18
	dais.mesh = dais_mesh
	dais.position = Vector3(0.0, 0.03, 0.0)
	dais.material_override = _mat(Color("243854"), 0.4, 0.38)
	add_child(dais)
	var ring := MeshInstance3D.new()
	var ring_mesh := TorusMesh.new()
	ring_mesh.inner_radius = 1.86
	ring_mesh.outer_radius = 1.9
	ring.mesh = ring_mesh
	ring.position.y = 0.13
	ring.material_override = _mat(Color("69dcd4"), 0.28, 0.34, true)
	add_child(ring)
	_add_text_3d("ASTRA // TRAINING DECK", Vector3(-5.0, 0.03, -4.8), 0.2, Color("84a6c4"))


func _build_player() -> void:
	_build_player_from_blender_model()


func _build_player_from_blender_model() -> void:
	player = CharacterBody3D.new()
	player.name = "AstraPlayer"
	player.position = Vector3(0.0, 0.1, 2.0)
	add_child(player)
	var collision := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.4
	capsule.height = 1.8
	collision.shape = capsule
	collision.position.y = 0.9
	player.add_child(collision)

	rig = Node3D.new()
	rig.name = "Astra_Rig"
	player.add_child(rig)
	var model_scene := load("res://assets/characters/Astra_MK06.glb") as PackedScene
	if model_scene == null:
		push_error("Could not load the imported Astra GLB scene.")
		return
	var character_model := model_scene.instantiate()
	character_model.name = "AstraCharacter"
	rig.add_child(character_model)
	animation_player = _find_animation_player(character_model)
	skeleton = _find_skeleton(character_model)
	if animation_player == null:
		push_error("The Astra character is missing its AnimationPlayer.")
	else:
		_create_pose_animations()
		animation_player.play("Idle")
	_add_ring(rig, Vector3(0.0, 0.08, 0.0), 0.7, 0.75, Color("b4dfdf", 0.36))


func _find_animation_player(node: Node) -> AnimationPlayer:
	if node is AnimationPlayer:
		return node
	for child in node.get_children():
		var found := _find_animation_player(child)
		if found != null:
			return found
	return null


func _find_skeleton(node: Node) -> Skeleton3D:
	if node is Skeleton3D:
		return node
	for child in node.get_children():
		var found := _find_skeleton(child)
		if found != null:
			return found
	return null


func _create_pose_animations() -> void:
	if animation_player == null or skeleton == null:
		return
	animation_player.get_animation("Locomotion").loop_mode = Animation.LOOP_LINEAR
	var library := animation_player.get_animation_library("")
	var sit := _build_pose_animation("Pose_Sit", {
		"mixamorig_LeftUpLeg": Vector3(-0.95, 0.0, 0.0),
		"mixamorig_RightUpLeg": Vector3(-0.95, 0.0, 0.0),
		"mixamorig_LeftLeg": Vector3(1.45, 0.0, 0.0),
		"mixamorig_RightLeg": Vector3(1.45, 0.0, 0.0),
		"mixamorig_LeftArm": Vector3(-0.18, 0.0, -0.18),
		"mixamorig_RightArm": Vector3(-0.18, 0.0, 0.18),
		"mixamorig_LeftForeArm": Vector3(-0.55, 0.0, 0.0),
		"mixamorig_RightForeArm": Vector3(-0.55, 0.0, 0.0),
		"mixamorig_Spine": Vector3(0.12, 0.0, 0.0),
	}, 0.65)
	var lie := _build_pose_animation("Pose_Lie", {
		"mixamorig_Hips": Vector3(0.0, 0.0, 1.48),
		"mixamorig_LeftArm": Vector3(0.0, 0.0, -0.62),
		"mixamorig_RightArm": Vector3(0.0, 0.0, 0.62),
		"mixamorig_LeftUpLeg": Vector3(0.15, 0.0, -0.12),
		"mixamorig_RightUpLeg": Vector3(-0.15, 0.0, 0.12),
	}, 0.65)
	var jump := _build_pose_animation("Pose_Jump", {
		"mixamorig_LeftUpLeg": Vector3(-0.42, 0.0, 0.0),
		"mixamorig_RightUpLeg": Vector3(-0.42, 0.0, 0.0),
		"mixamorig_LeftLeg": Vector3(0.72, 0.0, 0.0),
		"mixamorig_RightLeg": Vector3(0.72, 0.0, 0.0),
		"mixamorig_LeftArm": Vector3(-1.7, 0.0, -0.25),
		"mixamorig_RightArm": Vector3(-1.7, 0.0, 0.25),
	}, 0.72, true)
	if library != null:
		library.add_animation("Pose_Sit", sit)
		library.add_animation("Pose_Lie", lie)
		library.add_animation("Pose_Jump", jump)


func _build_pose_animation(animation_name: String, offsets: Dictionary, duration: float, reset_at_end := false) -> Animation:
	var animation := Animation.new()
	animation.resource_name = animation_name
	animation.length = duration
	for bone_index in range(skeleton.get_bone_count()):
		var bone_name := skeleton.get_bone_name(bone_index)
		var track := animation.add_track(Animation.TYPE_ROTATION_3D)
		animation.track_set_path(track, NodePath("Astra_Rig_MixamoStyle/Skeleton3D:" + bone_name))
		var target := Quaternion.IDENTITY
		if offsets.has(bone_name):
			target = Quaternion.from_euler(offsets[bone_name])
		animation.track_insert_key(track, 0.0, Quaternion.IDENTITY)
		animation.track_insert_key(track, duration * 0.65, target)
		animation.track_insert_key(track, duration, Quaternion.IDENTITY if reset_at_end else target)
	return animation


func _build_targets() -> void:
	for i in range(3):
		var target := Node3D.new()
		target.name = "PracticeTarget_%02d" % (i + 1)
		target.position = Vector3(-4.8 + float(i) * 4.8, 0.0, -3.7)
		add_child(target)
		_add_cylinder(target, "Stand", Vector3(0.0, 0.63, 0.0), 0.16, 1.26, Color("17243b"))
		_add_sphere(target, "Core", Vector3(0.0, 1.44, 0.0), Vector3(0.43, 0.48, 0.38), Color("725d9e"))
		_add_box(target, "Eye", Vector3(0.0, 1.47, -0.37), Vector3(0.26, 0.07, 0.045), Color("ffcf89"), 0.35, true)
		_add_ring(target, Vector3(0.0, 1.45, 0.0), 0.48, 0.52, Color("a891ff"))
		_add_text_3d("UNIT 0%d" % (i + 1), target.position + Vector3(-0.45, 2.1, 0.0), 0.13, Color("aabbd4"))
		target_nodes.append(target)
		target_hp.append(2)
		
	var start_marker := MeshInstance3D.new()
	var marker_mesh := CylinderMesh.new()
	marker_mesh.top_radius = 0.49
	marker_mesh.bottom_radius = 0.49
	marker_mesh.height = 0.015
	start_marker.mesh = marker_mesh
	start_marker.position = Vector3(0.0, 0.14, 2.0)
	start_marker.material_override = _mat(Color("67dacf", 0.34), 0.1, 0.38, true)
	add_child(start_marker)


func _build_camera() -> void:
	camera = Camera3D.new()
	camera.name = "DemoCamera"
	camera.position = Vector3(7.6, 7.1, 11.2)
	camera.fov = 43.0
	camera.current = true
	add_child(camera)
	camera.look_at(Vector3(0.0, 1.0, -0.35), Vector3.UP)


func _build_hud() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var root := Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	layer.add_child(root)

	var title := Label.new()
	title.text = "A S T R A  /  CHARACTER LAB"
	title.position = Vector2(36, 26)
	title.add_theme_font_size_override("font_size", 20)
	title.add_theme_color_override("font_color", Color("ecf7ff"))
	root.add_child(title)
	var sub := Label.new()
	sub.text = "HUMANOID RIG  •  MELEE LIBRARY  •  TRAINING BUILD"
	sub.position = Vector2(38, 57)
	sub.add_theme_font_size_override("font_size", 11)
	sub.add_theme_color_override("font_color", Color("7f9ab7"))
	root.add_child(sub)

	var panel := PanelContainer.new()
	panel.position = Vector2(32, 110)
	panel.custom_minimum_size = Vector2(252, 116)
	panel.add_theme_stylebox_override("panel", _panel_style(Color("0c1525", 0.88), Color("35516c")))
	root.add_child(panel)
	var stats := VBoxContainer.new()
	stats.add_theme_constant_override("separation", 9)
	panel.add_child(stats)
	var tag := Label.new()
	tag.text = "OPERATOR PROFILE"
	tag.add_theme_font_size_override("font_size", 11)
	tag.add_theme_color_override("font_color", Color("74e5dc"))
	stats.add_child(tag)
	var name := Label.new()
	name.text = "ASTRA / MK-06"
	name.add_theme_font_size_override("font_size", 20)
	name.add_theme_color_override("font_color", Color("f0f6ff"))
	stats.add_child(name)
	hp_label = Label.new()
	hp_label.text = "TARGETS  03 / 03     HITS  00"
	hp_label.add_theme_font_size_override("font_size", 12)
	hp_label.add_theme_color_override("font_color", Color("acbfd5"))
	stats.add_child(hp_label)

	var bottom := PanelContainer.new()
	bottom.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	bottom.position = Vector2(32, -84)
	bottom.custom_minimum_size = Vector2(450, 52)
	bottom.add_theme_stylebox_override("panel", _panel_style(Color("0c1525", 0.88), Color("35516c")))
	root.add_child(bottom)
	status_label = Label.new()
	status_label.text = "WASD / ARROWS  MOVE    •    SPACE / ENTER  SLASH    •    R  RESET"
	status_label.add_theme_font_size_override("font_size", 12)
	status_label.add_theme_color_override("font_color", Color("d0deef"))
	bottom.add_child(status_label)

	hint_label = Label.new()
	hint_label.text = "GODOT 4.7  |  WEB READY  |  CLICK GAME WINDOW FOR INPUT"
	hint_label.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	hint_label.position = Vector2(-435, -37)
	hint_label.add_theme_font_size_override("font_size", 10)
	hint_label.add_theme_color_override("font_color", Color("8ea7c2"))
	root.add_child(hint_label)

	_build_action_panel(root)


func _build_action_panel(root: Control) -> void:
	var panel := PanelContainer.new()
	panel.name = "PoseActionPanel"
	panel.custom_minimum_size = Vector2(272, 430)
	panel.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT, Control.PRESET_MODE_KEEP_SIZE)
	panel.position = Vector2(-304, 150)
	panel.size = Vector2(272, 430)
	panel.add_theme_stylebox_override("panel", _panel_style(Color("0c1525", 0.94), Color("4a6d8d")))
	root.add_child(panel)
	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 8)
	panel.add_child(column)
	var heading := Label.new()
	heading.text = "POSE LIBRARY"
	heading.add_theme_font_size_override("font_size", 14)
	heading.add_theme_color_override("font_color", Color("74e5dc"))
	column.add_child(heading)
	var subheading := Label.new()
	subheading.text = "CLICK A BUTTON TO PLAY"
	subheading.add_theme_font_size_override("font_size", 10)
	subheading.add_theme_color_override("font_color", Color("8ea7c2"))
	column.add_child(subheading)
	var actions := [
		["STAND  /  IDLE", "Idle"],
		["WALK", "Walk"],
		["SIT", "Sit"],
		["LIE DOWN", "Lie"],
		["JUMP", "Jump"],
		["SLASH", "Slash"],
	]
	for entry in actions:
		var button := Button.new()
		button.text = entry[0]
		button.custom_minimum_size = Vector2(220, 40)
		button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		button.add_theme_font_size_override("font_size", 12)
		button.add_theme_color_override("font_color", Color("e7f2ff"))
		button.add_theme_stylebox_override("normal", _button_style(Color("162840"), Color("385571")))
		button.add_theme_stylebox_override("hover", _button_style(Color("203b57"), Color("69dcd4")))
		button.add_theme_stylebox_override("pressed", _button_style(Color("275a68"), Color("69dcd4")))
		button.pressed.connect(_on_action_button.bind(entry[1]))
		column.add_child(button)
	var note := Label.new()
	note.text = "SIT / LIE HOLD THE POSE"
	note.add_theme_font_size_override("font_size", 9)
	note.add_theme_color_override("font_color", Color("8ea7c2"))
	column.add_child(note)
	action_label = Label.new()
	action_label.text = "ACTION  //  IDLE"
	action_label.add_theme_font_size_override("font_size", 10)
	action_label.add_theme_color_override("font_color", Color("74e5dc"))
	column.add_child(action_label)


func _button_style(background: Color, border: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = background
	style.border_color = border
	style.set_border_width_all(1)
	style.set_corner_radius_all(5)
	style.content_margin_left = 12
	style.content_margin_right = 12
	style.content_margin_top = 7
	style.content_margin_bottom = 7
	return style


func _on_action_button(action: String) -> void:
	_set_action(action)


func _set_action(action: String) -> void:
	if action_tween != null and action_tween.is_running():
		action_tween.kill()
	action_mode = action
	action_time = 0.0
	walk_button_active = action == "Walk"
	if action == "Walk":
		animation_player.play("Locomotion")
	elif action == "Idle":
		rig.position.y = 0.0
		animation_player.play("Idle")
	elif action == "Sit" or action == "Lie":
		rig.position.y = -0.08 if action == "Sit" else -0.25
		animation_player.play("Pose_Sit" if action == "Sit" else "Pose_Lie")
		animation_player.animation_finished.connect(_hold_pose, CONNECT_ONE_SHOT)
	elif action == "Jump":
		rig.position.y = 0.0
		animation_player.play("Pose_Jump")
		action_time = 0.82
		action_tween = create_tween()
		action_tween.tween_property(rig, "position:y", 1.15, 0.28).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		action_tween.tween_property(rig, "position:y", 0.0, 0.42).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	elif action == "Slash":
		_start_attack()
	if is_instance_valid(action_label):
		action_label.text = "ACTION  //  " + action.to_upper()
		if action == "Sit" or action == "Lie":
			action_label.text += "  //  CLICK STAND TO RESET"


func _hold_pose(_animation_name: StringName) -> void:
	if action_mode == "Sit" or action_mode == "Lie":
		animation_player.pause()


func _start_attack() -> void:
	action_mode = "Slash"
	swing_time = SWING_DURATION
	attack_cooldown = 0.55
	if animation_player != null:
		animation_player.play("Melee_Slash")
	if is_instance_valid(action_label):
		action_label.text = "ACTION  //  SLASH"
	if target_nodes.is_empty():
		return
	var nearest_index := -1
	var nearest_distance := 2.65
	for i in range(target_nodes.size()):
		if target_hp[i] <= 0:
			continue
		var target_position := target_nodes[i].global_position
		var distance := Vector2(target_position.x - player.global_position.x, target_position.z - player.global_position.z).length()
		var direction := Vector2(target_position.x - player.global_position.x, target_position.z - player.global_position.z).normalized()
		var facing := Vector2(sin(rig.rotation.y), -cos(rig.rotation.y))
		if distance < nearest_distance and facing.dot(direction) > 0.12:
			nearest_index = i
			nearest_distance = distance
	if nearest_index >= 0:
		target_hp[nearest_index] -= 1
		hit_count += 1
		if target_hp[nearest_index] <= 0:
			target_nodes[nearest_index].visible = false
		if is_instance_valid(status_label):
			status_label.text = "DIRECT HIT   //   TRAINING UNIT %02d" % (nearest_index + 1)


func _reset_targets() -> void:
	hit_count = 0
	for i in range(target_nodes.size()):
		target_hp[i] = 2
		target_nodes[i].visible = true


func _update_hud() -> void:
	if not is_instance_valid(hp_label):
		return
	var remaining := 0
	for hp in target_hp:
		if hp > 0:
			remaining += 1
	hp_label.text = "TARGETS  %02d / 03     HITS  %02d" % [remaining, hit_count]


func _mat(color: Color, metallic := 0.0, roughness := 0.5, emission := false) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.metallic = metallic
	m.roughness = roughness
	if emission:
		m.emission_enabled = true
		m.emission = color
		m.emission_energy_multiplier = 0.65
	return m


func _add_mesh(parent: Node3D, name: String, mesh: PrimitiveMesh, position: Vector3, scale: Vector3, color: Color, metallic := 0.0, emission := false) -> MeshInstance3D:
	var instance := MeshInstance3D.new()
	instance.name = name
	instance.mesh = mesh
	instance.position = position
	instance.scale = scale
	instance.material_override = _mat(color, metallic, 0.34, emission)
	parent.add_child(instance)
	return instance


func _add_box(parent: Node3D, name: String, pos: Vector3, size: Vector3, color: Color, metallic := 0.0, emission := false) -> MeshInstance3D:
	var mesh := BoxMesh.new()
	mesh.size = size
	return _add_mesh(parent, name, mesh, pos, Vector3.ONE, color, metallic, emission)


func _add_sphere(parent: Node3D, name: String, pos: Vector3, scale: Vector3, color: Color) -> MeshInstance3D:
	return _add_mesh(parent, name, SphereMesh.new(), pos, scale, color, 0.24)


func _add_cylinder(parent: Node3D, name: String, pos: Vector3, radius: float, height: float, color: Color) -> MeshInstance3D:
	var mesh := CylinderMesh.new()
	mesh.top_radius = radius
	mesh.bottom_radius = radius * 1.25
	mesh.height = height
	return _add_mesh(parent, name, mesh, pos, Vector3.ONE, color, 0.35)


func _add_ring(parent: Node3D, pos: Vector3, inner: float, outer: float, color: Color) -> void:
	var ring := MeshInstance3D.new()
	var mesh := TorusMesh.new()
	mesh.inner_radius = inner
	mesh.outer_radius = outer
	ring.mesh = mesh
	ring.position = pos
	ring.material_override = _mat(color, 0.3, 0.3, color.a < 1.0)
	parent.add_child(ring)


func _add_text_3d(text: String, pos: Vector3, size: float, color: Color) -> void:
	var label := Label3D.new()
	label.text = text
	label.position = pos
	label.font_size = 24
	label.pixel_size = size / 24.0
	label.modulate = color
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	add_child(label)


func _panel_style(background: Color, border: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = background
	style.border_color = border
	style.set_border_width_all(1)
	style.set_corner_radius_all(6)
	style.content_margin_left = 16
	style.content_margin_right = 16
	style.content_margin_top = 13
	style.content_margin_bottom = 12
	return style


func _ready_input_map() -> void:
	var bindings := {
		"move_forward": [KEY_W, KEY_UP],
		"move_back": [KEY_S, KEY_DOWN],
		"move_left": [KEY_A, KEY_LEFT],
		"move_right": [KEY_D, KEY_RIGHT],
		"attack": [KEY_SPACE, KEY_ENTER],
	}
	for action in bindings:
		if not InputMap.has_action(action):
			InputMap.add_action(action)
		for key in bindings[action]:
			var event := InputEventKey.new()
			event.physical_keycode = key
			InputMap.action_add_event(action, event)

