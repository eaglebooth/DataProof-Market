# DataProof Market

DataProof Market is a GenLayer-native funded marketplace for procuring useful,
well-documented, license-compatible datasets. Buyers lock real GEN against an
immutable rubric; providers submit immutable dataset evidence; a neutral on-chain
AI jury chooses a full payout, locked partial payout, or refund.

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

`OPEN -> PACKET_STARTED -> SUBMITTED -> RULING_READY -> PAID_FULL | PAID_PARTIAL | REFUNDED`

Recovery:

`SUBMITTED -> EVIDENCE_UNAVAILABLE -> REFUNDED` after both parties approve.

## Application routes

- `/`: live market directory and protocol overview
- `/bounties/new`: one payable primary action to open a funded request
- `/bounties/:id`: state-driven workspace that exposes only the next valid action
- `/protocol`: jury limits, payout bands, and recovery rules
- `/contract`: runtime contract selection, live state verification, and Explorer link

## Current status

`STUDIONET_VERIFIED`. Contract
`0x4AD7AaDf9e75563702B849866f55b524dA7420c1` passed the two-wallet funded
lifecycle and adversarial runtime checks. Production hosting remains blocked
until the frontend is reviewed and deployment is explicitly approved.

## Local verification

```bash
python -m unittest discover -s tests -p "test_*.py"
cd frontend
npm install
npm run lint
npm run build
npm run dev
```

The local app runs at `http://localhost:3045` in this workspace. The local
environment points to the verified deployment; reviewers may also select an
exact Studionet deployment at runtime on `/contract`.

## Live verification after deployment

Set `CONTRACT_ADDRESS`, `BUYER_PRIVATE_KEY`, `PROVIDER_PRIVATE_KEY`, and immutable
IPFS/Arweave URL plus SHA-256 digest pairs for the rubric, manifest, sample, and
license. Then run from `frontend/`:

```bash
npm run test:live
npm run test:adversarial
```

These scripts verify accepted receipts, state changes, sender-bound permissions,
duplicate-call rejection, exact-value funding, and payout conservation against
the selected deployed contract.

## Dependency note

The application pins the current `genlayer-js` release. Its published package
currently includes an ESLint dependency chain with a `brace-expansion` advisory
and no compatible upstream fix. PostCSS and Sharp are overridden to patched
versions. `npm run lint` and `npm run build` pass; forced audit rewrites are not
used because they break the GenLayer SDK toolchain.

Official references:

- https://docs.genlayer.com/developers/intelligent-contracts/features/web-access
- https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle
- https://docs.genlayer.com/developers/intelligent-contracts/features/messages
- https://docs.genlayer.com/api-references/genlayer-js
