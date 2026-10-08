# DataProof Market

> **v2 deploy candidate:** the repository contract now implements sealed,
> multi-provider dataset tournaments. The production URL and current Studionet
> address remain on verified v1 until the new storage/ABI is redeployed and its
> funded lifecycle is proven.

DataProof Market is a GenLayer-native funded marketplace for procuring useful,
well-documented, license-compatible datasets. Buyers lock real GEN against an
immutable rubric; providers submit immutable dataset evidence; a neutral on-chain
AI jury ranks only digest-verified candidates while the contract deterministically
assigns the fixed prize and provider bonds.

## Why GenLayer

Dataset usefulness, semantic coverage, provenance quality, leakage risk, and
license compatibility cannot be settled by Solidity or schema validation alone.
The judgment affects real escrow and neither buyer nor provider should control it.

## Repository

- `contracts/`: deployable Intelligent Contract
- `frontend/`: real `genlayer-js` frontend
- `frontend/scripts/`: two-wallet live lifecycle and adversarial checks
- `tests/`: local static and behavioral development checks
- `docs/`: build plan, compliance matrix, and evidence gate

## Lifecycle

`OPEN_COMMIT -> OPEN_REVEAL -> READY_FOR_JURY -> RULING_READY -> SETTLED`

Recovery:

`READY_FOR_JURY -> EVIDENCE_UNAVAILABLE -> SETTLED` after buyer + provider
approval, or after the recovery deadline. Provider deposits are reveal/liveness
bonds: fetch outages and mismatches cannot confiscate them or veto eligible rivals;
only no-reveal forfeits a bond.

## Application routes

- `/`: live market directory and protocol overview
- `/bounties/new`: one payable primary action to open a funded request
- `/bounties/:id`: state-driven workspace that exposes only the next valid action
- `/protocol`: jury limits, payout bands, and recovery rules
- `/contract`: canonical deployment, live state verification, and Explorer link

## Current status

`SUBMISSION_READY`. Contract
`0x4AD7AaDf9e75563702B849866f55b524dA7420c1` passed the two-wallet funded
lifecycle and adversarial runtime checks. The production frontend is live at
<https://dataproof-market.vercel.app> and was verified against the same
Studionet deployment.

## Local verification

```bash
python -m unittest discover -s tests -p "test_*.py"
cd frontend
npm install
npm run lint
npm run build
npm run dev
```

The local app runs at `http://localhost:3045` in this workspace. The public
frontend is hard-locked to Studionet and the canonical deployment; neither
browser storage nor Vercel environment variables can redirect it. Copy
`frontend/.env.example` to `frontend/.env.local` only when an explicit
Studionet RPC endpoint is required.

Production app: <https://dataproof-market.vercel.app>

Contract Explorer:
<https://explorer-studio.genlayer.com/address/0x4AD7AaDf9e75563702B849866f55b524dA7420c1>

## Live verification after deployment

After the v2 contract is deployed, set `CONTRACT_ADDRESS`, `BUYER_PRIVATE_KEY`,
`PROVIDER_A_PRIVATE_KEY`, `PROVIDER_B_PRIVATE_KEY`, and immutable
IPFS/Arweave URL plus SHA-256 digest pairs for the rubric, manifest, sample, and
license. Then run from `frontend/`:

```bash
npm run test:live
```

The v2 script verifies a three-wallet tournament, sealed commitments, reveals,
comparative adjudication or cooperative recovery, settlement, and exact custody
conservation. Historical v1 scripts remain explicitly suffixed `:v1`.

## Dependency note

The application pins `genlayer-js` 1.1.8. Vulnerable transitive development
packages are patched in the lockfile without changing the SDK version. Both the
full dependency audit and the production-only audit currently report zero known
vulnerabilities.

Official references:

- https://docs.genlayer.com/developers/intelligent-contracts/features/web-access
- https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle
- https://docs.genlayer.com/developers/intelligent-contracts/features/messages
- https://docs.genlayer.com/api-references/genlayer-js
