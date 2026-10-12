"""Shared dimensions, editorial palette, typography and helpers for visual v3."""
from __future__ import annotations
from ..visual_v2.palette import W,H,FPS,DURATION,NFRAMES,font,fit_font,clamp,smooth,ease_out

C={
    "night_top":(4,8,18),
    "night_mid":(10,18,31),
    "night_horizon":(30,39,50),
    "cloud_shadow":(11,19,32),
    "cloud_mid":(31,43,57),
    "cloud_lit":(70,84,100),
    "steel":(25,35,48),
    "steel_light":(62,78,95),
    "glass":(11,23,37),
    "window_warm":(255,190,109),
    "window_cool":(130,171,204),
    "street":(8,13,21),
    "white":(243,247,250),
    "muted":(180,194,207),
    "accent":(245,194,126),
    "lightning":(233,246,255),
    "lightning_glow":(127,184,229),
    "tree_shadow":(16,34,31),
    "tree_mid":(27,49,42),
    "tree_lit":(46,68,55),
    "brick":(28,35,43),
}

# Editorial cut points stay aligned to the previously approved VO/SFX.
SCENES=[
    (0.00,5.55,"hook"),
    (5.55,11.41,"stat"),
    (11.41,22.32,"mechanism"),
    (22.32,29.59,"repeat"),
    (29.59,39.81,"flicker"),
    (39.81,DURATION,"safety"),
]
TRANSITION=.20
