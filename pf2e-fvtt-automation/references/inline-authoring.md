# PF2e inline authoring

## Principle

Add clickable automation without changing rules meaning. Prefer explicit syntax when the check type, DC, damage expression, area, or action is known.

## Checks

Preferred concise forms:

```text
@Check[fortitude|dc:32]
@Check[reflex|dc:32|basic]
@Check[will|dc:29|basic|options:area-effect]
@Check[athletics|dc:32]
@Check[flat|dc:5]
```

PF2e also accepts explicit parameter forms in many system-authored descriptions. When matching an official example, preserve its current syntax rather than mechanically rewriting it.

For a damaging non-basic save, expose relevant roll options when the downstream automation needs them. A basic save already carries the system's basic-save semantics.

## Damage

```text
@Damage[10d6[sonic]]
@Damage[(2d6+4)[slashing]]
@Damage[5d6[cold],3d6[void]|options:area-damage]
@Damage[1d6[persistent,fire]]
```

Do not use generic inline rolls for damage when `@Damage` provides PF2e-aware behavior.

## Templates

```text
@Template[type:emanation|distance:40]
@Template[type:burst|distance:20]
@Template[type:cone|distance:30]
@Template[type:line|distance:60|width:10]
```

Only create a template link when the rules specify a measured area.

## Actions

PF2e pack data uses action links such as:

```text
[[/act demoralize]]{Demoralize}
[[/act demoralize statistic=deception]]{Demoralize}
```

Verify the action slug when localizing or linking a less common action.

## UUID links

Use `@UUID[...]` only with a verified UUID. Do not derive a compendium document ID from an English slug. For conditions or standard content, resolve the live compendium entry or let the consuming importer/system resolve it when that workflow supports it.

## Legacy syntax warning

Treat `@Compendium[...]` as legacy when targeting current Foundry/PF2e. Do not copy it from old data-entry scripts without checking the current system.

## Enrichment safety

- Preserve an existing valid `@Check`, `@Damage`, `@Template`, `@UUID`, or `[[/act ...]]` instead of wrapping it again.
- Avoid custom labels that themselves contain a second parseable damage/check expression when a downstream formatter performs auto-linking.
- Do not convert prose numbers such as durations, distances in requirements, or condition values into dice expressions unless they are rolls.
- Keep canonical PF2e slugs and damage types in English inside automation syntax even when player-facing text is localized.
