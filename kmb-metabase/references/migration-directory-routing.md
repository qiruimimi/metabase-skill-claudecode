# Migration Directory Routing

Read this when a Space page is being migrated without an explicit KMB destination.

## Default rule

- For Space-to-KMB migration with no user-provided KMB directory, default to KMB root collection `545`.
- Replicate the Space directory hierarchy under `545`.
- Create all migrated Models, cards, and dashboards in the resolved leaf collection, not directly under `545`.

## Path source priority

Use the Space page path in this order:

1. live MCP or page query result
2. offline `path` from `$kmb-space-query`

Record the fallback source when the live path is unavailable.

## Path normalization

- Start from the full Space page `path`
- Remove the fixed prefix `spaceId为1140的root页面`
- Split the remaining path by `/`
- Preserve all non-empty path segments in order
- Treat the final path segment, including the page name, as the leaf collection name

Example:

- Space path: `spaceId为1140的root页面/Coohom PLG/Acquisition/Traffic/访客访问记录`
- KMB root: `545`
- Replicated collections:
  - `Coohom PLG`
  - `Acquisition`
  - `Traffic`
  - `访客访问记录`

## Override rule

- If the user explicitly provides `target_collection_id`, a target collection path, or an equivalent KMB parent directory, use that destination directly.
- Do not apply the default `545-root` routing when an explicit KMB destination exists.

## Expected migration outputs

When the default routing rule is used, record at least:

- `root_collection_id`
- `space_path`
- `resolved_collection_path_segments`
- `intermediate_collection_ids`
- `final_target_collection_id`

## Guardrails

- Do not skip intermediate collection levels.
- Reuse an existing same-name collection under the intended parent only when it is the unique active candidate or its ownership has been confirmed by existing asset metadata and live contents.
- If multiple active same-name collections exist under the intended parent, do not resolve by first-match, newest, or oldest alone. Inspect ownership and either archive the mismatched duplicate or ignore it explicitly.
- Do not create a parallel “migration-only” collection unless the user explicitly asks for one.
