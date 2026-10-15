# Source policy

## Purpose

Use this file to decide where to retrieve PF2e/FVTT automation facts and which source wins when sources disagree.

## Known Context7 libraries

Use these exact IDs when the tool accepts direct library IDs:

- `/kagangtuya-star/foundry-pf2e-wiki-doc` — mirrored PF2e Rule Element and data-entry guidance.
- `/foundryvtt/pf2e` — PF2e system source and wiki material.
- `/websites/deepwiki_foundryvtt_pf2e` — architecture/discovery aid.
- `/websites/foundryvtt_api_v14` — Foundry v14 API documentation.

If a Context7 query returns ambiguous or stale information, inspect official source directly.

## Local mirror layout

The setup scripts default to:

```text
~/.pf2e-automation/
  manifest.json
  sources/
    foundry-pf2e-wiki-doc/
    pf2e/                       # optional sparse source mirror
```

Override the root with `PF2E_AUTOMATION_HOME` or `--root`. On ephemeral agents with a persistent repository, a project-local root is preferred. On read-only or non-persistent agents, skip the mirror and query current remote sources on demand.

The documentation mirror intentionally excludes uploaded images and keeps Markdown sources. The optional PF2e source mirror is sparse by default and focuses on system automation code. `manifest.json` records source URLs, refs, pack inclusion, commit SHAs, and sync timestamps so another agent or OS can continue the same knowledge profile.

## Search order

For Rule Elements, search in this order:

1. Local `foundry-pf2e-wiki-doc` Markdown.
2. Local sparse PF2e source if available.
3. Context7 `/foundryvtt/pf2e` or `/kagangtuya-star/foundry-pf2e-wiki-doc`.
4. Official GitHub `foundryvtt/pf2e` source and pack JSON.
5. Community material only for examples or edge cases.

For Foundry core API usage:

1. Context7 `/websites/foundryvtt_api_v14`.
2. Foundry official v14 API site.
3. Foundry core source when documentation does not expose enough detail.

## Authority order

When facts conflict, use the source that matches the user's installed version. A practical authority order is:

1. The user's installed PF2e/Foundry source and runtime behavior.
2. Official PF2e source for the matching release/tag/branch.
3. Foundry official public API docs for the matching core version.
4. PF2e wiki / local guide.
5. DeepWiki and other derived documentation.
6. Community examples.

Do not treat `v14-dev` as universally identical to a released PF2e build.

## Important PF2e source locations

Current source commonly places automation internals under:

```text
src/module/rules/index.ts
src/module/rules/rule-element/
src/module/rules/synthetics.ts
src/module/system/
src/module/actor/
src/module/item/
src/module/chat-message/
packs/pf2e/
```

`src/module/rules/index.ts` is especially useful for the current built-in Rule Element registry. Individual Rule Element schema files are the final check for accepted fields.

Official pack JSON is the best source of realistic usage examples. Search by Rule Element key, inline syntax, action slug, or feature name.

## Runtime verification

When selectors, roll options, or data paths are uncertain:

- Make the relevant roll and use PF2e **Inspect Roll** to capture exact domains and roll options.
- Inspect `game.system.version`, the relevant Actor/Item `_source`, or a document returned by `fromUuid` in the browser console.
- Prefer a runtime-observed option over a remembered string.

Never fabricate compendium document IDs. Resolve them from a verified source or search the live compendium.
