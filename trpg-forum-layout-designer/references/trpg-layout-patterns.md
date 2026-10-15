# TRPG Layout Patterns and Aesthetic Notes

All patterns must be implemented as GF/SMF-compatible `[font=;css]` layouts. In default Strict Mode, build from one outer shell and one inner stage. Use vertical flow, chips, and cards rather than web-style multi-column components.

## Institution dossier

Use for SCP-like, 三角机构, occult bureau, military archive, containment, or investigation posts.

Strict structure:

1. outer shell and inner stage
2. classification header band
3. title/designation card
4. metadata chips: project id, level, team size, duration
5. briefing paragraph cards
6. research/progress timeline as vertical cards
7. directives / optional tasks as reward cards
8. warning footer

Aesthetic: dark brown/black base, red danger accents, muted gold borders. Express this through bounded header bands, chip rows, section dividers, timeline cards, directive boxes, and warning footer. Avoid all-black fields and page-wide overlays.

## Creature archive

Use for monsters, bestiary entries, ecology notes, or anomaly organisms.

Strict structure:

1. name and epithet in a title card
2. taxonomy/threat chips
3. centered image block if supplied
4. habitat, behavior, and observed abilities as vertical trait cards
5. evidence notes
6. GM-facing hooks or optional objectives

Aesthetic: parchment/specimen card, green/brown/gold accents, narrow left borders. Do not float images or put images beside text with `calc()`; stack vertically.

## Campaign log

Use for session reports and recaps.

Strict structure:

1. campaign title and session number
2. date/location/participants chip row
3. short recap card
4. key events as stacked cards
5. clues, unresolved threads, next session objectives

Aesthetic: ledger, journal, travelogue, or archive index. Use chapter cards, chronological separators, clue boxes, and next-session agenda panels.

## Recruitment post

Use for opening a group or recruiting players.

Strict structure:

1. hook banner
2. system/platform/time/slots/tone chips
3. campaign premise card
4. player requirements cards
5. application template block
6. content/safety notes

Aesthetic: clear and functional before decorative. Use chips for constraints and boxed forms for applications. Avoid dense multi-column listings.

## Handout / evidence

Use for letters, clues, in-world documents, prophecy, lab notes, police reports, map captions.

Strict structure:

1. document title
2. authenticity/source label
3. body in paper card
4. marginal notes as vertical side-note blocks, not actual positioned margins
5. footer stamp

Aesthetic: paper color, subtle border, serif font, restrained shadows. Redaction strips may be made from inline `[font=;display:inline-block;background:#111;color:#111;]████[/font]` blocks, but keep them inside normal text flow.

## Optional tasks / reward blocks

For TRPG mission rewards or optional objectives, use vertical reward cards:

```bbcode
[font=;display:block;margin:18px 0 8px 0;color:#e6bd72;font-size:16px;line-height:1.35;font-weight:bold;letter-spacing:2px;border-bottom:2px solid #9b0000;padding-bottom:5px;]TA-3844 可选任务[/font]
[font=;display:block;margin:0 0 8px 0;padding:12px 14px;background:#22130f;border-left:5px solid #b98a4b;border-top:1px solid #5f432a;border-bottom:1px solid #5f432a;color:#f3ead8;font-size:13px;line-height:1.7;box-sizing:border-box;]
[font=;display:inline-block;padding:2px 8px;margin-right:8px;background:#5a0000;border:1px solid #d0aa66;color:#fff1d0;font-size:12px;line-height:1.4;font-weight:bold;]1嘉奖[/font]
Objective text.
[/font]
```

## Style palette examples

- containment bureau: `#18110d`, `#2b0d0d`, `#8b0000`, `#b98a4b`, `#f3ead8`
- parchment archive: `#f3ead8`, `#fff8e8`, `#7a3b16`, `#b4884d`, `#211610`
- arcane academy: `#151122`, `#30204a`, `#9f7aea`, `#d9c7ff`, `#f5efff`
- nautical expedition: `#0d1f2a`, `#18384a`, `#6fb3c8`, `#d7c49e`, `#f2ead5`
- cyber terminal: `#071111`, `#0f2d2d`, `#39ffca`, `#a8fff1`, `#e8fffb`

## Tone mapping

- horror/investigation: dense metadata, warning blocks, restrained red accents.
- heroic fantasy: warm gold, parchment, framed headings.
- science/ecology: specimen labels, observation blocks, progress timeline.
- absurd/comedic: formal bureaucratic structure with intentionally incongruent content.

## Creative breakthrough mode

When the user invokes “创意突破模式” or “突破模板”, explore variants beyond the skeleton. Good creative moves:

- unusual palette or genre hybrid
- more dramatic header typography
- asymmetrical but still bounded accent bars
- nested paper-on-dossier composition
- more elaborate reward cards or stamps
- icon-like glyphs using plain text symbols

Do not introduce page-level CSS behavior, raw HTML, JavaScript, or hostile overlay effects. For any risky BBCode feature, state the risk and provide a Strict Mode fallback.
