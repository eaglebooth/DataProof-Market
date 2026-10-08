# Explorer submission copy

## Project name

DataProof Market — AI-Adjudicated Dataset Escrow

## Primary tag

Marketplaces

## Suggested topic tag

Data Marketplaces

## One-liner

A sealed dataset tournament that verifies immutable evidence, ranks qualified providers by consensus, and settles escrow on-chain.

## Description

DataProof Market lets a buyer fund a sealed tournament for two to five dataset
providers. Providers post liveness bonds, commit hidden submissions, then reveal
content-addressed evidence. GenLayer first fetches the raw evidence bytes and
recomputes SHA-256 under `strict_eq`; only eligible reveals enter a blinded
`prompt_comparative` jury that ranks fitness, provenance, documentation, leakage
risk, and license compatibility. Deterministic settlement pays the winner,
refunds valid bonds, penalizes liveness failures, supports recovery, prevents
replay, and preserves a fully auditable conservation invariant.

## Exact reviewer path

1. Open <https://dataproof-market.vercel.app> and confirm the header shows Studionet.
2. Open an existing tournament from the market directory; no wallet is required for read-only verification.
3. Open `/contract`, click **Read live state**, and confirm two tournaments, four submissions, and the canonical contract.
4. Follow **Open Explorer** and verify `0x6e2F654E69562129aC62ea0a0289CAf960e6b168`.
5. For a funded test, connect a buyer wallet and open a tournament with 2–5 invited providers, a prize, reveal bonds, and explicit deadlines.
6. Each provider connects, posts its bond, and commits a salted evidence digest before the commit deadline.
7. Start reveal, reveal the URL/digest/salt, and close the phase after every provider reveals or the deadline passes.
8. Run the comparative jury, settle the terminal result, and let each participant withdraw its credited balance.
9. Reload the tournament and verify the ranking or no-winner reason, Explorer transactions, and conserved aggregate totals.

## Expected verification outcome

The reviewer can read the canonical Studionet state without a wallet and follow
two complete funded lifecycles in Explorer. Tournament 0 proves that byte-valid
but semantically irrelevant evidence is rejected with no winner. Tournament 1
proves that two eligible providers can be ranked and the winner paid. The final
state reports 2,400 received, 2,400 withdrawn, and zero remaining liabilities.

## Links

- Live app: <https://dataproof-market.vercel.app>
- GitHub: <https://github.com/eaglebooth/DataProof-Market>
- Explorer: <https://explorer-studio.genlayer.com/address/0x6e2F654E69562129aC62ea0a0289CAf960e6b168>
- Immutable v2 comparison: <https://github.com/eaglebooth/DataProof-Market/compare/0797299...2fa6a37>
- Studionet transaction evidence: <https://github.com/eaglebooth/DataProof-Market/blob/main/docs/release-evidence.md>
