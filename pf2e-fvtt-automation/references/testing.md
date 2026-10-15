# Validation checklist

## Rule Elements

- Add the final item/effect to a clean test actor.
- Confirm the Rule Element is accepted without console/schema warnings.
- Make the exact affected roll and inspect its domains/options.
- Confirm the selector hits the intended statistic and no unrelated rolls.
- Test every predicate branch, including the false branch.
- Confirm bonus/penalty type and stacking behavior.
- For degree-of-success changes, test natural 1/20 interactions and each relevant base outcome.
- For `removeAfterRoll` or ephemeral behavior, confirm cleanup timing.

## Target-aware behavior

- Test no target, one valid target, one invalid target, and multiple targets.
- Test the target both with and without required conditions/traits.
- Verify target roll options with Inspect Roll rather than assuming strings.

## Macros

- Test missing actor and uncontrolled-token cases.
- Test repeated execution to confirm idempotency.
- Verify temporary items/effects are updated or cleaned up.
- Refresh the browser/world and confirm no stale global state is required.
- Check the browser console for rejected Promises or deprecated API warnings.

## Modules

- Test a fresh world load and module enable/disable cycle.
- Verify `init`, `setup`, and `ready` responsibilities are separated correctly.
- Check permission behavior for player and GM users.
- Check multi-client duplication when hooks can execute on every connected client.
- Check scene transitions and token deletion when the feature tracks Canvas state.
- Confirm settings migrations/defaults if persistent settings are added.

## Inline text

- Open the item description and verify every enrichment renders.
- Click checks, damage, action links, and templates.
- Confirm localized labels do not break canonical slugs.
- Confirm no nested/double enrichment occurred.

## Version reporting

Record the tested Foundry core version, PF2e system version, and any module dependency version for complex automation. Mark untested versions as unverified rather than implying compatibility.

## Environment and knowledge-base maintenance

- Run `scripts/doctor.py --json` on the target environment and confirm OS/WSL, agent, Context7, scheduler, and mirror detection are plausible.
- Preview `scripts/setup_context7.py --agent auto` before applying. For an unknown agent, verify it falls back to generic MCP guidance instead of writing guessed config.
- Verify Node.js absence does not block local Git mirror usage.
- Test `scripts/sync_sources.py --ensure-fresh --refresh-configured` twice: the second run should skip fresh sources instead of fetching again.
- If optional PF2e source/packs were configured, verify `--refresh-configured` preserves the recorded ref and pack setting.
- Preview `scripts/install_update_timer.py --mode auto`; confirm it selects Task Scheduler on Windows, launchd on macOS, and systemd-user/cron on Linux when available.
- On WSL/container/cloud environments, confirm the workflow still functions without a background scheduler and does not claim persistence when none exists.
