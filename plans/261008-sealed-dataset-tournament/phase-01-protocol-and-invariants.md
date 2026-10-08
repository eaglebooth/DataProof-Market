# Phase 1 — Protocol and invariants

## Overview

Priority: highest
Status: planned

Replace the bilateral designated-provider lifecycle with a bounded multi-provider
commit/reveal tournament while preserving real custody and fail-safe exits.

## Lifecycle

```text
OPEN_COMMIT -> OPEN_REVEAL -> READY_FOR_JURY
  -> RULING_READY -> SETTLED
  -> EVIDENCE_UNAVAILABLE -> RECOVERABLE -> SETTLED
```

Submission lifecycle:

```text
COMMITTED -> REVEALED -> ELIGIBLE | INVALID
COMMITTED -> NO_REVEAL -> FORFEITED
```

## Contract design

Modify `G:\Genlayer\DataProof-Market\contracts\DataProofMarket.py`.

### Tournament storage

- Buyer, title, use case, rubric URL/digest.
- Prize escrow and fixed provider bond.
- Commit and reveal deadlines from authoritative chain time.
- Candidate cap: minimum 2, maximum 5.
- Status, winner, runner-up, jury reason.
- Active prize/bond totals and pull-payment accounting.

### Submission storage

- Global submission ID and parent tournament ID.
- Provider address.
- Manifest/sample/license digests locked at commit.
- Immutable URLs disclosed only at reveal.
- Reveal state, eligibility, score band and rank.
- One submission per provider per tournament.

### Public writes

- `open_tournament(...)` payable: buyer funds prize.
- `commit_submission(...)` payable: exact provider bond and three digests.
- `start_reveal(tournament_id)`: deterministic deadline transition.
- `reveal_dataset(...)`: immutable URLs and bounded note.
- `close_reveal(tournament_id)`: marks no-reveals and makes jury available.
- `judge_tournament(tournament_id)`: GenLayer comparative review.
- `settle_tournament(tournament_id)`: assigns pull-payment credits.
- `recover_unavailable(tournament_id)`: bounded two-party/timeout recovery.
- `withdraw()`: CEI-protected transfer of caller credit.

Keep each public method at six parameters or fewer. Split reveal into two writes if
the deployed runner rejects the intended ABI.

## Deterministic economics

- Winner receives the funded prize.
- Every eligible reveal receives its provider bond back.
- No-reveal or invalid packet bond is credited to buyer.
- If no candidate is safely rankable, prize returns to buyer; valid reveal bonds
  still return to their providers.
- Settlement writes all credits before any withdrawal.
- Jury never proposes amounts.

## Security requirements

- Deadline source must be consensus/chain-authoritative.
- No provider may commit twice.
- Reveal URLs cannot replace locked digests.
- Candidate loops capped at five.
- Winner/runner-up IDs sanitized against eligible candidate IDs.
- Settlement and withdrawal replay-safe.
- No direct multi-recipient external transfer during settlement.
- No unbounded history scans.

## Related files

- Modify: `contracts/DataProofMarket.py`
- Replace model: `tests/test_lifecycle_model.py`
- Extend static checks: `tests/test_contract_static.py`
- Create: `docs/adr/ADR-001-sealed-dataset-tournaments.md`

## Success criteria

- All economic terminal paths conserve value exactly.
- Two to five providers can participate.
- Commitments are locked before URLs are disclosed.
- Unrevealed candidates can never win.
- All terminal funds are withdrawable by their rightful owners.
