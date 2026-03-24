#!/usr/bin/env python3
"""
Stray Signal — Character & Location Reference Exploration v2

LOCKED STYLE. Varied character descriptions and location compositions.
The style DNA is fixed to the approved ink-wash/watercolor animation look.
Divergence is on CHARACTER DESIGN and LOCATION DESIGN within that style.

Pipeline: ComfyUI z-image-base-t2i (local, $0.00)
Output: projects/stray-signal/REFERENCES/exploration_v2/

Usage:
  python3 scripts/production/explore_character_refs_v2.py --target neda
  python3 scripts/production/explore_character_refs_v2.py --target kai
  python3 scripts/production/explore_character_refs_v2.py --target locations
  python3 scripts/production/explore_character_refs_v2.py --target all
  python3 scripts/production/explore_character_refs_v2.py --dry-run
"""

import io
import sys
import time
from pathlib import Path

from PIL import Image
import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
COMFYUI_BASE = "http://192.168.1.181:8100"

PROJECT = Path(__file__).resolve().parents[2] / "projects" / "stray-signal"
OUTPUT_BASE = PROJECT / "REFERENCES" / "exploration_v3"

# ---------------------------------------------------------------------------
# LOCKED STYLE PREFIX — ink-outlined animation frame
# ---------------------------------------------------------------------------
# Animation frame aesthetic — NOT concept art, NOT watercolor painting.
# Clean ink outlines, flat cel color with subtle texture, graphic novel
# character proportions (non-anime: broader features, angular jawlines,
# realistic proportions). Reads as a still frame from an animated series.

STYLE = (
    "Still frame from an animated series, clean dark ink outlines, "
    "flat cel-shaded coloring with subtle paper texture, bold graphic shapes, "
    "non-anime character proportions with broad angular features and realistic body shapes, "
    "strong silhouette design, limited color palette per frame, "
    "brutalist concrete architecture with visible surface texture, "
    "steel-blue and concrete grey color scheme with selective warm accents underground, "
    "cinematic composition and lighting, graphic novel aesthetic, "
)

NEGATIVE = (
    "photorealistic, 3D render, watercolor, concept art, painting, "
    "smooth digital coloring, airbrushed, soft gradients, "
    "anime eyes, anime proportions, manga, chibi, big eyes, pointy chin, "
    "soft glow, bloom, lens flare, neon, cyberpunk, "
    "multiple characters, crowd, blurry, low quality, deformed, "
    "extra limbs, bad anatomy, text, watermark, signature, "
    "holographic, floating UI, bright saturated colors"
)

# ---------------------------------------------------------------------------
# NEDA VARIANTS — same style, different character design choices
# ---------------------------------------------------------------------------
# Each variant explores a different interpretation of Neda's physical
# description while staying within the character sheet's constraints.

NEDA_CORE = (
    "17-year-old girl, brown skin with warm undertone, sharp dark assessing eyes, "
    "scar across right knuckles, "
)

NEDA_VARIANTS = {
    # --- Hair variations ---
    "hair_cropped_tight": {
        "desc": "Hair: tight crop, almost shaved sides, minimal top",
        "prompt": (
            STYLE + "Close-up portrait of " + NEDA_CORE +
            "black hair in a very tight crop — almost shaved on the sides with only "
            "a centimeter of length on top, military-practical, emphasizing the angular "
            "shape of her skull and jaw. Thin copper-wire braid behind left ear. "
            "Angular steel-blue geometric jacket with origami collar. "
            "Brutalist concrete wall background, cold flat fluorescent light. "
            "Expression: neutral, assessing, controlled."
        ),
        "w": 720, "h": 1024,
    },
    "hair_asymmetric_sweep": {
        "desc": "Hair: asymmetric sweep, shaved left, longer right",
        "prompt": (
            STYLE + "Close-up portrait of " + NEDA_CORE +
            "black hair in an asymmetric cut — shaved close on the left side "
            "with longer hair swept across to the right, falling just past the ear. "
            "The copper-wire braid hangs from the shaved left side, exposed and visible. "
            "Angular steel-blue geometric jacket with origami collar. "
            "Brutalist concrete wall background, cold flat fluorescent light. "
            "Expression: neutral, assessing, controlled."
        ),
        "w": 720, "h": 1024,
    },
    "hair_bob_blunt": {
        "desc": "Hair: blunt bob at jawline",
        "prompt": (
            STYLE + "Close-up portrait of " + NEDA_CORE +
            "black hair in a blunt bob cut at the jawline, straight and severe, "
            "framing the angular face like architecture. Pushed back from forehead. "
            "The copper-wire braid is tucked behind the left ear, barely visible. "
            "Angular steel-blue geometric jacket with origami collar. "
            "Brutalist concrete wall background, cold flat fluorescent light. "
            "Expression: neutral, assessing, controlled."
        ),
        "w": 720, "h": 1024,
    },
    "hair_undercut_topknot": {
        "desc": "Hair: undercut with short pulled-back top",
        "prompt": (
            STYLE + "Close-up portrait of " + NEDA_CORE +
            "black hair with a deep undercut — sides shaved, top section "
            "long enough to push straight back and stay put, practical and deliberate. "
            "Copper-wire braid hanging from behind left ear against the shaved section. "
            "Angular steel-blue geometric jacket with origami collar. "
            "Brutalist concrete wall background, cold flat fluorescent light. "
            "Expression: neutral, assessing, controlled."
        ),
        "w": 720, "h": 1024,
    },
    "hair_textured_short": {
        "desc": "Hair: short textured natural, tight curls",
        "prompt": (
            STYLE + "Close-up portrait of " + NEDA_CORE +
            "black hair in a short natural texture — tight curls kept very short, "
            "maybe two inches, with a clean geometric edge-up at the forehead and temples. "
            "Copper-wire braid woven into the hair behind left ear. "
            "Angular steel-blue geometric jacket with origami collar. "
            "Brutalist concrete wall background, cold flat fluorescent light. "
            "Expression: neutral, assessing, controlled."
        ),
        "w": 720, "h": 1024,
    },

    # --- Face/build variations ---
    "face_sharp_narrow": {
        "desc": "Face: sharp narrow jaw, high cheekbones, older-reading",
        "prompt": (
            STYLE + "Close-up portrait of " + NEDA_CORE +
            "narrow angular face with sharp jaw and high prominent cheekbones, "
            "reads slightly older than 17 — the face of someone who hasn't slept well "
            "in months. Hollows beneath the cheekbones. Black hair cropped short on sides, "
            "longer on top pushed back. Copper-wire braid behind left ear. "
            "Angular steel-blue geometric jacket with origami collar. "
            "Brutalist concrete wall background, cold flat fluorescent light. "
            "Expression: neutral, assessing, controlled."
        ),
        "w": 720, "h": 1024,
    },
    "face_round_strong": {
        "desc": "Face: rounder face, strong jaw, compact presence",
        "prompt": (
            STYLE + "Close-up portrait of " + NEDA_CORE +
            "rounder face with a strong squared jaw — compact and powerful, "
            "the face of someone built for tight corridors. Wide-set dark eyes. "
            "Black hair cropped short on sides, longer on top pushed back. "
            "Copper-wire braid behind left ear. "
            "Angular steel-blue geometric jacket with origami collar. "
            "Brutalist concrete wall background, cold flat fluorescent light. "
            "Expression: neutral, assessing, controlled."
        ),
        "w": 720, "h": 1024,
    },
    "face_broad_striking": {
        "desc": "Face: broad features, wide nose, striking/memorable",
        "prompt": (
            STYLE + "Close-up portrait of " + NEDA_CORE +
            "broad face with wide nose, full lips, strong brow — a face that is "
            "striking rather than pretty, impossible to forget once you've seen it. "
            "Deep-set watchful eyes under heavy brows. Black hair cropped short on sides, "
            "longer on top pushed back. Copper-wire braid behind left ear. "
            "Angular steel-blue geometric jacket with origami collar. "
            "Brutalist concrete wall background, cold flat fluorescent light. "
            "Expression: neutral, assessing, controlled."
        ),
        "w": 720, "h": 1024,
    },

    # --- Outfit variations (Grid) ---
    "outfit_grid_heavy": {
        "desc": "Grid outfit: heavier, more structured, armored feel",
        "prompt": (
            STYLE + "Full body shot of " + NEDA_CORE +
            "black hair cropped short on sides with longer top pushed back. "
            "Wearing a heavy structured steel-blue jacket with rigid origami panels — "
            "almost armored, geometric shoulder extensions, double-folded high collar "
            "that covers the neck. Thick concrete-grey fitted trousers with angular "
            "seam lines. Heavy polymer boots. The clothing is architectural — she looks "
            "like a small building moving through a street of larger buildings. "
            "Brutalist concrete plaza, overcast steel-blue sky, vanishing point perspective. "
            "Full figure head to toe."
        ),
        "w": 1024, "h": 1024,
    },
    "outfit_grid_minimal": {
        "desc": "Grid outfit: minimal, barely-there geometric detail",
        "prompt": (
            STYLE + "Full body shot of " + NEDA_CORE +
            "black hair cropped short on sides with longer top pushed back. "
            "Wearing a simple steel-blue cropped jacket with subtle geometric seams — "
            "the origami is restrained, just angular stitching at the shoulders and collar. "
            "Slim concrete-grey trousers, standard polymer boots. The outfit is deliberately "
            "unremarkable — designed to disappear into the Grid's uniformity. Her posture "
            "is the only thing that distinguishes her. "
            "Brutalist concrete plaza, overcast steel-blue sky, vanishing point perspective. "
            "Full figure head to toe."
        ),
        "w": 1024, "h": 1024,
    },
    "outfit_grid_layered": {
        "desc": "Grid outfit: visible layers, collar up, tactical",
        "prompt": (
            STYLE + "Full body shot of " + NEDA_CORE +
            "black hair cropped short on sides with longer top pushed back. "
            "Wearing layered Grid clothing — a steel-blue outer jacket with angular collar "
            "turned up, over a darker grey underlayer visible at the waist and wrists. "
            "Fitted trousers with cargo pockets sealed flat against the legs. "
            "Boots laced tight. The layering reads tactical — someone who dresses to "
            "move fast and carry things unseen. "
            "Brutalist concrete plaza, overcast steel-blue sky, vanishing point perspective. "
            "Full figure head to toe."
        ),
        "w": 1024, "h": 1024,
    },

    # --- Seam appearance ---
    "seam_warm_operational": {
        "desc": "Seam: rust layers, tool harness, amber light",
        "prompt": (
            STYLE + "Full body shot of " + NEDA_CORE +
            "black hair cropped short on sides with longer top pushed back. "
            "Copper-wire braid behind left ear catching amber light. "
            "Grid jacket removed. Wearing a fitted dark brown jacket with visible "
            "hand-stitching over a rust-colored underlayer. Tool harness across chest "
            "with junction access instruments. Cargo pockets on worn trousers. "
            "Boots with real scuffs and patina. She is sharp and direct here — no performance. "
            "Rough stone corridor with amber LED string lights, warm golden glow on everything. "
            "Full figure head to toe."
        ),
        "w": 1024, "h": 1024,
    },
    "seam_stripped_back": {
        "desc": "Seam: minimal layers, more of the person visible",
        "prompt": (
            STYLE + "Full body shot of " + NEDA_CORE +
            "black hair cropped short on sides with longer top pushed back. "
            "Copper-wire braid behind left ear catching amber light. "
            "Wearing just the rust-colored underlayer — a fitted long-sleeve "
            "with rolled sleeves showing forearms and the knuckle scar. Tool belt "
            "at the waist. Simple dark trousers and worn boots. Less clothing, "
            "more of the person visible. The amber light warms her brown skin. "
            "Rough stone corridor with amber LED string lights. "
            "Full figure head to toe."
        ),
        "w": 1024, "h": 1024,
    },
}

# ---------------------------------------------------------------------------
# KAI VARIANTS — same style, different character design choices
# ---------------------------------------------------------------------------

KAI_CORE = (
    "16-year-old boy, lean narrow-shouldered build, light brown skin, "
    "watchful dark eyes that track movement before faces, "
)

KAI_VARIANTS = {
    # --- Hair variations ---
    "hair_regulation_buzz": {
        "desc": "Hair: near-regulation buzz, barely longer on top",
        "prompt": (
            STYLE + "Close-up portrait of " + KAI_CORE +
            "dark hair in a near-regulation buzz cut — barely longer on top, "
            "the kind of cut you get when you keep forgetting to schedule the trim "
            "and it grows back to the same nothing-length every time. No style, no choice. "
            "Angular geometric jacket in concrete grey with high collar. "
            "Brutalist concrete wall background, cold flat fluorescent light. "
            "Expression: neutral, watchful, unremarkable at first glance."
        ),
        "w": 720, "h": 1024,
    },
    "hair_shaggy_overgrown": {
        "desc": "Hair: overgrown regulation cut, falling in eyes",
        "prompt": (
            STYLE + "Close-up portrait of " + KAI_CORE +
            "dark hair that's clearly an overgrown regulation cut — sides growing out "
            "unevenly, top long enough to fall across his forehead and into his eyes. "
            "He pushes it back but it doesn't stay. The one visible sign of deviation "
            "from Grid norms. "
            "Angular geometric jacket in concrete grey with high collar. "
            "Brutalist concrete wall background, cold flat fluorescent light. "
            "Expression: neutral, watchful, unremarkable at first glance."
        ),
        "w": 720, "h": 1024,
    },
    "hair_straight_longer": {
        "desc": "Hair: straight, deliberately longer on top, pushed back",
        "prompt": (
            STYLE + "Close-up portrait of " + KAI_CORE +
            "dark straight hair kept longer on top — maybe three inches — pushed back "
            "from his face with his fingers. The sides are shorter but not shaved. "
            "It looks intentional in a world where intention is suspicious. "
            "Angular geometric jacket in concrete grey with high collar. "
            "Brutalist concrete wall background, cold flat fluorescent light. "
            "Expression: neutral, watchful, unremarkable at first glance."
        ),
        "w": 720, "h": 1024,
    },
    "hair_textured_curls": {
        "desc": "Hair: short textured curls, natural",
        "prompt": (
            STYLE + "Close-up portrait of " + KAI_CORE +
            "dark hair in short natural curls — not styled, just the way it grows. "
            "Kept short enough to be regulation-adjacent but the texture is his own. "
            "Tight curls close to his head, slightly longer on top. "
            "Angular geometric jacket in concrete grey with high collar. "
            "Brutalist concrete wall background, cold flat fluorescent light. "
            "Expression: neutral, watchful, unremarkable at first glance."
        ),
        "w": 720, "h": 1024,
    },
    "hair_parted_flat": {
        "desc": "Hair: side-parted, flat, almost too neat",
        "prompt": (
            STYLE + "Close-up portrait of " + KAI_CORE +
            "dark hair side-parted and lying flat — almost too neat, the way someone "
            "who doesn't care about hair but follows rules would wear it. "
            "Precise part line, everything in its place. The compliance is visible. "
            "Angular geometric jacket in concrete grey with high collar. "
            "Brutalist concrete wall background, cold flat fluorescent light. "
            "Expression: neutral, watchful, unremarkable at first glance."
        ),
        "w": 720, "h": 1024,
    },

    # --- Face/build variations ---
    "face_angular_hungry": {
        "desc": "Face: angular, slight, hunger visible in the cheekbones",
        "prompt": (
            STYLE + "Close-up portrait of " + KAI_CORE +
            "angular face with prominent cheekbones and a narrow chin — the face of "
            "someone running on pattern-hunger, not food. Dark circles under watchful eyes. "
            "Dark short hair slightly longer on top. "
            "Angular geometric jacket in concrete grey with high collar. "
            "Brutalist concrete wall background, cold flat fluorescent light. "
            "Expression: neutral but the eyes are alive — tracking, calculating."
        ),
        "w": 720, "h": 1024,
    },
    "face_soft_round": {
        "desc": "Face: softer, rounder, looks younger than 16",
        "prompt": (
            STYLE + "Close-up portrait of " + KAI_CORE +
            "softer rounder face that makes him look younger than 16 — "
            "the kind of face that makes what happens to him worse. Round cheeks, "
            "wide dark eyes, slight frame. He looks like someone who should be protected. "
            "Dark short hair slightly longer on top. "
            "Angular geometric jacket in concrete grey with high collar. "
            "Brutalist concrete wall background, cold flat fluorescent light. "
            "Expression: neutral, watching."
        ),
        "w": 720, "h": 1024,
    },
    "face_plain_forgettable": {
        "desc": "Face: deliberately plain, the face you don't remember",
        "prompt": (
            STYLE + "Close-up portrait of " + KAI_CORE +
            "face that is deliberately, almost aggressively average — the kind LEDGER's "
            "behavioral models flag as nominal. Not ugly, not handsome, not memorable. "
            "Medium features, medium proportions. The only remarkable thing is the eyes — "
            "they're tracking something the rest of the face doesn't acknowledge. "
            "Dark short hair slightly longer on top. "
            "Angular geometric jacket in concrete grey with high collar. "
            "Brutalist concrete wall background, cold flat fluorescent light."
        ),
        "w": 720, "h": 1024,
    },

    # --- With device (the signature moment) ---
    "device_glow_portrait": {
        "desc": "Face lit by device — cyan glow, the hook",
        "prompt": (
            STYLE + "Close-up portrait of " + KAI_CORE +
            "dark short hair slightly longer on top. His face lit from below by "
            "cyan wireframe glow from a device screen. The cyan picks out his cheekbones "
            "and the shadows under his eyes. Dark maintenance corridor behind him — "
            "no fluorescent light, just the device glow. His expression: the first real "
            "curiosity he's ever felt. Eyes wide, lips slightly parted. "
            "The cyan is the only color in the frame."
        ),
        "w": 720, "h": 1024,
    },
    "device_hands_close": {
        "desc": "Hands holding device, cyan wireframe cat on screen",
        "prompt": (
            STYLE + "Extreme close-up of a boy's hands holding a brushed-aluminum "
            "tablet device. Light brown skin, lean fingers, one thumb testing the edge "
            "of the device frame. The screen shows a small cyan wireframe cat sitting. "
            "The glow casts cyan light on his fingertips and the polymer floor beneath. "
            "The device is scratched, dented, warm from use. Maintenance corridor background, "
            "dark with cold fluorescent strips. The hands are precise, quick — "
            "maintenance worker's hands."
        ),
        "w": 1024, "h": 720,
    },

    # --- Full body Grid ---
    "full_corridor_folded": {
        "desc": "Full body in corridor, folded inward, blending in",
        "prompt": (
            STYLE + "Full body shot of " + KAI_CORE +
            "dark short hair slightly longer on top. "
            "Angular geometric clothing in concrete grey and steel blue — "
            "structured jacket with folded panels and high collar, fitted trousers "
            "in pale sage, polymer boots. Maintenance tool belt at waist. "
            "He stands in a brutalist maintenance corridor — concrete walls, "
            "polymer conduits, fluorescent strips. Posture folded inward, shoulders "
            "slightly hunched. He blends into the architecture. The tool belt is "
            "his one visual distinction. Full figure head to toe."
        ),
        "w": 1024, "h": 1024,
    },
    "full_watched": {
        "desc": "Kai from distance — Neda's surveillance POV",
        "prompt": (
            STYLE + "Medium-wide shot of a 16-year-old boy with lean build, "
            "light brown skin, dark short hair, seen from behind a corridor junction. "
            "He doesn't know he's being watched. Crouched at a wall panel, device in hand, "
            "cyan glow on the polymer floor. Maintenance corridor at shift-end — "
            "empty, fluorescent, cold. He's the only warm thing in the frame. "
            "Shot from distance. Voyeuristic composition — we are surveilling him."
        ),
        "w": 1280, "h": 720,
    },
}

# ---------------------------------------------------------------------------
# LOCATION VARIANTS — same style, different compositions/interpretations
# ---------------------------------------------------------------------------

LOCATION_VARIANTS = {
    # --- Grid (3 variants each) ---
    "grid_plaza_monumental": {
        "desc": "Grid plaza: overwhelming scale, sky barely visible",
        "prompt": (
            STYLE + "Wide establishing shot of a brutalist dystopian cityscape. "
            "Massive monolithic concrete towers rising so high the sky is a thin strip "
            "at the top. No ornament, no curves, no color. The buildings are too large "
            "for the frame. Concrete grey and steel blue palette. Overcast diffused light. "
            "A single small surveillance drone in the upper portion. "
            "The scale is not grand — it's oppressive. The architecture is indifferent "
            "to human presence. NO people, NO characters, NO animals."
        ),
        "w": 1280, "h": 720,
    },
    "grid_plaza_geometric": {
        "desc": "Grid plaza: geometric pattern, overhead angle",
        "prompt": (
            STYLE + "Slightly elevated view of a brutalist concrete plaza. "
            "The buildings form a repeating geometric pattern — identical blocks "
            "at identical intervals stretching to the horizon. Smooth polished ground plane "
            "reflecting cold sky. No vegetation, no signage, no variation. "
            "The pattern is the point — this world was designed, not grown. "
            "Concrete grey and steel blue palette. Flat overcast light. "
            "NO people, NO characters, NO animals."
        ),
        "w": 1280, "h": 720,
    },
    "grid_street_canyon": {
        "desc": "Grid street: concrete canyon, pedestrian scale",
        "prompt": (
            STYLE + "Street-level view of a brutalist concrete canyon. "
            "Massive walls on both sides, smooth concrete with visible form-tie holes. "
            "Polymer floor with geometric grid lines. Fluorescent strip lights along "
            "the lower walls. A thin strip of cold grey sky between buildings. "
            "The street is sized for single-file. No signage, no decoration, no color. "
            "Vanishing point perspective. The architecture moves people, it doesn't "
            "welcome them. NO people, NO characters."
        ),
        "w": 1280, "h": 720,
    },

    # --- Descent (the gradient) ---
    "descent_upper_cold": {
        "desc": "Descent: cold upper section, polymer and fluorescent",
        "prompt": (
            STYLE + "Narrow vertical passage descending into dimness. "
            "Polymer steps going down. Cold fluorescent strip lights on smooth concrete walls. "
            "Steel-blue tone everywhere. The walls are processed, clinical, Grid-built. "
            "The passage is one-person wide. Looking downward into growing darkness. "
            "No warmth, no texture, no life. The same dead architecture going underground. "
            "NO people, NO characters."
        ),
        "w": 720, "h": 1280,
    },
    "descent_middle_transition": {
        "desc": "Descent: transition zone — cold above, warm below",
        "prompt": (
            STYLE + "Narrow vertical passage at the transition point. "
            "Looking downward. The upper walls are smooth concrete with cold fluorescent light. "
            "The lower walls shift to rough stone with amber light seeping upward. "
            "Two palettes sharing one frame — steel blue fading to amber. "
            "The polymer steps give way to rough-hewn stone steps below. "
            "The transition is visible — manufactured world above, hand-carved world below. "
            "NO people, NO characters."
        ),
        "w": 720, "h": 1280,
    },
    "descent_lower_warm": {
        "desc": "Descent: warm lower section, stone and amber",
        "prompt": (
            STYLE + "Underground stone stairway descending into warm amber light. "
            "Rough-hewn stone walls, hand-chipped texture visible. Amber LED string lights "
            "strung along the walls casting golden pools on the stone. The steps are "
            "worn smooth from years of use. At the bottom, a warm amber space opens up. "
            "The concrete is gone. Everything is stone, light, warmth. "
            "The opposite of the Grid. NO people, NO characters."
        ),
        "w": 720, "h": 1280,
    },

    # --- Seam corridor (3 variants) ---
    "seam_corridor_wide": {
        "desc": "Seam corridor: wide main passage, amber, branching",
        "prompt": (
            STYLE + "Wide shot of an underground corridor carved from rough stone. "
            "Amber LED string lights overhead casting warm golden light. "
            "Multiple branching passages visible — this is a hub, not a tunnel. "
            "Salvaged electronics on walls, old circuit boards repurposed as decoration. "
            "Growing plants in wall-mounted containers. Worn stone floor. "
            "The architecture is organic, adapted, human. Warm amber with moss green accents. "
            "NO people, NO characters."
        ),
        "w": 1280, "h": 720,
    },
    "seam_corridor_intimate": {
        "desc": "Seam corridor: narrow residential passage, lived-in",
        "prompt": (
            STYLE + "Narrow underground corridor carved from stone. "
            "Amber string lights at intervals creating pools of gold and shadow. "
            "Doorways cut into the stone walls — some with fabric curtains, some open "
            "revealing small rooms. A shelf carved into the wall holds a cup and a book. "
            "The stone has marks from three generations of hands. This is a home, "
            "not a bunker. Warm amber palette. NO people, NO characters."
        ),
        "w": 1280, "h": 720,
    },
    "seam_corridor_junction": {
        "desc": "Seam corridor: junction with colored wiring",
        "prompt": (
            STYLE + "Underground junction where three stone corridors meet. "
            "Bundles of salvaged wiring run along the ceiling — copper, green insulation, "
            "old data cables repurposed. A junction box mounted at the intersection, "
            "indicator lights glowing amber. Rough stone walls with moss in the cracks. "
            "Amber string lights illuminating the three passages. Handmade signage "
            "scratched into the stone — arrows, symbols. NO people, NO characters."
        ),
        "w": 1280, "h": 720,
    },

    # --- Fen's room (2 variants) ---
    "fen_room_doorway": {
        "desc": "Fen's room: seen through doorway, two light zones",
        "prompt": (
            STYLE + "View through a stone doorway into a small underground room. "
            "The room is lit by overhead grow-lamps casting harsh green-white light downward. "
            "A single chair in the center, empty. The walls are rough stone but the "
            "grow-lamp light makes them clinical. Small plants growing under the lamps. "
            "The doorway frame is in warm amber light from the corridor behind us. "
            "Two distinct lighting zones: warm amber doorway, green-white clinical room. "
            "The contrast is stark. NO people, NO characters."
        ),
        "w": 1280, "h": 720,
    },
    "fen_room_inside": {
        "desc": "Fen's room: from inside, looking at the chair",
        "prompt": (
            STYLE + "Interior of a small underground room. Green-white grow-lamp light "
            "from above casting harsh shadows. A single chair in the center of the room, "
            "empty but with the impression of constant use — the stone floor around it "
            "is worn smooth. Plants growing under the lamps along the walls. "
            "A doorway in the background shows warm amber corridor light — the only "
            "warm color in the frame. The room feels medical, careful, wrong. "
            "NO people, NO characters."
        ),
        "w": 1280, "h": 720,
    },

    # --- Briefing alcove (2 variants) ---
    "briefing_alcove_intimate": {
        "desc": "Briefing alcove: small, amber, stone table",
        "prompt": (
            STYLE + "A small underground room carved from rough stone. Close stone walls. "
            "Deep amber LED lights casting heavy golden light on every surface. "
            "A rough-hewn stone table in the center with two seats. Low ceiling. "
            "The amber light is thick, almost liquid on the stone surfaces. "
            "No windows. A map or storyboard pinned to the wall. Salvaged screen on "
            "the table, dark. A briefing room for two — private, hidden, warm. "
            "NO people, NO characters."
        ),
        "w": 1280, "h": 720,
    },
    "briefing_alcove_spartan": {
        "desc": "Briefing alcove: minimal, just table and stone",
        "prompt": (
            STYLE + "A cramped underground alcove. Bare rough stone walls with no "
            "decoration. A flat stone slab serving as a table, two crude seats carved "
            "from the rock. A single amber LED strip overhead, the only light source. "
            "The space is barely large enough for two people. There is nothing here "
            "except the essentials — table, seats, light. The minimalism is the point. "
            "This is where decisions that destroy people are made quietly. "
            "NO people, NO characters."
        ),
        "w": 1280, "h": 720,
    },

    # --- Maintenance corridor (where Kai meets device) ---
    "maintenance_corridor_end_of_shift": {
        "desc": "Maintenance corridor: empty, fluorescent, vanishing point",
        "prompt": (
            STYLE + "A long straight maintenance corridor in a brutalist facility. "
            "Cold fluorescent strip lights overhead casting flat shadowless light. "
            "Polymer conduits running along both walls. Access panels at regular intervals. "
            "The corridor stretches to a vanishing point — geometric, repetitive, empty. "
            "End-of-shift silence. This is infrastructure, not living space. "
            "Cold steel-blue palette with no warmth at all. "
            "NO people, NO characters."
        ),
        "w": 1280, "h": 720,
    },
    "maintenance_corridor_with_glow": {
        "desc": "Maintenance corridor: distant cyan glow at far end",
        "prompt": (
            STYLE + "A long straight maintenance corridor. Cold fluorescent strips overhead. "
            "Polymer conduits and access panels along concrete walls. The corridor stretches "
            "to a vanishing point. At the far end — barely visible — a faint cyan glow "
            "on the floor and lower wall. Something is glowing down there. "
            "The cyan is the only deviation from the monotone steel-blue palette. "
            "It draws the eye. It shouldn't be there. "
            "NO people, NO characters."
        ),
        "w": 1280, "h": 720,
    },
}


# ---------------------------------------------------------------------------
# API Helper
# ---------------------------------------------------------------------------
def submit_and_wait(workflow_id, params, timeout=600):
    url = f"{COMFYUI_BASE}/workflows/{workflow_id}"
    resp = requests.post(url, data=params)
    resp.raise_for_status()
    job = resp.json()
    job_id = job["job_id"]
    deadline = time.time() + timeout
    polls = 0
    while time.time() < deadline:
        status = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}").json()
        polls += 1
        if status["status"] == "completed":
            elapsed = time.time() - (deadline - timeout)
            print(f"    Done ({elapsed:.0f}s)")
            return requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result").content
        if status["status"] == "error":
            raise RuntimeError(f"Job {job_id} failed: {status.get('error')}")
        time.sleep(2 if polls <= 5 else 3)
    raise TimeoutError(f"Timeout on {job_id}")


def z_image_t2i(prompt, negative, seed, width, height, steps=25, cfg=4.0):
    params = {
        "prompt": prompt,
        "negative_prompt": negative,
        "seed": str(seed),
        "steps": str(steps),
        "cfg": str(cfg),
        "width": str(width),
        "height": str(height),
    }
    return submit_and_wait("z-image-base-t2i", params)


def save(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    size = Image.open(io.BytesIO(data)).size
    print(f"    Saved: {path.name} ({size[0]}x{size[1]})")
    return path


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------
def generate_variants(name, variants, out_dir, base_seed=8000):
    out_dir.mkdir(parents=True, exist_ok=True)
    total = len(variants)
    count = 0

    for var_name, var in variants.items():
        count += 1
        filename = f"{name}_{var_name}.png"
        filepath = out_dir / filename

        if filepath.exists():
            print(f"[{count}/{total}] SKIP (exists): {filename}")
            continue

        seed = base_seed + hash(var_name) % 10000

        print(f"\n[{count}/{total}] {filename}")
        print(f"  {var['desc']}")

        try:
            data = z_image_t2i(
                prompt=var["prompt"],
                negative=NEGATIVE,
                seed=seed,
                width=var["w"],
                height=var["h"],
            )
            save(data, filepath)
        except Exception as e:
            print(f"    ERROR: {e}")
            continue


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Character & location exploration v2 (locked style)")
    parser.add_argument("--target", choices=["neda", "kai", "locations", "all"],
                        default="all", help="What to explore (default: all)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be generated without generating")
    args = parser.parse_args()

    targets = {
        "neda": ("neda", NEDA_VARIANTS, OUTPUT_BASE / "neda", 8000),
        "kai": ("kai", KAI_VARIANTS, OUTPUT_BASE / "kai", 9000),
        "locations": ("loc", LOCATION_VARIANTS, OUTPUT_BASE / "locations", 10000),
    }

    if args.dry_run:
        print("=" * 70)
        print("DRY RUN — Exploration v2 (Locked Style)")
        print("=" * 70)
        print(f"\nStyle: ink-wash watercolor animation (LOCKED)")

        active = list(targets.keys()) if args.target == "all" else [args.target]
        total = 0
        for t in active:
            name, variants, out_dir, _ = targets[t]
            n = len(variants)
            total += n
            print(f"\n{t.upper()}: {n} variants")
            for v, d in variants.items():
                print(f"  {name}_{v}.png — {d['desc']} ({d['w']}x{d['h']})")

        print(f"\nTOTAL: {total} images")
        est = total * 20
        print(f"Estimated time: ~{est // 60}m {est % 60}s")
        sys.exit(0)

    print("=" * 70)
    print("Stray Signal — Exploration v2 (Locked Style)")
    print(f"Output: {OUTPUT_BASE}")
    print("=" * 70)

    active = list(targets.keys()) if args.target == "all" else [args.target]
    for t in active:
        name, variants, out_dir, seed = targets[t]
        print(f"\n{'=' * 70}")
        print(f"{t.upper()} — {len(variants)} variants")
        print("=" * 70)
        generate_variants(name, variants, out_dir, seed)

    print(f"\n{'=' * 70}")
    print("EXPLORATION v2 COMPLETE")
    print(f"Review: {OUTPUT_BASE}")
    print("=" * 70)
