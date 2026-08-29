# Explorer readiness

## Verified release identity

- Network: GenLayer Studionet
- Contract: `0x4AD7AaDf9e75563702B849866f55b524dA7420c1`
- Production: <https://dataproof-market.vercel.app>
- Contract source: `contracts/DataProofMarket.py`
- Consensus: `gl.eq_principle.prompt_comparative`

## Local release gates

- Contract/model/static tests must pass.
- Frontend lint and production build must pass.
- Production must expose the canonical address and must not expose a runtime override.
- The logo endpoint and canonical contract page must return HTTP 200.
- Repository, Vercel release, and Explorer address must agree.

## Contract v2 limitation

The current deployment validates the syntax of each `sha256:` commitment and
adjudicates content-addressed IPFS/Arweave sources, but it does not recompute the
digest from the fetched bytes. Do not describe the digest as cryptographically
verified by this deployment. Fixing that behavior changes contract source and
requires a new deployment plus a fresh funded lifecycle.
