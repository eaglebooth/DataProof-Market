# Milestone v2 — Sealed Multi-Provider Dataset Tournament

## Immutable comparison base

- Baseline: [`0797299`](https://github.com/eaglebooth/DataProof-Market/commit/0797299)
- Milestone comparison: replace `DEPLOY_COMMIT` after the deploy-candidate commit is pushed.

## Material upgrade

DataProof Market changes from one buyer/one provider escrow into competitive
dataset procurement. A buyer funds one prize and fixes an immutable rubric.
Between two and five providers post real bonds and commit three evidence digests
before revealing their manifest, sample, and license packet. This removes copycat
submissions and lets the jury compare candidates under the same sealed rules.

## Consensus boundary

1. `strict_eq` verifies canonical rendered text against all committed SHA-256
   digests. A fetch outage is `UNAVAILABLE`, not fraud.
2. Only packets with exact digest matches become eligible.
3. `prompt_comparative` ranks the eligible IDs against the locked rubric.
4. The contract rejects invented winner IDs. AI never proposes an amount.
5. The fixed prize and every bond are assigned by deterministic contract code.

## Economic and recovery hardening

- Exact prize/bond accounting uses decimal strings at JSON boundaries, avoiding
  JavaScript's unsafe-integer range.
- The bond is explicitly a reveal/liveness bond: every revealed provider can
  recover it, while no-reveal bonds go to the buyer. Digest mismatches are
  disqualified but cannot veto the remaining eligible candidates. This avoids
  treating a single gateway response as sufficient proof for confiscation.
- Web outages preserve revealed bonds and enter fail-closed recovery.
- Recovery requires buyer plus one provider, or a deadline followed by either
  participating party; outsiders cannot trigger it.
- Pull withdrawals follow checks-effects-interactions and reject replay.
- The invariant is `received = active prizes + active bonds + credits + withdrawn`.

## Evidence gate

- Local production-source harness: 25 tests passing.
- Frontend lint and production build must pass before deployment.
- The production URL remains pinned to verified v1 until the v2 Studionet
  address completes the three-wallet funded lifecycle.
- Pending: deploy `contracts/DataProofMarket.py`, update the canonical address,
  run `npm run test:live`, then publish the frontend and replace this section
  with Explorer transaction links.
