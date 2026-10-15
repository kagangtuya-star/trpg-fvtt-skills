# Rule Element map and patterns

## Current built-in families

The PF2e v14 development source registry currently includes these built-in keys. Verify against `src/module/rules/index.ts` for the user's installed system before relying on this list as exhaustive:

`ActiveEffectLike`, `ActorTraits`, `AdjustDegreeOfSuccess`, `AdjustModifier`, `AdjustStrike`, `Aura`, `BaseSpeed`, `BattleForm`, `ChoiceSet`, `CraftingAbility`, `CreatureSize`, `CriticalSpecialization`, `DamageAlteration`, `DamageDice`, `DexterityModifierCap`, `EphemeralEffect`, `FastHealing`, `FlatModifier`, `GrantItem`, `Immunity`, `ItemAlteration`, `LoseHitPoints`, `MartialProficiency`, `MultipleAttackPenalty`, `Note`, `Resistance`, `RollOption`, `RollTwice`, `Sense`, `SpecialResource`, `SpecialStatistic`, `Strike`, `SubstituteRoll`, `TempHP`, `TokenEffectIcon`, `TokenImage`, `TokenLight`, `TokenMark`, `TokenName`, `Weakness`.

The local Rule Element guide is the first authoring reference. The implementation file is the schema authority when a field is unclear.

## High-value patterns

### Degree of success

```json
{
  "key": "AdjustDegreeOfSuccess",
  "selector": "saving-throw",
  "adjustment": {
    "success": "to-critical-success",
    "failure": "to-critical-failure"
  }
}
```

Do not add historical fields such as `type: "save"` unless the matching installed version actually requires them.

### Toggle + predicate

```json
{
  "key": "RollOption",
  "domain": "all",
  "option": "example-toggle",
  "toggleable": true,
  "label": "Example Toggle"
}
```

```json
{
  "key": "FlatModifier",
  "selector": "strike-attack-roll",
  "type": "circumstance",
  "value": 1,
  "predicate": ["example-toggle"]
}
```

### Choice-driven data

Use `ChoiceSet` to store a user selection in item rule-selection flags, then reference the chosen value from a later Rule Element. Verify the exact flag path and field schema against current docs/source.

### Target predicates

Target-aware roll options can make a pure Rule Element possible, but exact strings are version- and roll-context-sensitive. Prefer Inspect Roll or an official pack example. Do not infer arbitrary `target:*` paths from actor data.

### Dynamic badge

When a runtime macro must capture a numeric value, prefer a short-lived item/effect badge if the Rule Element can consume `@item.badge.value`. This keeps the final modifier visible to PF2e's stacking engine.

## Choosing common keys

- `FlatModifier`: typed bonus/penalty to supported selectors.
- `AdjustModifier`: alter an existing modifier, often by slug.
- `AdjustDegreeOfSuccess`: remap outcomes using system degree-of-success machinery.
- `RollOption`: expose a boolean/toggleable predicate option.
- `DamageDice` / `DamageAlteration`: modify damage without replacing the damage roller.
- `RollTwice`: fortune/misfortune-style roll-twice behavior.
- `Note`: add outcome-sensitive roll notes.
- `Aura`: emanation-like automation that can grant/apply effects.
- `EphemeralEffect`: transient roll-context effects; verify current supported selectors and target semantics.
- `GrantItem`: grant a referenced item; always verify UUID.
- `ItemAlteration`: alter matching owned item properties; inspect current schema before complex use.
- `ChoiceSet`: store user choice for later injected-property use.
- `ActiveEffectLike`: modify actor data paths when a dedicated Rule Element is not more appropriate.
- `Strike` / `AdjustStrike`: create or alter strikes.
- `Resistance` / `Weakness` / `Immunity`: IWR changes.
- `SpecialStatistic`: create specialized checks/statistics when supported by the mechanic.

## Predicates and injected properties

Predicates evaluate roll options, not arbitrary object paths. If the condition is not present as an option, either expose it with a Rule Element or escalate to a macro/hybrid approach.

Injected properties such as `{actor|...}`, `{item|...}`, and rule-selection values are powerful but version-sensitive. Verify any nontrivial path in current docs/source.

## Similar-example rule

Before authoring a complex Rule Element, find a semantically similar official feat/item. Search official pack JSON by key and by the mechanic's natural-language term. Copy the pattern, not the UUID or unrelated predicates.
