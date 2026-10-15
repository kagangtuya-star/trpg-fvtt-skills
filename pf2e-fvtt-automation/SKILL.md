---
name: pf2e-fvtt-automation
description: >-
  Build, investigate, validate, and maintain Pathfinder 2e automation for Foundry VTT v14. Use for PF2e Rule Elements, predicates/selectors, effects and items, inline @Check/@Damage/@Template text, macros, hooks, module-level automation, target/scene-aware workflows, system-source investigation, and automation debugging. Also use when bootstrapping or maintaining a PF2e automation workspace across Windows, WSL, Linux, macOS, local or headless machines, and different AI agents such as Codex, Claude Code, Cursor, OpenCode, Gemini CLI, VS Code/Copilot, or generic MCP clients: detect the environment, install or reuse Context7 appropriately, mirror PF2e documentation locally, keep sources fresh, and select the least invasive automation layer that preserves PF2e stacking and roll behavior.
---

# PF2e FVTT Automation

Build automation from the least invasive layer upward, and ground every version-sensitive decision in current local docs, Context7, official Foundry v14 API docs, or the PF2e source.

## Operating workflow

1. Determine the installed Foundry and PF2e versions when they materially affect the result. Prefer runtime facts such as `game.version` and `game.system.version` over assumptions.
2. Detect the execution environment and agent capabilities before assuming a shell, config path, scheduler, or MCP installation method. For setup/maintenance work, read `references/environment-agents.md` and run `scripts/doctor.py` when shell access exists.
3. Ensure the documentation workspace exists and is fresh. If a persistent writable filesystem and shell are available, run `scripts/sync_sources.py --ensure-fresh --max-age-days 7 --refresh-configured`. Add `--with-pf2e-source` when source-level investigation is expected. On ephemeral or read-only agents, use connected Context7/GitHub/web sources instead of pretending a persistent mirror exists.
4. Search the local Rule Element mirror before inventing syntax. Use `scripts/find_pf2e_examples.py` for fast local examples.
5. Use Context7 for current APIs and implementation context. Prefer an already-connected Context7 tool, then an existing `ctx7` CLI, then client-specific MCP/CLI setup. Do not reinstall merely because the current agent surface differs.
6. If documentation and behavior disagree, inspect the matching PF2e source implementation. Treat the source matching the user's installed system version as authoritative for system internals.
7. Decompose the requested mechanic into clauses, choose an automation layer for each clause, then author the smallest complete solution.
8. Format player-facing PF2e item text and inline rolls after the mechanical design is stable.
9. Run `scripts/lint_pf2e_automation.py` on generated JSON/text when shell access is available, then give an explicit Foundry validation procedure.

## Automation ladder

Choose the lowest layer that can express the mechanic correctly:

- **Inline text only** for clickable checks, damage, templates, actions, recharge rolls, and links with no persistent mechanics.
- **Rule Elements** for data available during actor/roll preparation: modifiers, degree-of-success changes, predicates, roll options, damage dice/alterations, IWR, choices, grants, senses, auras, strike changes, and similar declarative behavior.
- **Hybrid Effect + Rule Elements** when a macro can capture live state into a badge, flag, temporary item, or roll option and Rule Elements can then apply the actual PF2e modifier or roll behavior.
- **Macro** when the mechanic requires live target selection, target badge values, scene geometry, token position, measured templates, interactive choice, document creation/deletion, or a one-shot orchestration step.
- **Module-level integration** when automation needs persistent hooks, reusable UI, chat-card behavior, settings, multiple macros, socket coordination, or ongoing event listeners.

Prefer declarative PF2e automation and hybrid designs over intercepting or replacing rolls. See `references/automation-ladder.md`.

## Source discipline

Use search order and authority separately. Search local docs first for speed; resolve conflicts using the most authoritative source.

- Rule Element authoring: local `foundry-pf2e-wiki-doc` mirror first, then Context7, then matching PF2e source.
- PF2e internals: `/foundryvtt/pf2e` Context7, then official GitHub source. Inspect `src/module/rules`, `src/module/system`, actor/item code, chat-message code, and official pack JSON as needed.
- Foundry core APIs: `/websites/foundryvtt_api_v14` Context7 and `https://foundryvtt.com/api/v14/`. Prefer public APIs.
- Architecture discovery: DeepWiki can locate concepts, but do not let it override current source or official API documentation.
- Community examples are hints, not schema authority.

Read `references/source-policy.md` before source-level or API-heavy work.

## Rule Element authoring

Read `references/rule-elements.md` for the current built-in family map and high-value patterns. For any unfamiliar key:

1. Search the local quickstart documentation.
2. Find at least one official pack example or inspect the Rule Element implementation.
3. Verify selectors and predicate roll options. Do not guess target or weapon roll options when Inspect Roll can reveal them.
4. Preserve PF2e stacking by using the correct modifier type and Rule Element instead of raw numeric mutation.
5. Do not invent compendium UUIDs.

When a mechanic says “success becomes critical success” or similar, use `AdjustDegreeOfSuccess` rather than manually interpreting the chat result.

## Macro and module authoring

Read `references/macro-module-patterns.md` before writing a macro or module. Use Foundry v14 public Documents, Hooks, settings, UUID resolution, and Canvas APIs where possible. Use PF2e internal APIs only when a public route is insufficient; pin or state the tested PF2e version and mark the dependency as version-sensitive.

Macros must fail cleanly, avoid duplicate temporary items/effects, and keep PF2e mechanical modifiers in Rule Elements whenever practical. Persistent listeners or reusable UI belong in a module, not an ever-growing macro.

## PF2e item text and inline rolls

Read both `references/item-formatting.md` and `references/inline-authoring.md` when converting prose into Foundry-ready text.

Preserve rules meaning. Add automation markup without rewriting a mechanic into a different rule. Prefer explicit PF2e enrichment syntax such as `@Check`, `@Damage`, `@Template`, `@UUID`, and `[[/act ...]]` only when the semantic target is known. Do not convert every number into a roll.

## Portable environment and knowledge-base setup

Treat environment maintenance as an adapter layer, not as Codex/Linux-specific behavior. Read `references/environment-agents.md` for the portability matrix.

For an environment/bootstrap request:

1. Run `scripts/doctor.py` when shell access exists. Detect Windows vs WSL vs Linux vs macOS, persistent vs ephemeral filesystem, available schedulers, installed agent CLIs, and any existing Context7 configuration.
2. Reuse capabilities in this order: native/connected Context7 tools -> existing `ctx7` CLI -> existing MCP configuration -> new Context7 setup. Do not reinstall Context7 simply because the user switched from one Agent to another.
3. If Context7 setup is needed, read `references/context7-bootstrap.md` and preview `scripts/setup_context7.py --agent auto`. Use `--mode mcp` or `--mode cli` only when the agent supports that mode and the user wants it; add `--apply` only when installation is authorized. Unknown MCP-capable agents use the generic hosted endpoint rather than guessed config paths.
4. Run `scripts/sync_sources.py --force` for the documentation mirror. Add `--with-pf2e-source` for a source-aware workstation. Later refreshes should use `--refresh-configured` so the recorded source ref, packs setting, and mirror URLs are preserved.
5. For unattended refresh, preview `scripts/install_update_timer.py --mode auto`. It chooses Windows Task Scheduler, macOS launchd, Linux systemd-user, or cron when available. WSL and sleeping/ephemeral systems must still rely on the per-use freshness gate.
6. On cloud/headless/read-only agents, do not claim local persistence. Prefer project-local caches when writable; otherwise query Context7/GitHub/official docs on demand and keep the same source-authority policy.

Never place API keys, OAuth tokens, or secret-bearing headers in the skill bundle, generated code, committed config, or knowledge mirror. Never install an OS package manager dependency unless the user explicitly authorizes it.

## Output contract

Match the user's requested scope. For a full automation request, normally provide:

- a short conclusion describing what is fully automated and which layer is used;
- assumptions that materially affect correctness;
- complete Rule Element JSON, item/effect data, macro JavaScript, or module files as required;
- Foundry-ready player-facing text when relevant;
- exact placement/trigger instructions;
- a compact validation procedure and any version-sensitive limitations.

For a narrow syntax question, answer narrowly instead of forcing the full template.

## Validation rules

Before finalizing:

- Confirm selectors match the intended statistic or roll domain.
- Confirm predicates are backed by documented or inspected roll options.
- Confirm modifier types preserve PF2e stacking.
- Confirm degree-of-success changes use system machinery rather than post-processing text.
- Confirm temporary effects/items are idempotent and clean up correctly.
- Confirm macros handle missing actor, missing/extra targets, and unavailable scene state.
- Confirm document writes use supported Foundry APIs.
- Confirm inline syntax remains valid after localization or item-description formatting.
- State any private/internal PF2e API dependency.

Use the full checklist in `references/testing.md` for complex work.
