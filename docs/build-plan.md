# DataProof Market Build Plan

## Product decision

DataProof Market is a funded dataset procurement desk. A buyer locks real GEN and
an immutable rubric. A designated provider submits an immutable manifest, bounded
sample, and license snapshot. A GenLayer jury decides the economic band:

`ACCEPT -> full provider payout`

`PARTIAL -> locked partial provider payout + buyer refund`

`REJECT -> buyer refund`

`UNAVAILABLE -> mutual recovery refund`

## Why GenLayer

Schema checks cannot determine whether a dataset is useful for a stated research
or product need, whether the sample meaningfully covers the rubric, whether the
documentation exposes leakage and provenance risks, or whether the license is
substantively compatible. Those subjective findings move escrowed value and must
not be decided by either party alone.

## Frozen interface

| Function | Caller | Value | Expected transition |
| --- | --- | ---: | --- |
| `open_bounty` | buyer | escrow | creates `OPEN` bounty |
| `submit_dataset` | stored provider | 0 | `OPEN -> PACKET_STARTED` |
| `attach_license` | stored provider | 0 | `PACKET_STARTED -> SUBMITTED` |
| `review_dataset` | either party | 0 | `SUBMITTED -> RULING_READY/UNAVAILABLE` |
| `settle_bounty` | either party | 0 | ruling to terminal transfers |
| `cancel_open_bounty` | buyer | 0 | `OPEN -> CANCELLED` and refund |
| `approve_unavailable_refund` | each party | 0 | mutual recovery and refund |
| `get_bounty` | anyone | 0 | bounded record read |
| `get_state` | anyone | 0 | aggregate ledger read |

## Delivery phases

1. Stable contract and local behavioral model.
2. Contract-connected frontend with state-driven primary action.
3. Studio schema and deployment after explicit approval.
4. Two-wallet live happy path and adversarial matrix.
5. Production release only after every release-evidence row passes.
