# Macro and module patterns

## Public API first

For Foundry v14, prefer documented public APIs for Hooks, Documents, settings, UUID resolution, Canvas/token access, and application behavior. If an API is marked internal/private, avoid it unless no stable alternative exists.

Useful core concepts include:

- `Hooks.on`, `Hooks.once`, `Hooks.off` for event lifecycle.
- `Actor`, `Item`, `ActiveEffect`, `ChatMessage`, `Scene`, and `TokenDocument` document APIs.
- `createEmbeddedDocuments`, `updateEmbeddedDocuments`, and `deleteEmbeddedDocuments` for owned documents.
- `fromUuid` / UUID-based resolution for verified document references.
- `game.settings.register` during initialization and `game.settings.get/set` after registration.
- Canvas token and template access only when scene state is actually needed.

Verify exact v14 signatures in the official API before authoring reusable module code.

## PF2e internals

Use Context7 `/foundryvtt/pf2e` and the matching source to inspect actor/item models, rule synthetics, check/damage machinery, chat-message flags, and system applications. Internal PF2e classes can change more quickly than Foundry's public core APIs.

If a solution imports or calls a PF2e internal class/path, state the tested PF2e version and provide a fallback or a clear failure mode.

## Safe macro shape

A target-aware macro should:

1. Resolve an acting Actor explicitly.
2. Validate target count before reading target state.
3. Resolve the needed state through documented actor/item data or verified source.
4. Create/update one stable temporary item/effect rather than duplicating it.
5. Let Rule Elements perform modifier stacking and roll integration when possible.
6. Clean up stale state.
7. Warn the user with `ui.notifications.warn` for recoverable misuse.

Do not assume a condition value path from memory. Verify the installed PF2e data shape or use a supported condition API.

## Idempotent temporary state

Give macro-created state a stable slug or flag namespace. Before creating a new document, search owned items/effects for the existing one and update or replace it. Repeated macro execution must not accumulate duplicates.

## When to write a module

Escalate from macro to module when the feature requires persistent Hooks, settings, UI, sockets, chat-card interception, ongoing token/scene monitoring, or several reusable services.

A v14 module should register configuration during the appropriate initialization phase and defer world-dependent work until the relevant later hook. Avoid running document-dependent code too early.

## Hook caution

Use a specific semantic hook when Foundry/PF2e exposes one. Broad hooks such as generic document updates can fire often and create recursion. Guard against self-triggered updates and check changed paths before doing work.

## Roll interception caution

Avoid replacing PF2e's roll resolution unless the requested mechanic cannot be represented declaratively. Direct roll interception can bypass degree-of-success adjustments, stacking, rerolls, roll notes, and Inspect Roll transparency.
