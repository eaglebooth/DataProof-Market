# Phase 2 — Comparative jury and tests

## Overview

Priority: high
Status: planned

Use GenLayer to compare multiple revealed datasets against the same immutable
rubric while keeping ranking output closed, bounded and safely validated.

## Jury input

Read deterministic storage into a bounded snapshot before the nondeterministic
closure. For each candidate, fetch:

- Manifest.
- Bounded representative sample.
- License snapshot.
- Provider disclosure note.

The prompt evaluates rubric coverage, usability, provenance, leakage/duplication
risk, documentation quality and license compatibility. Unavailable or digest-
inconsistent candidates become ineligible, not guessed winners.

## Consensus output

Suggested structured result:

```json
{
  "outcome": "RANKED|NO_QUALIFIED_DATASET|UNAVAILABLE",
  "winner_id": 0,
  "runner_up_id": 1,
  "winner_band": "STRONG|ACCEPTABLE",
  "reason": "bounded explanation"
}
```

Use `prompt_comparative` to compare the substantive ranking and qualification.
After consensus, deterministic code must:

- Coerce outcome and band to closed vocabularies.
- Accept IDs only from the eligible revealed set.
- Reject duplicate winner/runner-up IDs.
- Force no winner for `NO_QUALIFIED_DATASET` or `UNAVAILABLE`.
- Never use prose/confidence to calculate money.

## Test plan

Target at least 45 meaningful tests across direct runner, model and static checks.

### Behavioral

- Two, three and five-provider tournaments.
- Winner selection among eligible reveals.
- No-qualified-dataset refund.
- Unavailable recovery.
- Exact bond refund and no-reveal forfeiture.
- Deadline boundary behavior.
- One-provider and zero-provider non-reviewable states.

### Adversarial

- Duplicate provider commit.
- Commit/reveal/settle replay.
- Wrong bond and zero prize.
- Reveal before/after window.
- Digest substitution.
- Mutable/non-immutable URL.
- Hallucinated winner ID.
- Winner equals runner-up.
- Unrevealed or invalid candidate selected by model.
- Outsider state transition or withdrawal.
- Double withdrawal and reentrancy-sensitive ordering.

### Property tests

Enumerate/fuzz candidate counts, reveal subsets and jury outcomes. Assert:

```text
received == active_prize + active_bonds + withdrawable + withdrawn
```

and each provider receives at most its bond plus an explicitly awarded prize.

## Related files

- Modify: `contracts/DataProofMarket.py`
- Modify: `tests/test_contract_static.py`
- Replace/expand: `tests/test_lifecycle_model.py`
- Create: `tests/test_tournament_property.py`
- Create: `tests/test_jury_sanitization.py`

## Success criteria

- Prompt tests prove every candidate packet reaches the jury.
- Hallucinated IDs never enter state.
- All payout paths satisfy conservation.
- Local runner/compiler, full Python suite pass.
