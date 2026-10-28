---
name: invoice-chaser
description: Write a three-step, politely escalating payment reminder sequence from an invoice number, amount, due date and relationship context. Use when the user asks for payment reminders, dunning emails, overdue invoice follow-ups or a collections sequence that stays professional.
---

# Invoice chaser

A reminder sequence fails when it is either too soft to be read or too harsh for the relationship. This skill keeps the same facts and the same escalation ladder every time.

## Inputs

Ask only for what is missing:

| Field | Example |
| --- | --- |
| Invoice number | INV-2041 |
| Amount and currency | 4,800 EUR |
| Due date | 2026-10-15 |
| Client and contact name | Acme GmbH, Ms Weber |
| Relationship context | 3 years, always paid late by 5 to 10 days |
| Payment route | SEPA transfer to the account on the invoice |
| Any agreed terms | Net 30, late fee only if stated in the contract |

## Steps

1. **Check the facts once.** Confirm the invoice number, amount and due date match what the user gave. If a date or amount is missing, ask before writing; never fill a placeholder.
2. **Pick the escalation stage.** Step 1 goes out on the due date. Step 2 goes out 7 days after the due date. Step 3 goes out 14 days after, and only if the user confirms nothing arrived.
3. **Keep the same thread.** Each email replies to the previous one, keeps the subject line and repeats the invoice number, amount and due date so nobody has to scroll.
4. **Escalate the ask, not the tone.** Step 1 assumes an oversight and asks for a payment date. Step 2 states the account is now overdue and asks for a date within five working days. Step 3 says the account will be paused or passed to the user's stated next step, and asks for a call.
5. **Offer one easy action.** Every email ends with a single concrete next step: a payment date, a remittance note, or a 15-minute call.
6. **Respect the relationship note.** Long, reliable clients get one extra sentence of context; a first late payment never gets step 3 language unless the user asks for it.

## Output format

```text
Sequence for INV-2041, 4,800 EUR, due 2026-10-15

Step 1 - send 2026-10-15
Subject: Invoice INV-2041 - 4,800 EUR due today
Body: ...

Step 2 - send 2026-10-22
Subject: Re: Invoice INV-2041 - 7 days overdue
Body: ...

Step 3 - send 2026-10-29 (only if still unpaid)
Subject: Re: Invoice INV-2041 - action needed
Body: ...
```

## Rules

- Never invent a late fee, interest charge, legal threat or collection agency. Use only terms the user says are in the contract.
- Keep the amount, currency, invoice number and dates exactly as supplied.
- Do not shame the reader, use all caps, or add more than one exclamation mark in the whole sequence.
- If the user has no escalation policy, say so and offer two neutral options instead of writing step 3 as a threat.
- Every email must name the invoice number and the amount in the subject or the first two lines.

Credits: zeebyx/operator-skills contributors
