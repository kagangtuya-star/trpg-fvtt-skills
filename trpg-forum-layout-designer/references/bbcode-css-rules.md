# BBCode CSS Rules for SMF / GoddessFantasy Posts

## GF/SMF Strict Mode is the default

For GoddessFantasy, SMF, or unknown BBCode forums, design for the parser actually used by the forum, not for standard browser HTML/CSS. Default to a sealed stage structure: one outer shell, one inner shell, visible child blocks inside that stage.

Strict Mode priorities:

1. Use `[font=;css]...[/font]` as the core visual mechanism.
2. Keep content in normal document flow.
3. Use a single bounded container, not a component-like web page layout.
4. Use `font-size:0;line-height:0` on structural shells and explicitly restore text metrics on visible children.
5. Avoid `[spoiler]`, `[quote]`, `[list]`, `[table]`, `[center]`, `calc()`, columns, viewport units, positioning, and page-wide effects unless the user explicitly asks and accepts risk.

## Strict Mode skeleton

```bbcode
[font=;display:block;width:96%;max-width:900px;margin:8px auto;padding:6px;box-sizing:border-box;overflow:hidden;background:#18110d;border:1px solid #b98a4b;font-size:0;line-height:0;]
[font=;display:block;padding:8px;box-sizing:border-box;overflow:hidden;background:#241711;border:1px solid #5f432a;font-size:0;line-height:0;]

[font=;display:block;padding:12px;background:#5a0000;border-bottom:1px solid #b98a4b;text-align:center;font-size:0;line-height:0;]
[font=;display:block;color:#fff2d0;font-size:24px;line-height:1.25;font-weight:bold;letter-spacing:2px;]Title[/font]
[font=;display:block;margin-top:4px;color:#ffe3a6;font-size:11px;line-height:1.3;letter-spacing:2px;]Subtitle[/font]
[/font]

[font=;display:block;padding:14px 16px;color:#f3ead8;font-size:13px;line-height:1.75;]
Content
[/font]

[/font][/font]
```

## Why shells use font-size:0

SMF/GF BBCode parsing can introduce line breaks, inherited font sizing, and spacing between nested generated tags. Use `font-size:0;line-height:0` on layout shells to suppress accidental whitespace. Every text-bearing child must restore `font-size` and `line-height`, for example:

```bbcode
[font=;display:block;font-size:13px;line-height:1.75;color:#f3ead8;]Readable text[/font]
```

## Safe outer shell

Use this shape for most layouts. Do not wrap it with `[center]` by default.

```bbcode
[font=;display:block;width:96%;max-width:900px;margin:8px auto;padding:6px;background:#18110d;color:#f3ead8;border:1px solid #b98a4b;box-shadow:0 0 12px rgba(0,0,0,0.35);box-sizing:border-box;overflow:hidden;font-size:0;line-height:0;]
...inner stage...
[/font]
```

## Safe inner stage

```bbcode
[font=;display:block;padding:8px;background:#241711;border:1px solid #5f432a;box-sizing:border-box;overflow:hidden;font-size:0;line-height:0;]
...visible child blocks...
[/font]
```

## Safe section block

```bbcode
[font=;display:block;margin:18px 0 8px 0;color:#e6bd72;font-size:16px;line-height:1.35;font-weight:bold;letter-spacing:2px;border-bottom:2px solid #9b0000;padding-bottom:5px;]Section Title[/font]
[font=;display:block;margin:0 0 10px 0;padding:12px 14px;background:#241711;border-left:5px solid #b00000;border-top:1px solid #5f432a;border-bottom:1px solid #5f432a;color:#f3ead8;font-size:13px;line-height:1.75;box-sizing:border-box;]
Body text.
[/font]
```

## Metadata chips

Use `inline-block` chips because they wrap on narrow posts and do not require column math.

```bbcode
[font=;display:inline-block;padding:5px 10px;margin:3px 6px 3px 0;background:#8b0000;border:1px solid #d0aa66;color:#fff6de;font-size:12px;line-height:1.4;font-weight:bold;]项目编号 TA-3844[/font]
```

Place chip rows inside a visible parent that restores metrics:

```bbcode
[font=;display:block;padding:10px 12px;background:#2b0d0d;border-bottom:1px solid #b98a4b;font-size:0;line-height:0;]
...chips...
[/font]
```

## Images

Images are safer as centered vertical elements than as floated or two-column layouts. Use simple wrappers:

```bbcode
[font=;display:block;text-align:center;margin:8px 0 12px 0;font-size:13px;line-height:1.4;]
[img width=420]IMAGE_URL[/img]
[/font]
```

Do not use `float`, `position`, or `width:calc(...)` to place text beside images in production GF/SMF BBCode.

## High-risk block BBCode

Treat these as high-risk inside long styled containers:

- `[spoiler]`
- `[quote]`
- `[list]`
- `[table]`

They can make SMF generate its own nested HTML and break the surrounding `[font=;css]` structure.

If collapsible content is required:

1. Stable option: use titled content blocks instead of `[spoiler]`.
2. Medium-risk option: close all styled `[font]` containers before `[spoiler]`, then reopen styling after it.
3. High-risk option: nest `[spoiler]` inside styled containers only after the user explicitly accepts compatibility risk.

Never nest `[spoiler]` inside multiple `[font=;css]` levels in Strict Mode.

## Avoid calc and columns

Avoid `calc()` in production BBCode. Do not use structures such as:

```css
width:calc(100% - 210px)
```

Avoid two-column layouts unless explicitly requested. Use vertical stacking, metadata chips, and content cards instead.

## Forbidden production properties

Do not use these in normal post layouts:

- `position:fixed`
- `position:absolute`
- `z-index`
- `top`, `left`, `right`, `bottom`
- viewport units such as `100vw`, `100vh`
- `transform`
- negative margins for escape effects
- `box-shadow:0 0 0 9999px ...`
- `filter`, `backdrop-filter`
- `pointer-events`
- `animation`
- page-wide backgrounds or overlays

These can escape the post area, cover the forum UI, or black-screen mobile browsers.

## Permitted advanced effects

Use advanced font-css effects only inside the bounded stage:

- nested framed shells
- header bands
- metadata chips
- title hierarchy using font size, weight, and letter spacing
- side borders and section dividers
- warning ribbons
- paper or dossier cards
- small shadows such as `box-shadow:0 2px 8px rgba(0,0,0,0.35)`
- restrained text shadows
- simple color blocks

Do not confuse “advanced” with “page-level web layout”.

## Closure sanity check

Before final output:

- No `</font>` may appear.
- Every `[font=;...]` and `[font]` must close with `[/font]`.
- Never mix HTML-style closing tags with BBCode.
- Do not allow visible `[/font]` text to remain in output.
- Avoid `[spoiler]`, `[quote]`, `[table]`, and `[list]` inside styled containers in Strict Mode.
- Avoid `calc()`, `position`, viewport units, transforms, and negative margins.
- If a parent has `font-size:0;line-height:0`, every text-bearing child restores `font-size` and `line-height`.

## Failure recovery

When a user reports overflow, exposed closing tags, broken spoilers, page-wide bars, mobile black screens, or hidden text:

1. Discard the previous component structure.
2. Rebuild from the Strict Mode skeleton.
3. Keep one outer shell and one inner stage.
4. Remove `[center]`, `[spoiler]`, `[quote]`, `[list]`, `[table]`, `calc()`, columns, and complex width math.
5. Use only `[font=;css]`, `[img]`, `[b]`, `[i]`, and `[url]` unless the user approves otherwise.
6. Provide the stable version first; decorative enhancements can follow.
