---
name: job-post-to-icp
description: Read a job posting and extract buying signals such as tools named, team size and stated pains, then qualify the company against an ideal customer profile. Use when the user pastes a job description and asks whether the company is a good fit, to pull signals from hiring posts, or to score a prospect from a job ad.
---

# Job post to ICP

A job post is a public statement of what a company is building and what hurts. This skill turns it into the same short qualification record every time.

## Inputs

| Field | Notes |
| --- | --- |
| Job post text or URL | The raw posting, not a summary |
| Target ICP, if the user has one | Roles, company size, industries, must-have tools |
| Known account context | Anything already known about the company |

If there is no ICP, use these defaults and say so: B2B software company, 20 to 500 employees, a named team that owns the pain in the post.

## Steps

1. **Extract verbatim signals.** Copy the exact phrases for tools, team names, seniority, locations, headcount hints and pains. Quote, do not paraphrase, in this step.
2. **Group the signals.** Put them in four buckets: tools and stack, team and size, pains and goals, buying clues (new role, backfill, expansion, "first hire", "build from scratch").
3. **Score the fit.** Rate each bucket 0 to 2 against the ICP and explain each score in one line. Total out of 8: 6 or more strong fit, 3 to 5 worth a look, 2 or less poor fit.
4. **Find the wedge.** Name the single pain in the post that the user's product addresses, and the role that owns it.
5. **Write the opener angle.** One sentence the user could use in outreach that quotes the post. No generic praise.
6. **List what the post cannot tell you.** Company size, budget, current contract and decision process are usually missing; mark them unknown instead of guessing.

## Output format

```text
Company: Acme GmbH (from posting)
Role: Senior Platform Engineer, Data Platform
Fit: 6/8, strong

Signals
- Tools: "Kubernetes", "dbt", "Snowflake" (verbatim)
- Team: "team of four", "first data hire"
- Pains: "pipelines break every week", "no on-call rotation"
- Buying clues: new role, build from scratch

Scores
- Tools and stack: 2, matches the ICP stack.
- Team and size: 1, size not stated.
- Pains and goals: 2, matches the pipeline reliability pain.
- Buying clues: 1, new role but no budget signal.

Wedge: pipeline reliability owned by the data platform lead.
Opener: "You mention pipelines break every week and there is no on-call rotation..."
Unknown: company size, budget, current vendor, decision process.
```

## Rules

- Every signal is a direct quote from the posting; put quotes around it.
- Never infer headcount, revenue or budget from a job title alone.
- Do not score a bucket without a quote that supports it; write `unknown` and zero with a reason.
- Keep the output under 300 words; this is a qualification note, not a report.
- If the posting is for an agency or a recruiter, say so and stop; it is not the hiring company.

Credits: zeebyx/operator-skills contributors
