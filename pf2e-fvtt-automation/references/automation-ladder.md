# Automation ladder

## Goal

Implement each mechanic at the lowest layer that remains correct, transparent, and maintainable.

## 0. Inline text

Use only enrichment markup when the user needs clickable interaction but no persistent rule state. Typical cases include saves, skill checks, damage, areas, recharge rolls, and action links.

Do not add Rule Elements merely because an ability contains a roll.

## 1. Pure Rule Elements

Use when all required information is available during actor preparation or roll preparation. Common tasks include bonuses/penalties, toggles, degree-of-success changes, damage dice and damage alteration, roll-twice, notes, senses, IWR, choices, grants, strike changes, auras, token presentation, and derived data.

Advantages: PF2e stacking remains correct, the modifier appears in roll dialogs/Inspect Roll, and the automation is data-driven.

## 2. Hybrid temporary state + Rule Elements

Use when a dynamic value must be read at runtime but PF2e should still apply the final mechanic. A macro may capture target/scene state into an Effect badge, actor flag, item flag, or RollOption; a Rule Element then consumes that value.

This is usually better than a macro that directly edits a roll total.

Example shape:

```json
{
  "key": "FlatModifier",
  "selector": "strike-attack-roll",
  "type": "circumstance",
  "value": "@item.badge.value",
  "removeAfterRoll": "if-enabled",
  "predicate": ["example-enabled"]
}
```

## 3. Macro orchestration

Use when live interaction is unavoidable: selected targets, exact condition badge values, template placement, distances, token positions, interactive target choice, temporary document creation, or multi-step document updates.

A macro should orchestrate rather than reimplement PF2e's roller. Keep modifier math and stacking in Rule Elements whenever possible.

## 4. Module-level automation

Use a module when behavior must persist across sessions or react continuously to Foundry events. Good triggers include:

- registering Hooks during `init`, `setup`, or `ready`;
- custom settings or configuration UI;
- augmenting chat cards or actor/item sheets;
- monitoring damage, targeting, token movement, or item use repeatedly;
- coordinating multiple users or sockets;
- packaging several macros/helpers into a maintained feature.

A module should expose a narrow surface and avoid monkey-patching unless no supported hook/API can solve the problem.

## Escalation questions

Before moving upward, ask:

1. Is the needed fact already exposed as a PF2e roll option or selector?
2. Can `ChoiceSet`, `RollOption`, `GrantItem`, `ItemAlteration`, an item badge, or an Effect represent the state?
3. Can the macro only prepare state while PF2e handles the roll?
4. Does the code need to stay active after the initiating click? If yes, it is probably module territory.

## Anti-patterns

Avoid post-processing chat text to simulate degrees of success, direct mutation of final roll totals when a modifier Rule Element exists, duplicate temporary Effects on repeated macro clicks, permanent feat flags for target-specific one-shot state, and undocumented private APIs without a version pin.
