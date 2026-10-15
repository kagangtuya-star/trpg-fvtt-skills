---
name: pf2-wiki-maintenance
description: Maintain the PF2 HuijiWiki production site at pf2.huijiwiki.com using live MediaWiki source and revision state. Use for Wikitext pages, templates, Scribunto Lua modules, Data pages, dependency analysis, candidate validation, and concurrency-safe edits. Do not use for generic PF2 rules questions or unrelated MediaWiki sites.
---

# PF2 Wiki Maintenance

Maintain the production site `https://pf2.huijiwiki.com/`. Treat it as a live system, not as an ordinary code repository.

When asked which environment is active, answer: “当前是 PF2 Wiki 专用 Codex 环境。” Replace “Codex” with the current agent product name when this skill is running elsewhere.

## Establish the operating context

Before acting, determine whether the request is read-only analysis, a candidate draft, or an authorized production edit.

- Use the live MediaWiki API or its connected tool as the source of truth for page source, revision metadata, content models, transclusions, links, and current site state.
- Do not infer live content from memory or from local files. Local files are only drafts, inputs, diffs, and test artifacts.
- If no compatible MediaWiki connection is available, perform only local analysis or draft generation. State that live verification or writing was not possible.
- Use user-provided CSV/XLSX or text as the factual source for fields it explicitly supplies. Do not silently replace those values with web research.
- For third-party libraries, software, and technical behavior, inspect bundled versions and local types first, then prefer current primary documentation or a current documentation service such as Context7. Do not use external research when live Wiki state or supplied files already establish the answer.
- For OpenAI, Codex, MCP, Agent Skills, or agent configuration questions, prefer the product's current official developer documentation.
- For local files, use the destination runtime's efficient structured file tools. When FastCtx is available, prefer `inspect_local_file`, `grep`, `glob`, and `replace`; batch reads where practical and honor pagination markers. This preference never makes local files authoritative for live Wiki state.

Read [references/mediawiki-tools.md](references/mediawiki-tools.md) when selecting or adapting a Wiki connector, configuring another agent runtime, or mapping tool names.

## Production boundaries

- Remote writes must directly serve the current request. Prior permission does not authorize unrelated changes.
- Never delete, undelete, move, upload, or replace files unless the user explicitly requests that operation and the current connector exposes the corresponding capability.
- Never modify user CSS/JS, site-wide CSS/JS, the `MediaWiki:` namespace, permissions, OAuth/bot configuration, or site administration settings unless the user explicitly names that task.
- If the expected operation affects more than 10 pages, report the estimated scope and migration plan before bulk writing. Do not begin the bulk write in the same step without the user's go-ahead.
- Prefer the smallest necessary change. Preserve established parameter names, defaults, public Lua functions, argument conventions, and return shapes unless the user requests a breaking migration.

## Inspect and prepare

1. Read every target page's latest source, content model, and revision identifier before preparing a modification.
2. For `Template:` or `Module:` changes, inspect transclusions, backlinks, outgoing links, and relevant dependencies. Identify representative live callers and estimate the affected page count.
3. For a new page, verify that the exact title does not already exist. For an existing page, use the update workflow rather than a create operation.
4. Produce a minimal candidate. Do not reformat or rename unrelated content.
5. Parse candidate Wikitext or Lua callers on the server without saving. Compare modified page candidates with their latest online revisions when a compare capability is available.
6. Review both semantic behavior and the textual diff. Syntax success alone is not sufficient evidence for a template or Lua change.

## Write safely

Immediately before saving an existing page, confirm its revision still matches the revision used to prepare the candidate. Use an update primitive that requires the expected revision ID or an equivalent MediaWiki concurrency guard.

- If the online revision changed during analysis, stop the overwrite path, fetch the new revision, and recompute the candidate and diff.
- Use a concise edit summary that names the purpose of the change.
- Use a create-only primitive for new pages so an unexpectedly existing page cannot be overwritten.
- Do not treat a successful API response as final verification.

After saving:

1. Fetch the page again and confirm the stored source, content model, and new revision match the intended result.
2. Reparse the saved page or compare it with the intended candidate.
3. For a `Template:` or `Module:` change, validate at least one real page or template that invokes it. Check rendered behavior, not only Lua syntax.
4. Report exactly what changed and any validation that could not be performed.

## Specialized workflows

- For creating or updating item display pages and `Data:Items-<Original>.json`, read [references/item-entry.md](references/item-entry.md) before preparing candidates.
- For connector capability mapping, secret handling, and migration to WorkBuddy or another agent runtime, read [references/mediawiki-tools.md](references/mediawiki-tools.md).
