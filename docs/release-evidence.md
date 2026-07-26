# Release Evidence

This file is intentionally strict. Local tests cannot mark deployed-runtime rows
as passed.

| Gate | Status | Evidence |
| --- | --- | --- |
| Toolchain | PASS | Runner `v0.2.16`; pinned py-genlayer; SDK versions in `frontend/package.json` |
| Contract schema | PASS | Studio deployed the exact repository contract at `0x4AD7AaDf9e75563702B849866f55b524dA7420c1` |
| Functions | PASS | Frozen interface in `docs/build-plan.md` |
| Runtime writes | PASS | Full lifecycle writes were accepted and each expected state transition was read back |
| State proof | PASS | Bounties `0` and `1` reached terminal states with record escrow reduced to zero |
| Failure proof | PASS | Zero funding, sender impersonation, early settlement, evidence overwrite, late cancel, duplicate license, and double settlement left state unchanged |
| Value proof | PASS | Contract received `2000` wei, refunded `1000` wei, paid provider `1000` wei, and retained `0` active escrow |
| Consensus | PASS | Jury produced both `REJECT` and `ACCEPT` semantic verdicts on immutable web evidence |
| Address audit | PASS | Frontend `/contract` read live state from the same submitted Studionet address |
| Production | PASS | `https://dataproof-market.vercel.app` reads the submitted Studionet deployment and its two live records |
| Provenance | PASS | Case-bound submitter, immutable URLs, and SHA-256 digests are stored |
| Limitations | PASS | Large dataset bytes are not fetched; only bounded immutable artifacts are evaluated |

Release status: `SUBMISSION_READY`.

Behavioral model tests do not prove GenLayer runtime behavior. A release may be
called submission-ready only after both live scripts run against the exact
deployed address and the production frontend is rechecked against that address.

## Verified Studionet lifecycle

Contract:
[`0x4AD7AaDf9e75563702B849866f55b524dA7420c1`](https://explorer-studio.genlayer.com/address/0x4AD7AaDf9e75563702B849866f55b524dA7420c1)

Lifecycle for bounty `0`:

- Open funded request: `0xe8c7f35f5447234fc73f110c515eb7292d0a7b67b478596d7ac7e608a5ea8f06`
- Lock dataset core: `0x4f5c50ca8209333b9c389579ac67a3900c657477d4191e3737be766cf1587c71`
- Lock license evidence: `0x1e17ad33cd2458a2ce82605fbbc56284f89961b824c23c3f8596e38a67a7364c`
- Semantic jury review: `0x75fa648bde5d4141d7008b078928c015cd883d34a2bb12d43a62e0f2ceb14867`
- Buyer refund settlement: `0x2401d44fc3e73e049f59ed54fa60a2918b8355014c562f5afd49ab0306cddc9d`

Adversarial lifecycle for bounty `1`:

- Jury review: `0xfcf00985a20bc7cf6edbb5dba43a2b27aad2377d64cfa5d549fef1bd86546f5c`
- Terminal result: `PAID_FULL`, score `95`, escrow `0`
- Invalid calls were submitted separately and verified not to mutate state.

Final conservation proof:

```text
total_received = 2000
active_escrow = 0
total_transferred = 2000
total_provider_paid = 1000
total_buyer_refunded = 1000
```

## Required live commands

Set `CONTRACT_ADDRESS`, both test-wallet keys, and immutable URL/digest pairs for
`RUBRIC`, `MANIFEST`, `SAMPLE`, and `LICENSE`, then run:

```powershell
npm run test:live
npm run test:adversarial
```
