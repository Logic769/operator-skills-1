---
name: zapier-to-n8n-migration
description: Read a list of Zapier Zaps and produce an n8n migration plan with node mapping, credentials, risks and migration order. Use when the user asks to move from Zapier to n8n, plan a workflow migration, or estimate the work of rebuilding Zaps.
---

# Zapier to n8n migration

Most migrations fail on credentials and on the few Zaps that cannot be rebuilt one to one. This skill produces the same four-part plan every time so the work can be scheduled.

## Inputs

| Field | Notes |
| --- | --- |
| Zap list or export | Name, trigger, actions, filter steps, apps used |
| Current Zapier plan and task volume | Explains what is worth migrating first |
| n8n hosting choice | Cloud or self-hosted, because it changes credential options |
| Known hard constraints | Data residency, approval rules, apps with no n8n node |

## Steps

1. **List every Zap as trigger plus steps.** Number the steps. Mark filters, formatter steps and paths, because they are the parts people forget.
2. **Map each app to an n8n node.** Write the node name. If there is no native node, mark it `HTTP Request` and note the API auth type. Never claim a node exists without naming it.
3. **Collect credentials.** One line per connection: app, auth type (OAuth2, API key, basic), who owns the account, and whether n8n supports it natively.
4. **Find the risky Zaps.** Flag any Zap with a filter or path, a polling trigger faster than five minutes, a formatter with a custom formula, or an app with no native node. These are the ones to rebuild first and test hardest.
5. **Order the migration.** Wave 1: single-step Zaps with native nodes and OAuth2. Wave 2: multi-step Zaps with native nodes. Wave 3: Zaps with HTTP Request, code steps or filters. Wave 4: the rest, or keep them on Zapier.
6. **Estimate effort.** Give each Zap a size: S (native, under five steps), M (native, five or more, or one filter), L (custom API, code or no native node).

## Output format

```text
Migration plan: 34 Zaps, 3 waves

1. Node mapping
| Zap | Trigger | Steps | n8n nodes | Size |
| --- | --- | --- | --- | --- |
| New lead to Slack | Typeform | 3 | Typeform Trigger, Slack | S |

2. Credentials
| App | Auth | Owner | n8n support |
| --- | --- | --- | --- |

3. Risks
1. ... (Zap, why, mitigation)

4. Order
Wave 1: ...
Wave 2: ...
Wave 3: ...
Keep on Zapier: ...
```

## Rules

- Name the exact n8n node or say `HTTP Request`; never leave a step unmapped.
- Do not promise that a Zap can be rebuilt if its app has no native node and no API.
- Keep secrets out: name the credential and its owner, never a key or token.
- Preserve the user's Zap names so they can match rows back to Zapier.
- If the export lacks steps, say the plan is provisional and ask for the step details of the first wave.

Credits: zeebyx/operator-skills contributors
