---
name: trpg-forum-layout-designer
description: "gf/smf-compatible bbcode layout design for trpg forum posts that must use [font=;css] inline styling as the primary medium. use when the user asks to typeset, beautify, redesign, or convert trpg announcements, modules, creature entries, campaign logs, mission briefs, handouts, rules notes, or forum posts for goddessfantasy/smf bbcode. default to strict compatibility: bounded in-post layouts, single-shell stage structure, no page-wide effects, no html tags, no complex web-css assumptions. support a user-invoked creative override while still warning about compatibility risk."
---

# TRPG Forum Layout Designer

Design TRPG forum post layouts for GoddessFantasy / SMF BBCode where visual styling is embedded through `[font=;css]...[/font]`. Treat `[font=;css]` as the required expressive medium, but treat GF/SMF compatibility as the top priority. The default deliverable is production-ready BBCode that stays inside the original post area.

## First-use prompt

When first applying this skill in a conversation, briefly tell the user: default output uses **GF/SMF Strict Mode**, which prioritizes real forum compatibility over component-like web CSS. Also tell the user they can explicitly request **“创意突破模式”** to loosen template constraints and explore more ambitious font-css composition, with compatibility caveats.

Do not repeat this prompt on every minor revision unless the user changes mode or asks about the design constraints.

## Core priority order

1. Preserve GF/SMF rendering stability.
2. Keep the layout inside the post boundary.
3. Use `[font=;css]` as the main visual mechanism.
4. Build clear TRPG visual hierarchy.
5. Add advanced decorative effects only after structure is stable.

Advanced visual styling is encouraged only after structural stability. If the user reports overflow, exposed BBCode tags, spoiler breakage, or page-wide blocks, switch immediately to Strict Mode and reduce complexity. Stable rendering takes priority over visual richness.

## GoddessFantasy / SMF Strict Mode

When the target platform is GoddessFantasy, SMF, or an unknown BBCode forum, default to Strict Mode.

Strict Mode rules:

1. Use one outer `[font=;css]` shell and one inner stage shell.
2. The outer and inner shells should use `font-size:0;line-height:0;overflow:hidden;box-sizing:border-box;`.
3. Every visible child block must explicitly restore `font-size` and `line-height`.
4. Avoid component-style multi-shell layouts. Keep all main content inside one bounded container.
5. Prefer vertical block flow over columns, tables, or calculated widths.
6. Do not wrap the whole layout in `[center]` by default. Use `margin:8px auto` on the outer shell and `text-align:center` only on specific child blocks.
7. Avoid `calc()` in production BBCode. Do not use layouts such as `width:calc(100% - 210px)`.
8. Avoid two-column layouts unless the user explicitly asks for them. Use centered image + vertical metadata chips instead.
9. Avoid `[spoiler]`, `[quote]`, `[list]`, and `[table]` inside styled containers unless the user explicitly accepts risk.
10. Do not use raw HTML. Never output `</font>`.

## Strict Mode Skeleton

Use this skeleton for GF/SMF-compatible layouts:

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

This skeleton is not an aesthetic ceiling. It is the compatibility baseline. Decorate by adding bounded child blocks that restore `font-size` and `line-height`, not by adding page-level web layout behavior.

## Creative override command

If the user says **“创意突破模式”**, **“突破模板”**, **“超越模板”**, or equivalent, you may propose bolder visual compositions. Even then:

- Keep the output in the post boundary unless the user explicitly asks for defensive analysis of broken layouts.
- Explain which parts have higher GF/SMF compatibility risk.
- Provide either a Strict Mode fallback or mark the risky version clearly.
- Never use HTML closing tags, JavaScript, external CSS, or assets that the user has not supplied.

## Operating workflow

First identify the input type: announcement, module pitch, creature/stat block, faction dossier, mission brief, investigation handout, session log, rules note, recruitment post, archive index, or custom forum block.

If content, target mood, forum constraints, or desired output granularity are unclear, ask concise clarifying questions. Prefer confirming: input content, desired visual style, whether images are included, and whether the user wants design plan first or final BBCode directly.

Then choose a layout pattern:

- Mission / institution dossier: header strip, metadata chips, designation card, briefing sections, directive boxes, warning footer.
- Creature / anomaly entry: title card, taxonomy/meta chips, trait blocks, observation notes, reward/optional objective section.
- Campaign log: dated chapter cards, recap summary, unresolved clues, next-session agenda.
- Recruitment post: hook, system/table info, schedule, requirements, application form, safety notes.
- Handout / letter: paper card, source label, body block, marginal notes, seals, redactions.

Then choose a visual direction. Use 2-4 dominant colors. Favor high contrast over decorative complexity. Express the direction with visible but bounded font-css craft: framed shells, header bands, chips, section dividers, card backgrounds, inset notes, warning ribbons, and small shadows.

Finally output BBCode in one fenced block unless the user asks for a design plan only. If useful, add a short insertion note such as “place this block after 行动指令摘录”.

## Standard BBCode compatibility

Standard BBCode such as `[b]`, `[i]`, `[color]`, `[size]`, `[url]`, and `[img]` may support the design. Treat `[spoiler]`, `[quote]`, `[list]`, and `[table]` as high-risk block BBCode on SMF/GoddessFantasy. Do not place them inside long or deeply nested `[font=;css]` containers unless the user explicitly accepts compatibility risk. If collapsible content is required, either close all styled containers before the spoiler, or provide a non-spoiler stable version.

## Collapsible Content Policy

When the user requests `[spoiler]`:

- Safe option: do not use `[spoiler]`; use titled content blocks instead.
- Medium-risk option: close all styled `[font]` containers before `[spoiler]`, then reopen styling after it.
- High-risk option: place `[spoiler]` inside styled containers only if the user explicitly accepts the risk.

Never nest `[spoiler]` inside multiple `[font=;css]` levels in GF/SMF Strict Mode.

## Production CSS constraints

Use stable properties for in-boundary effects: `display`, `width`, `max-width`, `margin`, `padding`, `background`, `background-color`, simple `linear-gradient` only when not essential, `color`, `font-family`, `font-size`, `font-weight`, `letter-spacing`, `line-height`, `border`, `border-left`, `border-bottom`, small `box-shadow`, restrained `text-shadow`, `text-align`, `box-sizing`, `overflow:hidden`, and `inline-block`.

Use `display:table/table-row/table-cell` only when the user needs tabular data and the structure is short. Prefer vertical blocks and metadata chips.

Avoid fragile properties in production BBCode: `calc()`, viewport units, fixed/absolute positioning, transforms, negative margins, huge shadows, filters, backdrop-filter, animation, pointer-events, page-wide backgrounds, and complicated column math.

## Failure recovery

If the user reports overflow, exposed closing tags, broken spoiler blocks, page-wide bars, or black-screen effects:

1. Stop using `[spoiler]`, `[quote]`, `[center]`, `calc()`, columns, table-like layouts, and complex inline-block width math.
2. Rebuild from the Strict Mode Skeleton.
3. Keep all content inside one outer shell and one inner stage shell.
4. Use only `[font=;css]`, `[img]`, `[b]`, `[i]`, and `[url]` unless the user explicitly requests otherwise.
5. Provide a plain stable version before attempting decorative enhancements.

## BBCode closure sanity check

Before final output, run a BBCode compatibility check:

- No `</font>` may appear.
- Every `[font=;...]` and `[font]` must close with `[/font]`.
- Never mix HTML-style closing tags with BBCode.
- Do not allow visible `[/font]` text to remain in the output.
- Are all large visual sections inside the same outer shell?
- Are there any `[spoiler]`, `[quote]`, `[table]`, or `[list]` inside styled containers?
- Are there any `calc()`, `position`, viewport units, or negative margins?
- Does every text-bearing child restore `font-size` and `line-height` if the parent uses `font-size:0;line-height:0`?

## Output standards

A complete output should normally include visible font-css composition, not a minimally styled wrapper. In Strict Mode, this means one bounded stage with child blocks that restore text metrics. It should normally include:

1. Outer shell and inner stage shell.
2. Header title block.
3. Metadata chips or short vertical metadata cards.
4. Main content sections with clear headings.
5. Optional objective/reward blocks when supplied.
6. Footer/warning/notice block.

Preserve user text unless asked to rewrite. Correct only obvious spacing/punctuation issues when necessary for readability.

## References

Consult `references/bbcode-css-rules.md` for strict GF/SMF compatibility rules and safe CSS patterns.
Consult `references/trpg-layout-patterns.md` for reusable structures and aesthetics.
