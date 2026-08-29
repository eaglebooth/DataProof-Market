# Explorer submission copy

## Project name

DataProof Market — AI-Adjudicated Dataset Escrow

## Primary tag

Marketplaces

## Suggested topic tag

Data Marketplaces

## One-liner

A funded dataset marketplace where GenLayer evaluates immutable evidence and settles escrow by consensus.

## Description

DataProof Market lets a buyer lock real GEN behind a dataset request and a
fixed partial-payout policy. A provider submits content-addressed manifest,
sample, and license evidence. GenLayer validators independently assess semantic
fitness, documentation, provenance risk, leakage risk, and license
compatibility, then agree on ACCEPT, PARTIAL, REJECT, or UNAVAILABLE.
Deterministic contract logic maps that bounded verdict to the locked payout,
prevents replay, conserves escrow, and provides a two-party recovery path when
evidence cannot be safely evaluated.

## Exact reviewer path

1. Open <https://dataproof-market.vercel.app> and confirm the header shows Studionet.
2. Open an existing bounty from the market directory; no wallet is required for read-only verification.
3. Open `/contract`, click **Read live state**, and confirm the canonical contract responds.
4. Follow **Open Explorer** and verify `0x4AD7AaDf9e75563702B849866f55b524dA7420c1`.
5. For a funded test, connect a buyer wallet, open **Fund request**, enter a provider wallet, immutable rubric URL/digest, escrow, and partial reward, then submit **Open funded request**.
6. Connect the named provider wallet, open the new bounty, lock manifest/sample evidence, then attach the license snapshot.
7. Either named party runs the GenLayer jury. After `RULING_READY`, execute the verdict.
8. Reload the bounty and verify its terminal state, transaction link, provider payout/buyer refund, and conserved aggregate totals.

## Expected verification outcome

The reviewer can read the canonical Studionet state without a wallet, inspect
the existing funded lifecycle, and follow every transaction in Explorer. A new
two-wallet run progresses through funded request, evidence lock, semantic jury,
and exactly-once settlement. The final provider payout plus buyer refund equals
the original escrow, and active escrow decreases by the settled amount.

## Links

- Live app: <https://dataproof-market.vercel.app>
- GitHub: <https://github.com/eaglebooth/DataProof-Market>
- Explorer: <https://explorer-studio.genlayer.com/address/0x4AD7AaDf9e75563702B849866f55b524dA7420c1>
