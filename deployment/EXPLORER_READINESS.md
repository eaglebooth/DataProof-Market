# Explorer readiness

## Verified release identity

- Network: GenLayer Studionet
- Contract: `0x6e2F654E69562129aC62ea0a0289CAf960e6b168`
- Production: <https://dataproof-market.vercel.app>
- Contract source: `contracts/DataProofMarket.py`
- Consensus: `strict_eq` for raw-byte SHA-256 eligibility, then
  `gl.eq_principle.prompt_comparative` for semantic ranking

## Local release gates

- Contract/model/static tests must pass.
- Frontend lint and production build must pass.
- Production must expose the canonical address and must not expose a runtime override.
- The logo endpoint and canonical contract page must return HTTP 200.
- Repository, Vercel release, and Explorer address must agree.

## Verified v2 release

The deployment recomputes each submitted `sha256:` commitment from the fetched
raw bytes before the entry becomes eligible. Only eligible reveals reach the
comparative jury. Two funded Studionet tournaments cover both terminal outcomes:
`NO_QUALIFIED_DATASET` with full refunds and `RANKED` with a winner payout.
After all withdrawals, the on-chain accounting invariant is closed:
`2,400 received = 2,400 withdrawn`, with zero active prizes, bonds, or credits.
