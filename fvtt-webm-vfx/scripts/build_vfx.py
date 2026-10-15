#!/usr/bin/env python3
"""Render procedural RGBA VFX recipes and encode transparent VP9 WebM for Foundry VTT."""

from __future__ import annotations

import argparse
import copy
import json
import math
import random
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageStat
except ImportError as exc:
    raise SystemExit("Pillow is required. Install the Python package 'Pillow'.") from exc

TAU = math.tau


def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def lerp(a, b, t):
    return a + (b - a) * t


def smoothstep(t):
    t = clamp(t)
    return t * t * (3.0 - 2.0 * t)


def ease_out_cubic(t):
    t = clamp(t)
    return 1.0 - (1.0 - t) ** 3


def as_pair(v):
    if isinstance(v, (int, float)):
        return float(v), float(v)
    if isinstance(v, list) and len(v) == 2 and all(isinstance(x, (int, float)) for x in v):
        return float(v[0]), float(v[1])
    raise ValueError(f"Expected scalar or numeric pair, got {v!r}")


def color_rgba(value, alpha_mul=1.0):
    if isinstance(value, list):
        if len(value) == 3:
            r, g, b = value
            a = 255
        elif len(value) == 4:
            r, g, b, a = value
        else:
            raise ValueError(f"Color list must have 3 or 4 values: {value!r}")
        return tuple(int(clamp(float(c) / 255.0) * 255) for c in (r, g, b)) + (int(clamp(float(a) / 255.0 * alpha_mul) * 255),)
    if not isinstance(value, str):
        raise ValueError(f"Unsupported color: {value!r}")
    s = value.strip().lstrip("#")
    if len(s) == 6:
        s += "FF"
    if len(s) != 8 or not re.fullmatch(r"[0-9a-fA-F]{8}", s):
        raise ValueError(f"Color must be #RRGGBB or #RRGGBBAA: {value!r}")
    r, g, b, a = (int(s[i:i+2], 16) for i in (0, 2, 4, 6))
    return r, g, b, int(clamp(a / 255.0 * alpha_mul) * 255)


def point_px(value, width, height):
    return float(value[0]) * width, float(value[1]) * height


def layer_timing(layer, t):
    start = float(layer.get("start", 0.0))
    end = float(layer.get("end", 1.0))
    if end <= start or t < start or t > end:
        return None
    p = clamp((t - start) / (end - start))
    fade_in = max(0.0, float(layer.get("fade_in", 0.06)))
    fade_out = max(0.0, float(layer.get("fade_out", 0.24)))
    env = 1.0
    if fade_in > 0 and p < fade_in:
        env *= smoothstep(p / fade_in)
    if fade_out > 0 and p > 1.0 - fade_out:
        env *= smoothstep((1.0 - p) / fade_out)
    env *= float(layer.get("opacity", 1.0))
    return p, clamp(env)


def composite(base, layer, mode="normal"):
    if mode == "add":
        br, bg, bb, ba = base.split()
        lr, lg, lb, la = layer.split()
        out = Image.merge(
            "RGBA",
            (
                ImageChops.add(br, lr),
                ImageChops.add(bg, lg),
                ImageChops.add(bb, lb),
                ImageChops.lighter(ba, la),
            ),
        )
        return out
    return Image.alpha_composite(base, layer)


def with_glow(layer_img, glow_norm, basis):
    glow_norm = float(glow_norm or 0.0)
    if glow_norm <= 0:
        return layer_img
    radius = max(0.5, glow_norm * basis)
    glow = layer_img.filter(ImageFilter.GaussianBlur(radius=radius))
    ga = glow.getchannel("A")
    ga = ImageEnhance.Brightness(ga).enhance(0.9)
    glow.putalpha(ga)
    return Image.alpha_composite(glow, layer_img)


def draw_tapered_polyline(draw, points, color, widths):
    if len(points) < 2:
        return
    for i in range(len(points) - 1):
        w = max(1, int((widths[i] + widths[i + 1]) * 0.5))
        draw.line([points[i], points[i + 1]], fill=color, width=w)


def render_arc_slash(layer, t, width, height, basis, env):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    center = point_px(layer.get("center", [0.5, 0.5]), width, height)
    r0, r1 = as_pair(layer.get("radius", 0.34))
    radius = lerp(r0, r1, ease_out_cubic(t)) * basis
    a0, a1 = as_pair(layer.get("angles", [-150, 20]))
    trail = clamp(float(layer.get("trail", 0.6)), 0.02, 1.0)
    reveal = bool(layer.get("reveal", True))
    if reveal:
        head = ease_out_cubic(min(1.0, t / 0.74))
        tail = max(0.0, head - trail)
    else:
        tail, head = 0.0, 1.0
    samples = max(12, int(100 * (head - tail)))
    us = [lerp(tail, head, i / samples) for i in range(samples + 1)]
    points = []
    widths = []
    base_w = float(layer.get("width", 0.055)) * basis
    taper_power = float(layer.get("taper_power", 0.55))
    for i, u in enumerate(us):
        rel = i / max(1, samples)
        ang = math.radians(lerp(a0, a1, u))
        points.append((center[0] + math.cos(ang) * radius, center[1] + math.sin(ang) * radius))
        taper = max(0.04, math.sin(math.pi * rel)) ** taper_power
        widths.append(base_w * taper)
    body = color_rgba(layer.get("color", "#4BB7FFFF"), env)
    core = color_rgba(layer.get("core_color", "#EAF9FFFF"), env)
    d = ImageDraw.Draw(img)
    draw_tapered_polyline(d, points, body, widths)
    core_ratio = clamp(float(layer.get("core_width", 0.24)), 0.04, 1.0)
    draw_tapered_polyline(d, points, core, [w * core_ratio for w in widths])
    return with_glow(img, layer.get("glow", 0.0), basis)


def lightning_points(start, end, segments, jitter_px, rng):
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = max(1e-6, math.hypot(dx, dy))
    nx, ny = -dy / length, dx / length
    pts = [start]
    for i in range(1, segments):
        u = i / segments
        taper = math.sin(math.pi * u)
        off = rng.uniform(-1.0, 1.0) * jitter_px * taper
        pts.append((lerp(start[0], end[0], u) + nx * off, lerp(start[1], end[1], u) + ny * off))
    pts.append(end)
    return pts


def render_lightning(layer, t, width, height, basis, env, seed, frame_index):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    start = point_px(layer.get("from", [0.15, 0.5]), width, height)
    end = point_px(layer.get("to", [0.85, 0.5]), width, height)
    segs = max(4, int(layer.get("segments", 18)))
    jitter = float(layer.get("jitter", 0.04)) * basis
    rng = random.Random(seed + frame_index * 13007)
    flicker = clamp(float(layer.get("flicker", 0.18)), 0.0, 0.95)
    local_env = env * (1.0 - flicker * rng.random())
    pts = lightning_points(start, end, segs, jitter, rng)
    body = color_rgba(layer.get("color", "#65BFFFFF"), local_env)
    core = color_rgba(layer.get("core_color", "#F4FCFFFF"), local_env)
    base_w = max(1, int(float(layer.get("width", 0.012)) * basis))
    d = ImageDraw.Draw(img)
    d.line(pts, fill=body, width=max(2, base_w), joint="curve")
    d.line(pts, fill=core, width=max(1, int(base_w * 0.34)), joint="curve")
    branch_count = max(0, int(layer.get("branches", 4)))
    for b in range(branch_count):
        idx = rng.randint(2, max(2, len(pts) - 3))
        sx, sy = pts[idx]
        ex, ey = end
        main_angle = math.atan2(ey - sy, ex - sx)
        branch_angle = main_angle + rng.choice([-1, 1]) * rng.uniform(0.55, 1.15)
        branch_len = rng.uniform(0.06, 0.16) * basis
        bend = (sx + math.cos(branch_angle) * branch_len, sy + math.sin(branch_angle) * branch_len)
        bpts = lightning_points((sx, sy), bend, max(3, segs // 3), jitter * 0.45, rng)
        d.line(bpts, fill=body, width=max(1, int(base_w * 0.55)))
        d.line(bpts, fill=core, width=max(1, int(base_w * 0.20)))
    return with_glow(img, layer.get("glow", 0.0), basis)


def render_beam(layer, t, width, height, basis, env):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    start = point_px(layer.get("from", [0.12, 0.5]), width, height)
    end = point_px(layer.get("to", [0.88, 0.5]), width, height)
    reveal = clamp(t / max(0.01, float(layer.get("reveal_time", 0.18))))
    reveal = ease_out_cubic(reveal)
    current = (lerp(start[0], end[0], reveal), lerp(start[1], end[1], reveal))
    pulse = float(layer.get("pulse", 0.16))
    cycles = float(layer.get("pulse_cycles", 3.0))
    scale = 1.0 + pulse * math.sin(TAU * (t * cycles))
    w = max(1, int(float(layer.get("width", 0.04)) * basis * scale))
    body = color_rgba(layer.get("color", "#5FD9FFFF"), env)
    core = color_rgba(layer.get("core_color", "#FFFFFFFF"), env)
    d = ImageDraw.Draw(img)
    d.line([start, current], fill=body, width=w)
    d.line([start, current], fill=core, width=max(1, int(w * 0.30)))
    return with_glow(img, layer.get("glow", 0.0), basis)


def render_burst(layer, t, width, height, basis, env, seed):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    center = point_px(layer.get("center", [0.5, 0.5]), width, height)
    r0, r1 = as_pair(layer.get("radius", [0.03, 0.18]))
    radius = lerp(r0, r1, ease_out_cubic(t)) * basis
    body = color_rgba(layer.get("color", "#FFD36AFF"), env)
    core = color_rgba(layer.get("core_color", "#FFFFFFFF"), env)
    d = ImageDraw.Draw(img)
    d.ellipse([center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius], fill=body)
    core_r = radius * 0.32
    d.ellipse([center[0] - core_r, center[1] - core_r, center[0] + core_r, center[1] + core_r], fill=core)
    rays = max(0, int(layer.get("rays", 18)))
    l0, l1 = as_pair(layer.get("ray_length", [0.08, 0.25]))
    w0, w1 = as_pair(layer.get("ray_width_px", [2, 6]))
    rng = random.Random(seed)
    ray_progress = ease_out_cubic(min(1.0, t / 0.58))
    for i in range(rays):
        a = TAU * i / max(1, rays) + rng.uniform(-0.12, 0.12)
        length = rng.uniform(l0, l1) * basis * ray_progress
        inner = radius * rng.uniform(0.35, 0.75)
        x0 = center[0] + math.cos(a) * inner
        y0 = center[1] + math.sin(a) * inner
        x1 = center[0] + math.cos(a) * (inner + length)
        y1 = center[1] + math.sin(a) * (inner + length)
        rw = max(1, int(rng.uniform(w0, w1)))
        d.line([(x0, y0), (x1, y1)], fill=body, width=rw)
    return with_glow(img, layer.get("glow", 0.0), basis)


def render_ring(layer, t, width, height, basis, env, loop):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    center = point_px(layer.get("center", [0.5, 0.5]), width, height)
    r0, r1 = as_pair(layer.get("radius", [0.2, 0.38]))
    radius = lerp(r0, r1, ease_out_cubic(t)) * basis
    pulse = float(layer.get("pulse", 0.0))
    cycles = float(layer.get("pulse_cycles", 1.0 if loop else 2.0))
    phase = math.sin(TAU * t * cycles)
    local_env = env * (1.0 - pulse * 0.35 + pulse * 0.35 * (phase + 1.0))
    ring_w = float(layer.get("width", 0.018)) * basis * (1.0 + pulse * 0.20 * phase)
    color = color_rgba(layer.get("color", "#73E7FFFF"), clamp(local_env))
    d = ImageDraw.Draw(img)
    box = [center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius]
    d.ellipse(box, outline=color, width=max(1, int(ring_w)))
    return with_glow(img, layer.get("glow", 0.0), basis)


def particle_age(t_sec, birth, life, duration, loop):
    age = t_sec - birth
    if loop and age < 0:
        age += duration
    if age < 0 or age > life:
        return None
    return age / max(1e-6, life)


def render_particles(layer, t, width, height, basis, env, seed, duration, loop):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    origin = point_px(layer.get("origin", [0.5, 0.5]), width, height)
    count = max(0, int(layer.get("count", 32)))
    emit0, emit1 = as_pair(layer.get("emit", [0.0, 0.35]))
    life0, life1 = as_pair(layer.get("lifetime", [0.25, 0.65]))
    speed0, speed1 = as_pair(layer.get("speed", [0.15, 0.5]))
    angle0, angle1 = as_pair(layer.get("angle", [0, 360]))
    size0, size1 = as_pair(layer.get("size_px", [2, 7]))
    gravity = layer.get("gravity", [0.0, 0.0])
    gx, gy = float(gravity[0]) * basis, float(gravity[1]) * basis
    jitter = float(layer.get("origin_jitter", 0.0)) * basis
    base_color = layer.get("color", "#A8E6FFFF")
    t_sec = t * duration
    for i in range(count):
        rng = random.Random(seed + i * 4099)
        birth = rng.uniform(emit0, emit1) * duration
        life = rng.uniform(life0, life1)
        age_n = particle_age(t_sec, birth, life, duration, loop)
        if age_n is None:
            continue
        a = math.radians(rng.uniform(angle0, angle1))
        speed = rng.uniform(speed0, speed1) * basis
        age = age_n * life
        ox = origin[0] + rng.uniform(-jitter, jitter)
        oy = origin[1] + rng.uniform(-jitter, jitter)
        x = ox + math.cos(a) * speed * age + 0.5 * gx * age * age
        y = oy + math.sin(a) * speed * age + 0.5 * gy * age * age
        size = lerp(rng.uniform(size0, size1), 0.7, age_n)
        alpha = env * (math.sin(math.pi * clamp(age_n)) ** 0.55)
        c = color_rgba(base_color, alpha)
        r = max(0.5, size)
        d.ellipse([x-r, y-r, x+r, y+r], fill=c)
    return with_glow(img, layer.get("glow", 0.0), basis)



def render_converge(layer, t, width, height, basis, env, seed):
    """Render deterministic particles collapsing from an annulus into a center.

    This is useful for attraction, gravity-well, vacuum and implosion effects where
    ordinary outward particle emitters would communicate the wrong motion.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    center = point_px(layer.get("center", [0.5, 0.5]), width, height)
    count = max(0, int(layer.get("count", 64)))
    r0, r1 = as_pair(layer.get("radius", [0.16, 0.42]))
    end_radius = float(layer.get("end_radius", 0.015))
    size0, size1 = as_pair(layer.get("size_px", [2, 6]))
    swirl_deg = float(layer.get("swirl", 90.0))
    streak = float(layer.get("streak", 0.018)) * basis
    base_color = layer.get("color", "#73CFFFFF")
    core_color = layer.get("core_color", "#EAFBFFFF")
    for i in range(count):
        rng = random.Random(seed + i * 7919)
        start_r = rng.uniform(r0, r1) * basis
        base_a = rng.uniform(0.0, TAU)
        delay = rng.uniform(-0.18, 0.32)
        speed = rng.uniform(0.78, 1.24)
        p = clamp((t - delay) * speed)
        if p <= 0.0:
            continue
        q = p * p * (3.0 - 2.0 * p)
        radius = lerp(start_r, end_radius * basis, q)
        angle = base_a + math.radians(swirl_deg) * q * rng.uniform(0.65, 1.25)
        x = center[0] + math.cos(angle) * radius
        y = center[1] + math.sin(angle) * radius
        prev_q = clamp(q - 0.06)
        prev_r = lerp(start_r, end_radius * basis, prev_q)
        prev_a = base_a + math.radians(swirl_deg) * prev_q * rng.uniform(0.65, 1.25)
        x0 = center[0] + math.cos(prev_a) * prev_r
        y0 = center[1] + math.sin(prev_a) * prev_r
        size = rng.uniform(size0, size1) * (0.75 + 0.45 * q)
        alpha = env * (0.35 + 0.65 * q) * (1.0 - 0.65 * max(0.0, (q - 0.93) / 0.07))
        c = color_rgba(base_color, alpha)
        if streak > 0:
            d.line([(x0, y0), (x, y)], fill=c, width=max(1, int(size * 0.55)))
        r = max(0.6, size)
        d.ellipse([x-r, y-r, x+r, y+r], fill=c)
    # Dense terminal core communicates the sink without relying on particles alone.
    core_r = lerp(0.012, 0.032, math.sin(math.pi * clamp(t)) ** 0.55) * basis
    cd = color_rgba(core_color, env * (0.45 + 0.55 * clamp(t)))
    d.ellipse([center[0]-core_r, center[1]-core_r, center[0]+core_r, center[1]+core_r], fill=cd)
    return with_glow(img, layer.get("glow", 0.02), basis)


def render_smoke(layer, t, width, height, basis, env, seed, duration, loop):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    origin = point_px(layer.get("origin", [0.5, 0.5]), width, height)
    count = max(0, int(layer.get("count", 18)))
    emit0, emit1 = as_pair(layer.get("emit", [0.0, 0.55]))
    life0, life1 = as_pair(layer.get("lifetime", [0.5, 1.2]))
    speed0, speed1 = as_pair(layer.get("speed", [0.02, 0.1]))
    angle0, angle1 = as_pair(layer.get("angle", [210, 330]))
    size0, size1 = as_pair(layer.get("size", [0.035, 0.12]))
    t_sec = t * duration
    for i in range(count):
        rng = random.Random(seed + i * 6151)
        birth = rng.uniform(emit0, emit1) * duration
        life = rng.uniform(life0, life1)
        age_n = particle_age(t_sec, birth, life, duration, loop)
        if age_n is None:
            continue
        age = age_n * life
        a = math.radians(rng.uniform(angle0, angle1))
        speed = rng.uniform(speed0, speed1) * basis
        x = origin[0] + math.cos(a) * speed * age
        y = origin[1] + math.sin(a) * speed * age
        rad = lerp(size0, size1, ease_out_cubic(age_n)) * basis * rng.uniform(0.8, 1.2)
        alpha = env * (math.sin(math.pi * clamp(age_n)) ** 0.85)
        puff = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        pd = ImageDraw.Draw(puff)
        pd.ellipse([x-rad, y-rad, x+rad, y+rad], fill=color_rgba(layer.get("color", "#42546FA0"), alpha))
        blur = float(layer.get("blur", 0.018)) * basis
        if blur > 0:
            puff = puff.filter(ImageFilter.GaussianBlur(blur))
        img = Image.alpha_composite(img, puff)
    return img


def interpolate_point(value, t):
    if isinstance(value, list) and len(value) == 2 and all(isinstance(x, (int, float)) for x in value):
        return value
    if isinstance(value, list) and len(value) == 2 and all(isinstance(x, list) and len(x) == 2 for x in value):
        return [lerp(float(value[0][0]), float(value[1][0]), t), lerp(float(value[0][1]), float(value[1][1]), t)]
    raise ValueError(f"Invalid point animation value: {value!r}")


def interpolate_scalar(value, t):
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, list) and len(value) == 2:
        return lerp(float(value[0]), float(value[1]), t)
    raise ValueError(f"Invalid scalar animation value: {value!r}")


def render_sprite(layer, t, width, height, basis, env, recipe_dir, cache):
    raw_path = layer.get("path")
    if not raw_path:
        raise ValueError("sprite layer requires 'path'")
    path = (recipe_dir / raw_path).resolve() if not Path(raw_path).is_absolute() else Path(raw_path)
    if not path.exists():
        raise FileNotFoundError(f"Sprite not found: {path}")
    key = str(path)
    if key not in cache:
        cache[key] = Image.open(path).convert("RGBA")
    src = cache[key].copy()
    pos = interpolate_point(layer.get("position", [0.5, 0.5]), t)
    scale = interpolate_scalar(layer.get("scale", 0.5), t)
    rotation = interpolate_scalar(layer.get("rotation", 0.0), t)
    opacity_curve = layer.get("opacity_curve", "default")
    local_env = env
    if opacity_curve == "burst":
        local_env *= math.sin(math.pi * clamp(t)) ** 0.55
    target_max = max(1, int(scale * basis))
    factor = target_max / max(src.width, src.height)
    new_size = (max(1, int(src.width * factor)), max(1, int(src.height * factor)))
    src = src.resize(new_size, Image.Resampling.LANCZOS)
    if rotation:
        src = src.rotate(rotation, expand=True, resample=Image.Resampling.BICUBIC)
    if local_env < 0.999:
        a = src.getchannel("A")
        a = ImageEnhance.Brightness(a).enhance(clamp(local_env))
        src.putalpha(a)
    x, y = point_px(pos, width, height)
    layer_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    layer_img.alpha_composite(src, (int(x - src.width / 2), int(y - src.height / 2)))
    return with_glow(layer_img, layer.get("glow", 0.0), basis)


def render_frame(recipe, frame_index, frame_count, recipe_dir, cache):
    canvas = recipe["canvas"]
    width, height = int(canvas["width"]), int(canvas["height"])
    duration = float(canvas["duration"])
    basis = min(width, height)
    loop = bool(recipe.get("loop", False))
    t = frame_index / frame_count if loop else (frame_index / max(1, frame_count - 1))
    base = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    global_seed = int(recipe.get("seed", 1))
    for idx, layer in enumerate(recipe.get("layers", [])):
        timing = layer_timing(layer, t)
        if timing is None:
            continue
        p, env = timing
        if env <= 0:
            continue
        typ = layer.get("type")
        seed = global_seed + idx * 100003
        if typ == "arc_slash":
            out = render_arc_slash(layer, p, width, height, basis, env)
        elif typ == "lightning":
            out = render_lightning(layer, p, width, height, basis, env, seed, frame_index)
        elif typ == "beam":
            out = render_beam(layer, p, width, height, basis, env)
        elif typ == "burst":
            out = render_burst(layer, p, width, height, basis, env, seed)
        elif typ == "ring":
            out = render_ring(layer, p, width, height, basis, env, loop)
        elif typ == "particles":
            out = render_particles(layer, p, width, height, basis, env, seed, duration * (float(layer.get("end", 1)) - float(layer.get("start", 0))), loop)
        elif typ == "converge":
            out = render_converge(layer, p, width, height, basis, env, seed)
        elif typ == "smoke":
            out = render_smoke(layer, p, width, height, basis, env, seed, duration * (float(layer.get("end", 1)) - float(layer.get("start", 0))), loop)
        elif typ == "sprite":
            out = render_sprite(layer, p, width, height, basis, env, recipe_dir, cache)
        else:
            raise ValueError(f"Unknown layer type: {typ!r}")
        base = composite(base, out, layer.get("blend", "normal"))
    return base


def checkerboard(width, height, cell=16):
    img = Image.new("RGB", (width, height), (205, 205, 205))
    d = ImageDraw.Draw(img)
    for y in range(0, height, cell):
        for x in range(0, width, cell):
            if (x // cell + y // cell) % 2:
                d.rectangle([x, y, x + cell - 1, y + cell - 1], fill=(155, 155, 155))
    return img.convert("RGBA")


def make_preview_images(frames, out_path, tile=256):
    if not frames:
        return
    board = Image.new("RGBA", (tile * len(frames), tile), (0, 0, 0, 255))
    for col, frame in enumerate(frames):
        im = frame.copy()
        im.thumbnail((tile, tile), Image.Resampling.LANCZOS)
        bg = checkerboard(tile, tile, max(8, tile // 16))
        x = (tile - im.width) // 2
        y = (tile - im.height) // 2
        bg.alpha_composite(im, (x, y))
        board.alpha_composite(bg, (col * tile, 0))
    board.convert("RGB").save(out_path, quality=95)


def start_webm_encoder(width, height, fps, crf, out_path, deadline="realtime", cpu_used=8):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg not found in PATH")
    cmd = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pixel_format", "rgba",
        "-video_size", f"{width}x{height}", "-framerate", str(fps), "-i", "pipe:0",
        "-an", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
        "-auto-alt-ref", "0", "-row-mt", "1", "-deadline", str(deadline), "-cpu-used", str(cpu_used),
        "-b:v", "0", "-crf", str(crf), "-metadata:s:v:0", "alpha_mode=1",
        str(out_path),
    ]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)


def probe_webm(path):
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return {"available": False}
    cmd = [ffprobe, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name,width,height,pix_fmt,r_frame_rate,duration:stream_tags", "-of", "json", str(path)]
    cp = subprocess.run(cmd, check=True, capture_output=True, text=True)
    data = json.loads(cp.stdout)
    stream = (data.get("streams") or [{}])[0]
    tags = stream.get("tags") or {}
    alpha_mode = tags.get("alpha_mode") or tags.get("ALPHA_MODE")
    return {
        "available": True,
        "codec_name": stream.get("codec_name"),
        "width": stream.get("width"),
        "height": stream.get("height"),
        "pix_fmt": stream.get("pix_fmt"),
        "r_frame_rate": stream.get("r_frame_rate"),
        "duration": stream.get("duration"),
        "alpha_mode": alpha_mode,
    }


def seam_difference(a, b):
    aa = a.convert("RGBA").resize((64, 64), Image.Resampling.BILINEAR)
    bb = b.convert("RGBA").resize((64, 64), Image.Resampling.BILINEAR)
    diff = ImageChops.difference(aa, bb)
    return sum(ImageStat.Stat(diff).mean) / (4 * 255.0)

def validate_recipe(recipe):
    canvas = recipe.setdefault("canvas", {})
    canvas.setdefault("width", 1024)
    canvas.setdefault("height", 1024)
    canvas.setdefault("fps", 30)
    canvas.setdefault("duration", 1.0)
    w, h = int(canvas["width"]), int(canvas["height"])
    fps, duration = int(canvas["fps"]), float(canvas["duration"])
    if not (128 <= w <= 4096 and 128 <= h <= 4096):
        raise ValueError("Canvas width/height must be between 128 and 4096")
    if not (6 <= fps <= 60):
        raise ValueError("FPS must be between 6 and 60")
    if not (0.1 <= duration <= 30):
        raise ValueError("Duration must be between 0.1 and 30 seconds")
    if not recipe.get("layers"):
        raise ValueError("Recipe requires at least one layer")
    recipe.setdefault("name", "fvtt-vfx")
    recipe.setdefault("seed", 1)
    recipe.setdefault("loop", False)
    recipe.setdefault("direction", "none")
    recipe.setdefault("anchor", [0.5, 0.5])
    enc = recipe.setdefault("encoding", {})
    enc.setdefault("crf", 22)
    enc.setdefault("deadline", "good")
    enc.setdefault("cpu_used", 2)
    quality = recipe.setdefault("quality", {})
    # Force high-quality rendering by default: at least 2x supersampling before downscale.
    quality["render_scale"] = max(2, int(quality.get("render_scale", 2)))
    return recipe


def safe_name(name):
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", str(name)).strip("-.")
    return name or "fvtt-vfx"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipe", required=True, help="Path to VFX recipe JSON")
    parser.add_argument("--outdir", required=True, help="Output directory")
    parser.add_argument("--keep-frames", action="store_true", help="Keep rendered PNG frames")
    args = parser.parse_args()

    recipe_path = Path(args.recipe).resolve()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    recipe = validate_recipe(json.loads(recipe_path.read_text(encoding="utf-8")))
    canvas = recipe["canvas"]
    width, height = int(canvas["width"]), int(canvas["height"])
    fps, duration = int(canvas["fps"]), float(canvas["duration"])
    frame_count = max(2, int(round(fps * duration)))
    name = safe_name(recipe["name"])
    quality = recipe.get("quality") or {}
    render_scale = max(2, int(quality.get("render_scale", 2)))
    render_recipe = copy.deepcopy(recipe)
    render_recipe["canvas"]["width"] = width * render_scale
    render_recipe["canvas"]["height"] = height * render_scale

    webm_path = outdir / f"{name}.webm"
    preview_path = outdir / f"{name}.preview.png"
    manifest_path = outdir / f"{name}.manifest.json"
    frames_dir = outdir / f"{name}.frames" if args.keep_frames else None
    if frames_dir:
        if frames_dir.exists():
            shutil.rmtree(frames_dir)
        frames_dir.mkdir(parents=True)

    enc = recipe.get("encoding") or {}
    crf = int(enc.get("crf", 22))
    deadline = str(enc.get("deadline", "good"))
    cpu_used = int(enc.get("cpu_used", 2))
    proc = start_webm_encoder(width, height, fps, crf, webm_path, deadline=deadline, cpu_used=cpu_used)
    if proc.stdin is None:
        raise RuntimeError("Could not open ffmpeg stdin")

    preview_indices = sorted(set(round(i * (frame_count - 1) / 5) for i in range(6)))
    previews = []
    cache = {}
    alpha_min, alpha_max = 255, 0
    has_transparent = False
    has_visible = False
    peak_idx, peak_sum, peak_bbox = 0, -1, None
    first_frame = None
    last_frame = None

    print(f"Rendering {frame_count} frames at {width}x{height}, {fps} fps (forced HQ render_scale={render_scale}, internal={width * render_scale}x{height * render_scale})...")
    try:
        for i in range(frame_count):
            im = render_frame(render_recipe, i, frame_count, recipe_path.parent, cache)
            if render_scale != 1:
                im = im.resize((width, height), Image.Resampling.LANCZOS)
            a = im.getchannel("A")
            extrema = a.getextrema()
            alpha_min = min(alpha_min, extrema[0])
            alpha_max = max(alpha_max, extrema[1])
            has_transparent = has_transparent or extrema[0] < 255
            has_visible = has_visible or extrema[1] > 0
            total = ImageStat.Stat(a).sum[0]
            if total > peak_sum:
                peak_sum = total
                peak_idx = i
                peak_bbox = a.getbbox()
            if i == 0:
                first_frame = im.copy()
            if i == frame_count - 1:
                last_frame = im.copy()
            if i in preview_indices:
                previews.append(im.copy())
            if frames_dir:
                im.save(frames_dir / f"frame_{i:04d}.png", compress_level=3)
            proc.stdin.write(im.tobytes())
        proc.stdin.close()
        stderr = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
        rc = proc.wait()
        if rc != 0:
            raise RuntimeError(f"ffmpeg failed with exit code {rc}: {stderr.strip()}")
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass
        raise

    make_preview_images(previews, preview_path)
    seam = seam_difference(first_frame, last_frame) if first_frame is not None and last_frame is not None else None
    metrics = {
        "alpha_min": alpha_min,
        "alpha_max": alpha_max,
        "has_transparent_pixels": has_transparent,
        "has_visible_pixels": has_visible,
        "peak_frame": peak_idx,
        "peak_alpha_bbox": list(peak_bbox) if peak_bbox else None,
        "seam_difference": round(seam, 5) if seam is not None else None,
    }
    probe = probe_webm(webm_path)

    bbox = metrics.get("peak_alpha_bbox")
    margin = None
    touches = None
    if bbox:
        l, top, r, bottom = bbox
        margin = {
            "left": round(l / width, 4),
            "top": round(top / height, 4),
            "right": round((width - r) / width, 4),
            "bottom": round((height - bottom) / height, 4),
        }
        touches = any(v < 0.02 for v in margin.values())

    warnings = []
    if not metrics["has_visible_pixels"]:
        warnings.append("No visible pixels were rendered.")
    if not metrics["has_transparent_pixels"]:
        warnings.append("Frames do not contain transparent pixels.")
    if touches:
        warnings.append("Peak-frame content is within 2% of a canvas edge; check for clipping.")
    if recipe.get("loop") and metrics.get("seam_difference") is not None and metrics["seam_difference"] > 0.12:
        warnings.append("Loop seam difference is high; inspect the last-to-first transition.")
    if probe.get("available") and probe.get("codec_name") != "vp9":
        warnings.append(f"Unexpected codec: {probe.get('codec_name')}")
    if probe.get("available") and str(probe.get("alpha_mode")) != "1":
        warnings.append("ffprobe did not report alpha_mode=1; verify browser alpha playback.")

    manifest = {
        "name": name,
        "canvas": {"width": width, "height": height, "fps": fps, "duration": duration, "frames": frame_count},
        "quality": {"render_scale": render_scale, "forced_hq": True},
        "loop": bool(recipe.get("loop", False)),
        "direction": recipe.get("direction", "none"),
        "anchor": recipe.get("anchor", [0.5, 0.5]),
        "fvtt": recipe.get("fvtt", {}),
        "encoding": {"codec": "vp9", "pixel_format_request": "yuva420p", "crf": crf, "deadline": deadline, "cpu_used": cpu_used, "alpha": True},
        "validation": {**metrics, "peak_safe_margin": margin, "touches_edge": touches, "ffprobe": probe, "warnings": warnings, "ok": len(warnings) == 0},
        "files": {"webm": webm_path.name, "preview": preview_path.name},
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    size_mb = webm_path.stat().st_size / (1024 * 1024)
    print(f"WebM: {webm_path} ({size_mb:.2f} MiB)")
    print(f"Preview: {preview_path}")
    print(f"Manifest: {manifest_path}")
    print(f"Validation: {'OK' if not warnings else 'WARN'}")
    for warning in warnings:
        print(f"  - {warning}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"External command failed with exit code {exc.returncode}") from exc
    except Exception as exc:
        raise SystemExit(f"Build failed: {exc}") from exc
