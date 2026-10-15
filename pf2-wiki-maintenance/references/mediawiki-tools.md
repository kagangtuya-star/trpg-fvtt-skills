# MediaWiki connector and runtime portability

Read this reference when adapting the skill to a new agent runtime, checking whether a connector is sufficient, or mapping platform-specific tool names.

## Required capabilities

The agent should have a MediaWiki connector scoped to `https://pf2.huijiwiki.com/` with these logical operations:

| Capability | Purpose | Current HuijiWiki MCP tool |
| --- | --- | --- |
| Site information | Confirm site identity and namespaces | `huiji_get_site_info` |
| Current identity | Confirm authenticated user and rights | `huiji_whoami` |
| Read one or many pages | Get source, content model, existence, and revision metadata | `huiji_get_page`, `huiji_get_pages` |
| Search | Locate pages without guessing titles | `huiji_search_pages` |
| Backlinks and outgoing links | Analyze dependencies and navigation | `huiji_get_backlinks`, `huiji_get_links` |
| Transclusions | Find template/module callers and estimate impact | `huiji_get_transclusions` |
| Server-side parse | Validate candidate Wikitext without saving | `huiji_parse_wikitext` |
| Compare | Diff candidate text against the latest online revision | `huiji_compare` |
| Create only | Create a page while failing if it already exists | `huiji_create_page` |
| Revision-guarded update | Update only if the expected revision still matches | `huiji_update_page` with `expectedRevId` |
| Cache purge | Refresh pages after a relevant edit when needed | `huiji_purge` |

Tool names are not part of the portable contract. On another platform, map each operation to an equivalent API, MCP tool, plugin, or function. A safe write adapter must preserve create-only behavior and optimistic concurrency for updates; a generic unrestricted “save page” operation is not an equivalent substitute.

If dependency enumeration, server parsing, or compare is unavailable, explicitly identify the missing verification. Do not claim that a template/module production edit was fully validated. If revision-guarded updates are unavailable, do not overwrite existing pages.

## Connection profile

The current environment uses this non-secret site profile:

```json
{
  "allowWikiManagement": false,
  "defaultWiki": "pf2.huijiwiki.com",
  "wikis": {
    "pf2.huijiwiki.com": {
      "sitename": "PF2 灰机 Wiki",
      "server": "https://pf2.huijiwiki.com",
      "articlepath": "/wiki",
      "scriptpath": "/w",
      "private": false,
      "readOnly": false,
      "username": "${PF2_WIKI_BOT_USERNAME}",
      "password": "${PF2_WIKI_BOT_PASSWORD}",
      "attributeEdits": true
    }
  }
}
```

Keep credentials outside the skill directory and inject them through the target runtime's secret store or environment. Never commit credential values. The current connector may also use `HUIJI_AUTHKEY`, `HUIJI_BOT_USERNAME`, `HUIJI_BOT_PASSWORD`, `HUIJI_PREFIX=pf2`, and `HUIJI_USER_AGENT`; use only variables required by the selected connector.

## Moving the skill to another agent

The portable contract is `SKILL.md` plus `references/`. Copy the entire `pf2-wiki-maintenance` directory so relative links remain valid.

- A runtime that supports Agent Skills can register the directory directly.
- A runtime that supports only project instructions can load `SKILL.md` as its scoped instruction file and make `references/` available for on-demand reading.
- `agents/openai.yaml` is optional Codex UI metadata. Non-Codex runtimes may ignore it.
- Do not copy local authentication files, shell launchers, absolute paths, caches, or model/provider settings. Configure the MediaWiki connector natively in the destination runtime.

Before the first real edit in a new runtime:

1. Fetch site information and confirm the server is `pf2.huijiwiki.com`.
2. Check the current identity and expected edit rights.
3. Read one known page and confirm source plus revision metadata are returned.
4. Confirm candidate parsing and comparison work without saving.
5. Confirm the update operation accepts an expected revision guard.

Do not use a production write merely as a connection test.
