import bpy
import io, csv

# --- Active object checks ---
obj = bpy.context.active_object
if obj is None or obj.type != 'MESH':
    raise Exception("Please select a mesh object with shape keys.")

if not obj.data.shape_keys:
    raise Exception("The selected object has no shape keys.")

# --- Parse clipboard data ---
clipboard_text = bpy.context.window_manager.clipboard
if not clipboard_text:
    raise Exception("Clipboard is empty or invalid.")

reader = csv.reader(io.StringIO(clipboard_text), delimiter='\t')
rows = [row for row in reader if row]

def set_shape_values(mapping):
    for k, v in mapping.items():
        obj.data.shape_keys.key_blocks[k].value = v

def reset_shape_values(mapping):
    for k in mapping.keys():
        obj.data.shape_keys.key_blocks[k].value = 0.0

for row in rows:
    if len(row) < 1:
        continue

    # --- Parse row ---
    output_name = row[0].strip()
    # Keys are in columns 1–4, values in columns 5–8
    key_names = [row[i].strip() for i in range(1, 5) if i < len(row) and row[i].strip()]
    key_values = [float(row[i]) for i in range(5, 9) if i < len(row) and row[i].strip()]
    key_value_map = {k: v for k, v in zip(key_names, key_values)}

    # --- Handle blank mix → use Basis ---
    if not key_value_map:
        basis = obj.data.shape_keys.key_blocks.get("Basis")
        if basis is None:
            raise Exception("No 'Basis' shape key found.")
        new_key = obj.shape_key_add(name=output_name, from_mix=False)
        print(f"Created shape key from Basis: {new_key.name}")
        continue

    # --- Check for missing shape keys ---
    missing = [k for k in key_value_map.keys() if k not in obj.data.shape_keys.key_blocks]
    if missing:
        error_name = f"[Error] Missing: {', '.join(missing)}"
        new_key = obj.shape_key_add(name=error_name, from_mix=False)
        print(f"[Error] Shape key(s) not found: {', '.join(missing)} — created placeholder '{error_name}'")
        continue

    # --- Apply valid mix ---
    set_shape_values(key_value_map)
    new_key = obj.shape_key_add(name=output_name, from_mix=True)
    print(f"Created mixed shape key: {new_key.name}")

    # Reset values
    reset_shape_values(key_value_map)

print("Processing complete.")
