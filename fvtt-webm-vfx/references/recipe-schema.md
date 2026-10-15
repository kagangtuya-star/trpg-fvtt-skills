# 配方 JSON 格式

`build_vfx.py` 接受一个 JSON 配方。除 `name` 外大多数字段都有默认值。

## 顶层

```json
{
  "name": "lightning-slash",
  "canvas": {"width": 1024, "height": 1024, "fps": 30, "duration": 0.9},
  "loop": false,
  "seed": 42,
  "direction": "left-to-right",
  "anchor": [0.5, 0.5],
  "encoding": {"crf": 28, "deadline": "realtime", "cpu_used": 8},
  "fvtt": {"kind": "effect", "recommended_playback": "once"},
  "layers": []
}
```

坐标、半径、宽度、速度等优先使用相对画布的归一化值；脚本中明确标成 `*_px` 的字段才使用像素。颜色接受 `#RRGGBB`、`#RRGGBBAA` 或 `[r,g,b,a]`。`encoding.deadline` 与 `cpu_used` 用于控制 VP9 编码速度；聊天环境默认 `realtime / 8`，需要更慢的高质量编码时可改为 `good` 并降低 `cpu_used`。

## 公共层字段

每层可使用：

```json
{
  "type": "...",
  "start": 0.0,
  "end": 1.0,
  "fade_in": 0.08,
  "fade_out": 0.25,
  "opacity": 1.0,
  "blend": "normal",
  "glow": 0.02
}
```

`start/end` 是总时长的归一化比例。`fade_in/fade_out` 是该层局部生命周期的比例。`blend` 支持 `normal` 或 `add`。`glow` 是相对最短边的高斯模糊半径。

## arc_slash

```json
{
  "type": "arc_slash",
  "center": [0.50, 0.52],
  "radius": [0.18, 0.40],
  "angles": [-155, 20],
  "width": 0.055,
  "trail": 0.55,
  "reveal": true,
  "color": "#4BB7FFFF",
  "core_color": "#E8FAFFFF",
  "core_width": 0.28,
  "glow": 0.018,
  "taper_power": 0.55
}
```

`radius` 可为单值或 `[start,end]`。`trail` 控制展开时可见弧长比例。角度单位为度。

## lightning

```json
{
  "type": "lightning",
  "from": [0.16, 0.52],
  "to": [0.84, 0.48],
  "segments": 18,
  "jitter": 0.045,
  "branches": 5,
  "width": 0.012,
  "color": "#65BFFFFF",
  "core_color": "#F4FCFFFF",
  "flicker": 0.25,
  "glow": 0.025
}
```

闪电每帧会在固定 seed 基础上做受控抖动；不要用极高 `jitter` 代替清晰主路径。

## beam

```json
{
  "type": "beam",
  "from": [0.12, 0.50],
  "to": [0.88, 0.50],
  "width": 0.04,
  "pulse": 0.18,
  "color": "#5FD9FFFF",
  "core_color": "#FFFFFFFF",
  "glow": 0.03
}
```

## burst

```json
{
  "type": "burst",
  "center": [0.5, 0.5],
  "radius": [0.03, 0.18],
  "rays": 20,
  "ray_length": [0.08, 0.27],
  "ray_width_px": [2, 7],
  "color": "#FFD36AFF",
  "core_color": "#FFFFFFFF",
  "glow": 0.025
}
```

## ring

```json
{
  "type": "ring",
  "center": [0.5, 0.5],
  "radius": [0.18, 0.38],
  "width": 0.018,
  "pulse": 0.12,
  "color": "#73E7FFFF",
  "glow": 0.016
}
```

循环光环可把半径固定，并使用 `pulse` 做周期亮度/线宽变化。

## particles

```json
{
  "type": "particles",
  "origin": [0.5, 0.5],
  "count": 38,
  "emit": [0.0, 0.35],
  "lifetime": [0.25, 0.65],
  "speed": [0.18, 0.55],
  "angle": [-15, 195],
  "gravity": [0.0, 0.10],
  "size_px": [2, 8],
  "color": "#8EDBFFFF",
  "glow": 0.008
}
```

速度和重力以“画布最短边/秒”为尺度。

## converge

```json
{
  "type": "converge",
  "center": [0.5, 0.5],
  "count": 72,
  "radius": [0.18, 0.42],
  "end_radius": 0.015,
  "swirl": 110,
  "streak": 0.018,
  "size_px": [2, 6],
  "color": "#4EBFFFFF",
  "core_color": "#E9FAFFFF",
  "glow": 0.024
}
```

用于吸引、坍缩、重力井、真空收束等“运动方向指向中心”的效果。`radius` 是粒子初始环带，`end_radius` 是收束终点，`swirl` 控制向内运动时的旋转角度，避免把吸引效果错误地画成向外喷射。

## smoke

```json
{
  "type": "smoke",
  "origin": [0.5, 0.54],
  "count": 18,
  "emit": [0.0, 0.55],
  "lifetime": [0.5, 1.2],
  "speed": [0.02, 0.10],
  "angle": [210, 330],
  "size": [0.035, 0.12],
  "color": "#42546FA0",
  "blur": 0.018
}
```

## sprite

```json
{
  "type": "sprite",
  "path": "./wolf-head.png",
  "position": [[0.38, 0.52], [0.62, 0.50]],
  "scale": [0.45, 0.75],
  "rotation": [-8, 5],
  "opacity_curve": "burst",
  "glow": 0.015
}
```

`path` 相对配方文件解析。`position` 可以是固定 `[x,y]` 或起终点 `[[x0,y0],[x1,y1]]`。
