# Phase 3 — Frontend tournament workspace

## Overview

Priority: high
Status: planned

Expose the complete tournament lifecycle without hiding contract state or allowing
actions that the connected role/deadline cannot execute.

## User experience

### Buyer

- Create tournament with prize, bond, deadlines and candidate cap.
- Inspect committed/revealed candidate counts.
- Close reveal, start jury, settle and withdraw.
- See prize/bond conservation and Explorer receipts.

### Provider

- Commit three evidence digests with exact bond.
- Save a local reveal checklist; warn that losing URLs does not unlock the bond.
- Reveal immutable packet during the reveal window.
- Inspect eligibility/ranking and withdraw bond/prize credit.

### Public reviewer

- Compare all revealed packets in a candidate matrix.
- View jury outcome, winner, runner-up and bounded reasoning.
- Inspect every immutable source/digest and transaction.
- Verify aggregate custody state from contract views.

## Architecture

- Add tournament/submission TypeScript models.
- Replace bilateral bounty page with phase-aware tournament workspace.
- Add candidate matrix and settlement ledger components.
- Read contract state after every accepted write before showing success.
- Gate actions by role, phase, deadline and existing submission.
- Keep Studionet/address hard-lock until deployment rotation.

## Related files

- Modify: `frontend/src/lib/types.ts`
- Modify: `frontend/src/lib/genlayer.ts`
- Modify: `frontend/src/app/page.tsx`
- Modify: `frontend/src/app/bounties/new/page.tsx`
- Replace: `frontend/src/app/bounties/[id]/page.tsx`
- Create: `frontend/src/components/CandidateMatrix.tsx`
- Create: `frontend/src/components/TournamentTimeline.tsx`
- Create: `frontend/src/components/SettlementLedger.tsx`
- Modify: `frontend/src/app/protocol/page.tsx`
- Modify: `frontend/src/app/globals.css`
- Add frontend logic tests for deadline and role gating.

## Verification

- ESLint passes.
- Next.js production build passes.
- Component/logic tests pass.
- No stale v1 method names in production paths.
- Production bundle contains only the new verified address after rotation.

## Success criteria

- Three-wallet workflow is understandable without documentation.
- Every accepted transaction links to Explorer.
- Jury ranking and deterministic money flow are separately explained.
- No invalid lifecycle action is presented as executable.
