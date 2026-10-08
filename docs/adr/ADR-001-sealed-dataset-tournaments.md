# ADR-001 — Sealed multi-provider dataset tournaments

Date: 2026-10-08
Status: Accepted for v2

## Context

DataProof v1 assigned each bounty to one provider. It proved funded semantic
review, but buyers could not compare competing datasets and providers could see
another packet before submitting their own.

## Decision

v2 uses a bounded commit/reveal tournament. A buyer escrows one prize. Two to
five providers post equal bonds and commit manifest, sample and license digests.
URLs are revealed only after commitments close. Exact digest verification uses
`strict_eq`; comparative dataset ranking uses `prompt_comparative`.

The jury selects only an eligible submission ID. It never selects amounts.
Deterministic settlement credits the prize to the winner, refunds every eligible
bond and assigns invalid/no-reveal bonds to the buyer. Transfers use a CEI-safe
pull-payment ledger.

## Invariants

```text
total_received = active_prizes + active_bonds + total_credited + total_withdrawn
```

- At most five submissions per tournament.
- At most one submission per provider.
- Only a revealed packet whose three digests verify can win.
- A terminal tournament cannot settle twice.
- A credit cannot be withdrawn twice.

## Consequences

The product becomes a competitive procurement market rather than a bilateral
escrow. Storage and ABI are incompatible with v1, so a fresh Studionet deployment
is required. The v1 address remains historical evidence.
