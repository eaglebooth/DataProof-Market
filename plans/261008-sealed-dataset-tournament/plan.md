# DataProof Market v2 — Sealed Dataset Tournament

Status: planned
Baseline: `0797299`
Date: 2026-10-08

## Outcome

Upgrade a designated-provider escrow into a bounded competitive procurement
market. A buyer funds one prize. Up to five providers bond and commit evidence
digests before revealing immutable packets. GenLayer ranks valid candidates
against one rubric. Deterministic code assigns the prize and refunds/forfeits
bonds without allowing AI to move arbitrary value.

## Why this feature

- Makes DataProof a real marketplace instead of a bilateral escrow.
- Prevents providers copying another submission before committing.
- Uses GenLayer for comparative semantic dataset evaluation.
- Creates auditable competition, bounded storage, and strong economic invariants.
- Produces clear Studionet evidence with three wallets and multiple candidates.

## Phases

1. [Protocol and invariants](phase-01-protocol-and-invariants.md) — contract storage,
   commit/reveal lifecycle, bounded candidate set, pull-payment ledger.
2. [Comparative jury and tests](phase-02-jury-and-tests.md) — candidate ranking,
   closed output validation, adversarial/property tests.
3. [Frontend tournament workspace](phase-03-frontend-workspace.md) — buyer/provider
   role flows, deadlines, candidates, ranking, withdrawals.
4. [Deployment and evidence](phase-04-deployment-and-evidence.md) — new Studionet
   deployment, three-wallet lifecycle, Vercel, immutable compare and milestone docs.

## Core invariants

```text
total_received = active_prizes + active_bonds + withdrawable + withdrawn
```

```text
one address has at most one submission per tournament
```

```text
candidate_count <= 5; winner belongs to revealed eligible candidates
```

```text
AI selects ranking only; deterministic code controls every credit and withdrawal
```

## Deployment

Storage and ABI change materially. A fresh Studionet contract is required. The
current `0x4AD7...20c1` remains immutable v1 evidence and must be marked deprecated
only after v2 runtime verification passes.

## Open release gate

Implementation may proceed locally without a new address. Stop after deploy-ready
verification and ask the owner to deploy the new contract. Do not rotate frontend
production until schema and funded lifecycle are verified.
