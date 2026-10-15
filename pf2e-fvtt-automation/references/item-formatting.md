# PF2e item text formatting

## Goal

Turn rules prose into a readable Foundry item description while preserving the source mechanic and adding only justified automation markup.

## Structure

Keep the source's logical order. For actions and abilities, preserve fields such as action cost, traits, frequency, trigger, requirements, and effect when present. Do not invent missing rules metadata.

A practical body order is:

```text
Trigger / Requirements / Frequency when present
Effect prose
Degree-of-success entries when the source defines them
Special or heightened clauses
```

Use the user's language for prose and canonical English slugs inside PF2e automation syntax.

## Formatting rules

- Keep defined game terms consistent with the user's localization glossary.
- Do not silently “correct” a homebrew mechanic into published PF2e rules.
- Replace plain checks/damage/areas with inline automation only when semantics are unambiguous.
- Preserve outcome headings such as Critical Success, Success, Failure, and Critical Failure when the ability has distinct results.
- Keep durations and recharge text readable; use an inline roll only for an actual random duration/recharge.
- Prefer system-resolvable links over hard-coded compendium IDs when IDs have not been verified.

## Automation split

The item description explains the rule. Rule Elements implement persistent mechanical effects. Macros orchestrate live state. Do not hide an important mechanical limitation only in code; keep the player-facing text complete.

## Localization safety

Do not translate selectors, Rule Element keys, damage-type slugs, roll-option slugs, or action slugs. Translate labels and prose around them.

When converting older text, watch for remaster terminology changes and legacy Foundry markup. Preserve the user's intended ruleset/version rather than globally remastering every term.
