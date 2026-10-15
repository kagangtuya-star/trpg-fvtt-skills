---
name: trpg-circular-token
description: >-
  Create circular D&D/TRPG/VTT character tokens or standalone empty token frames. Use for round tokens, token rings, portrait compositing, transparent token borders, 单独设计Token框, 只要边框, or 根据文本描述设计Token框. Support three modes: faithful complete tokens from character art; frame-only design from an image, existing token, or border requirements; and frame-only design from text details, character information, class, faction, or story without an image. Frame-only output has a transparent center and exterior, with no character or inner background. Preserve source identity in complete-token mode. Use a text-first workflow: present numbered schemes for each new source image or frame brief, then render after a later user message selects or approves a scheme.
---

# TRPG Circular Token

Create 1:1 circular VTT character tokens or reusable standalone token frames. Route the request before proposing designs; an uploaded character image does not automatically mean the user wants a complete token.

## Mode selection

| Mode | When to use | Deliverable |
| --- | --- | --- |
| **Complete token** | The user wants a finished character token from character art or an existing token. | Source-faithful character, circular rim, inner background, and optional controlled pop-out; transparent exterior. |
| **Standalone frame** | The user asks for “单独设计Token框”, “只要框/边框”, “空框”, a reusable border, or a frame based on an uploaded character/token/frame reference or direct border specifications. | A circular frame asset only, with both the center opening and exterior transparent. Any character reference supplies design cues, not content to composite. |
| **Text-described frame** | The user asks for a frame based on text details, character information, race, class, faction, equipment, story, or mood, without requiring an image. | A circular frame asset only, translating the text into rim materials, motifs, colors, and ornament. No character illustration or inner background. |

Explicit frame-only intent takes priority over complete-token defaults, including when a portrait is attached. Direct construction requirements such as “银色金属圆框、顶部月石” fit standalone frame mode; a character brief such as “月神牧师、银白、月石、藤蔓” fits text-described frame mode. Mixed frame briefs can combine both sources without asking the user to choose a label.

Do not infer a frame request from character information alone: if there is no image and it is unclear whether the user wants an empty frame or a complete character token, ask which deliverable they want. When frame intent is explicit, proceed without asking for a character image. Do not create a new character from text in place of a requested frame.

Runtime must be pure ChatGPT image analysis plus ChatGPT image generation/editing only in the rendering stage. Do not use scripts, code execution, external image-processing programs, command-line workflows, or bundled assets.

## Absolute interaction rule

Use a mandatory two-turn design-then-render workflow for every new source image or frame brief in all three modes. There is no first-turn render shortcut.

On the first turn with a usable source image/token, frame requirements, or text-only frame brief, if there is no previously approved scheme for that task and output mode, respond with text-only design options. Do not call image generation/editing. Do not output a generated image. Do not silently proceed to render.

Treat requests such as "设计token方案", "给token方案", "设计方案", "先看看怎么做", "帮我分析这个token", or equivalent wording as Stage 1 only. These phrases request a written design proposal, not image generation.

Even if the user says "generate directly", "you choose and draw now", "auto-pick", "直接画", or similar in the same first message as a new source image or frame brief, still provide text-only schemes first and ask for confirmation. The user must send a later message choosing or approving a scheme before rendering.

Only invoke image generation/editing when both conditions are true: (1) this conversation already contains a prior assistant response with numbered design schemes for the same source image or frame brief and requested output mode, and (2) the user's latest message explicitly chooses a scheme number, approves a scheme, requests a specific combination of existing schemes, or says to proceed after seeing the text options.

## Stage 1: text-only design selection

Inspect the available image or text brief and provide 3 to 5 numbered design schemes for the selected mode when none has been approved yet. Frame-only modes do not require an image.

Stage 1 must be normal text only. Never call image generation/editing during Stage 1. Never attach or produce an image during Stage 1. The response should be a concise written menu of design choices.

Each scheme must be concise and actionable. For complete tokens, include:

- **scheme name**: short fantasy-token label.
- **rim design**: circular border motif and material.
- **inner background**: atmosphere contained inside the circle.
- **lighting/integration**: subtle effect used to unify the source image with the token.
- **controlled pop-out plan**: which existing visible part may sit slightly in front of or beyond the rim, such as hair, hood, head, shoulder, horn, wing, cape edge, or weapon tip; state "none" if a pop-out would risk changing the source.
- **fidelity note**: what will be preserved from the original image/token.

Keep every scheme faithful to the source. Do not propose options that require changing the character identity, face, body shape, pose, equipment type, costume design, color scheme, or overall silhouette.

For both frame-only modes, include:

- **scheme name** and **frame design**: materials, color palette, motifs, thickness, and readable ornament placement.
- **reference or text mapping**: which supplied character traits or explicit details inform the rim; decorative interpretation is not a new character design.
- **opening and transparency**: a large empty circular center plus transparent exterior, leaving room for later portrait compositing.
- **frame-only scope**: no portrait, face, body, character silhouette, scene, inner background, or character pop-out. Do not offer an “inner background” for these modes.

Treat stated details such as material, symbols, colors, and shape as constraints. Interpret character information into frame ornament, such as a crescent inlay for a moon priest or an engraved blade motif for a warrior, rather than drawing the character or a scene inside the opening.

End Stage 1 by asking the user to choose a scheme number or request adjustments. Do not include a full generation prompt.

## Stage 2: selected-scheme rendering

When the user chooses a scheme, requests a minor variant of a scheme, combines scheme elements, or explicitly approves proceeding after Stage 1, invoke image generation/editing directly.

The final response after generation should be the generated/edited image only. Do not explain the design plan, prompt, or workflow after the final image is produced.

If the user asks for revisions after the generated image, preserve the selected output mode and scheme constraints. A frame-only revision must remain an empty frame unless the user explicitly requests a complete token.

## Core behavior

Only complete-token mode requires a usable character image or existing token; request one if missing. Standalone frames can start from border specifications, and text-described frames can start entirely from character information. If a frame request has no design cues at all, ask briefly for a theme or offer neutral frame schemes; do not request a portrait as a prerequisite.

If multiple images are present and the target image is ambiguous, use the most recent character or token image unless the user clearly identifies another target.

In complete-token mode, use accompanying text to guide the rim, inner background, symbols, lighting, atmosphere, and allowed pop-out emphasis without overriding visible identity anchors. In frame-only modes, use images and text only for frame design cues; explicit border specifications control the new frame, without imposing the source portrait silhouette or copying its inner scene.

If the user says to skip selection, auto-pick, choose the best, or use your judgment in the first request with a new source image or frame brief, do not proceed to Stage 2. Provide numbered schemes and recommend a suitable option for the selected mode. Ask the user to confirm before rendering.

## Preservation priority

This section applies to complete-token compositing. For frame-only modes, preserve relevant reference motifs and explicit frame constraints, not the source character as image content.

Treat the uploaded image as the ground truth. Preserve the original visible token/character as strictly as possible.

Do:

- Preserve the original face, expression, pose, silhouette, body proportions, gesture, clothing, armor, weapons, accessories, hairstyle, colors, markings, and visible design language.
- Preserve the original token shape and character placement when the input is already a token, unless the user explicitly asks for recropping.
- Preserve existing readable linework, painterly style, rendering style, and texture treatment.
- Use only minimal restoration or enhancement: cleaner edges, slight sharpening, subtle lighting integration, transparent exterior cleanup, minor rim/background unification, controlled foreground layering, and small repairs caused by masking.
- Keep any iconic equipment or props in the same relative position whenever possible.
- Create the pop-out effect primarily by layer ordering: place an existing visible part of the character in front of the rim or allow it to slightly cross the circular rim, rather than redrawing or extending the part.

Do not:

- Redesign the character into another person or another costume.
- Change gender presentation, species/race cues, age impression, facial structure, pose, weapon type, armor design, clothing design, or color scheme.
- Enlarge, rotate, bend, extend, or invent limbs, hair, horns, wings, weapons, or props unless needed to repair a damaged edge.
- Create a dramatic pop-out composition that changes the original silhouette.
- Crop away important parts of the original character/token shape.
- Add a pop-out element if doing so requires inventing unseen body parts, reshaping the character, or changing the original pose.

## Hidden analysis before Stage 1 and Stage 2

Before offering schemes or invoking image editing, determine the requested output mode. For frame-only modes, identify the supplied materials, motifs, colors, theme, rim thickness, and opening size; skip character-compositing and background planning. For complete-token mode, determine:

1. The source image type: existing token, portrait, bust, half-body, full-body, or screenshot.
2. The source character's identity anchors: face, expression, species/race cues, hair, skin, pose, clothing, armor, weapons, accessories, color palette, markings, and silhouette.
3. The original token/character boundary that must be preserved.
4. The likely fantasy role: class/archetype, combat style, magic type, faction, alignment vibe, environment, and story tone.
5. Several safe token rim motifs matching the image: vines, roots, bone, steel, silver, gold, runes, leather, stone, ice, fire, shadow, celestial ornament, infernal ornament, gears, nautical rope, holy iconography, draconic scales, arcane sigils, or another motif matching the character.
6. Candidate circular backgrounds: atmospheric, complementary, inside the circle only, and visually separated from the foreground character.
7. The safest circular-core composition: centered readability, transparent exterior, no accidental cropping, no unwanted reshaping, and a modest pop-out only where an existing visible element can cross the rim naturally.

Use this analysis only to make the scheme options and final image operation better. Do not reveal detailed chain-of-thought or full prompt text.

## Image editing requirements for Stage 2

Produce a 1:1 square PNG-style result with genuine transparency, following the selected mode's contract.

### Standalone frame and text-described frame

- Render only one complete circular rim with its approved ornament, fully inside the canvas with a safe transparent margin.
- Keep a large, unobstructed, genuinely transparent center opening for later character insertion. Keep the exterior genuinely transparent too.
- Do not fill the opening with black, white, checkerboard, a scene, a portrait placeholder, a character, or a translucent colored disc. Transparency must be real Alpha, not an illustrated transparency pattern.
- Keep material, glow, motifs, and decoration localized to the rim. Do not span the opening with symbols, webs, weapons, fog, or other ornament; do not use an inner background or character pop-out.
- Preserve a circular inner opening and a circular outer rim boundary. Ornament follows the rim and remains legible at VTT scale without overwhelming the opening.
- In reference-based work, use the image for palette and motif guidance; do not retain its face, body, silhouette, or background in the frame asset. If the reference is already a standalone frame, preserve the features the user asks to retain.
- In text-based work, translate character details into frame design only. A request for a necromancer's frame may produce bone and rune ornament, but never a necromancer portrait in the center.
- The result is a reusable frame asset, not a mockup showing a finished token. Return the generated frame image only after rendering.

### Complete token

Build a circular-core token with controlled pop-out:

- The main rim must read as a complete circular token.
- The outer rim boundary must be circular, not oval, not shield-shaped, and not an irregular frame.
- The token exterior must be transparent except for approved foreground pop-out parts from the character.
- Any ornate rim must follow the circular boundary. The rim itself should remain a complete circle.
- Allow a small, deliberate pop-out effect: an existing visible part of the character may overlap the rim or extend slightly beyond it while staying fully inside the square canvas.
- Preferred pop-out parts are natural identity-safe elements already visible in the source: top hair mass, hood, head, shoulders, shoulder armor, cape edge, horn, ear, wing edge, or weapon tip.
- Keep the pop-out modest. As a default, it should feel like a shallow VTT token relief effect, not a full poster composition. Do not let the pop-out dominate the circle or make the token hard to read at small scale.
- Do not stretch, enlarge, rotate, bend, or invent a pop-out part. Use masking, layering, conservative cropping, and rim placement rather than character redesign.
- If the input is already a circular token, preserve its current placement and add only a subtle foreground-over-rim effect where the original silhouette already supports it.
- If a safe pop-out is impossible without changing the source, prioritize source fidelity and keep the character inside the circular token.

Preserve and composite:

- Cleanly isolate the original character/token while retaining the original silhouette.
- Add or refine a thick ornate circular rim matching the selected design scheme and the character's story, class, equipment, and mood.
- Add or refine an atmospheric background contained inside the circle.
- Use subtle cinematic/rim lighting only to separate foreground from background; do not repaint the character into a different style.
- For an existing circular token, prefer enhancing the current rim/background rather than replacing the whole composition.
- For a non-token source image, crop and scale conservatively for token readability while keeping the original pose and important equipment visible.

## Fidelity and conflict rules

The following source-image fidelity rules apply to complete-token mode. In frame-only modes, follow the approved border design and use character references only as design cues.

When user text conflicts with the source image, use the image as ground truth for identity, face, pose, silhouette, clothing, weapons, and visible equipment. Use text mainly for border theme, background mood, magic effects, faction symbols, lighting, and the desired strength of the pop-out effect.

If the source image has a plain or unsuitable background, replace or reinterpret it as an atmospheric circular background. If the source background is story-relevant, keep its mood and major color logic inside the circle.

If the image is low resolution, lightly clarify the character, but avoid inventing new facial features, costume details, or equipment.

If the user asks for a revision that would alter identity or shape, preserve the original form and only apply the requested change where it does not conflict with source fidelity.

## Quality checklist before finalizing Stage 1 options

Ensure all proposed schemes satisfy:

- Stage 1 is text-only and no image generation/editing was invoked.
- The output mode matches the request; frame-only requests stay frame-only even when a character image is attached.
- Circular-core token construction with a complete circular rim.
- Transparent exterior after generation.
- Frame-only schemes specify an empty transparent center, omit characters and backgrounds, and can proceed from text alone.
- Rim treatments are distinct enough for the user to choose meaningfully.
- For complete tokens: no character redesign, source shape is preserved, and any pop-out is modest, faithful, and executable; otherwise specify none.

## Quality checklist before finalizing Stage 2 image

Ensure all of the following are satisfied before producing the image:

- The visible token has a complete circular rim inside a 1:1 square canvas.
- The rim is circular, thick enough to read at VTT scale, and thematically consistent with the selected scheme.
- For frame-only modes: center and exterior are truly transparent; no character, portrait placeholder, scene, inner background, or decoration blocking the opening is present.
- For complete tokens: the exterior is transparent except for approved character pop-out; the original shape, face, pose, proportions, equipment, and colors are preserved; important parts are not cropped or reshaped.
- For complete tokens: pop-out uses only existing visible parts, remains modest and within the canvas; the background stays within the circle and remains distinct from the character without heavy repainting.
- Final response after Stage 2 contains only the generated/edited image.
