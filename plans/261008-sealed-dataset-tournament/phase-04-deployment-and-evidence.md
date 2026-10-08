# Phase 4 — Deployment and evidence

## Overview

Priority: release gate
Status: blocked until owner deploys contract

Storage, ABI and economics change, so deploy a new Studionet contract. Do not
reuse the v1 address.

## Pre-deploy gate

- Python compile/direct runner passes.
- Full test suite passes.
- Frontend lint/build/tests pass.
- Source and schema methods reviewed.
- Git working tree clean except intended release changes.
- Deploy commit SHA recorded before deployment.

## Required live matrix

Use three wallets: buyer, provider A, provider B.

1. Buyer opens funded tournament.
2. Providers A/B commit distinct digests and exact bonds.
3. Both reveal distinct immutable packets.
4. Close reveal after authoritative deadline.
5. Run comparative jury.
6. Settle credits.
7. Winner and providers withdraw.
8. Read final state and prove conservation.

Additional transactions:

- Duplicate commit rejection.
- Wrong bond rejection.
- Reveal outside window rejection.
- Unrevealed provider cannot win and loses bond.
- Double settlement and double withdrawal rejection.
- `UNAVAILABLE` recovery on a separate tournament.

## Evidence artifacts

- Create `docs/MILESTONE_V2_SEALED_TOURNAMENT.md`.
- Create `docs/live-evidence/STUDIONET_V2_TOURNAMENT.md` with Explorer links.
- Create/update deployment JSON with new contract and deploy transaction.
- Add immutable compare from baseline `0797299` to final milestone commit.
- Update README, CHANGELOG, compliance matrix and limitations.
- Mark old address as v1 evidence, not current production.

## Production release

After runtime proof:

- Rotate `canonicalContractAddress`.
- Deploy latest frontend to Vercel.
- Verify HTTP 200, visible v2 capability and address in production bundle.
- Run a read-only browser walkthrough against the new records.
- Commit/push final evidence only after links are verified.

## Submission package

- Title focused on sealed multi-provider procurement.
- Changes under 1000 characters; quantify tests and live roles.
- Evidence: immutable compare, milestone doc, Studionet report, contract Explorer,
  live app and important feature/security commits.
- State limitations honestly. Never claim audit, formal verification or successful
  positive jury outcome without direct evidence.

## Success criteria

- New schema is publicly readable.
- Complete three-wallet funded lifecycle reaches terminal state.
- Final active prize/bond balance is zero.
- Conservation equation holds exactly.
- GitHub and Vercel point to the same verified deployment.
