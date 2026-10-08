# Milestone v2 — Sealed Multi-Provider Dataset Tournament

## Immutable comparison base

- Baseline: [`0797299`](https://github.com/eaglebooth/DataProof-Market/commit/0797299)
- Core milestone comparison: [`0797299...2fa6a37`](https://github.com/eaglebooth/DataProof-Market/compare/0797299...2fa6a37)

## Material upgrade

DataProof Market changes from one buyer/one provider escrow into competitive
dataset procurement. A buyer funds one prize and fixes an immutable rubric.
Between two and five providers post real bonds and commit three evidence digests
before revealing their manifest, sample, and license packet. This removes copycat
submissions and lets the jury compare candidates under the same sealed rules.

## Consensus boundary

1. `strict_eq` verifies raw immutable bytes from `web.get` against committed
   SHA-256 digests; `web.render` is used only for semantic input.
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

- Local suite: 36 tests passing; frontend lint and production build pass.
- Canonical Studionet contract: [`0x6e2F...b168`](https://explorer-studio.genlayer.com/address/0x6e2F654E69562129aC62ea0a0289CAf960e6b168).
- Tournament `0`: two eligible packets, semantic `NO_QUALIFIED_DATASET`, exact
  buyer/provider refunds, all credits withdrawn.
- Tournament `1`: `RANKED`, winner submission `2`, runner-up `3`; winner withdrew
  `1100 wei` and runner-up withdrew `100 wei`.
- Final invariant: `total_received = total_withdrawn = 2400`, with zero active
  prizes, active bonds, or withdrawable credits.
