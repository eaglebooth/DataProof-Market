import { accountFrom, assert, attempt, clientFor, print, read, required, write } from "./live-helpers.mjs";

const address = required("CONTRACT_ADDRESS");
const buyer = accountFrom("BUYER_PRIVATE_KEY");
const provider = accountFrom("PROVIDER_PRIVATE_KEY");
const buyerClient = clientFor(buyer);
const providerClient = clientFor(provider);
const baseArgs = [
  provider.address,
  "Adversarial dataset request",
  "This funded record proves sender authorization, exact payable custody, immutable evidence locking, and guarded settlement behavior under invalid calls.",
  required("RUBRIC_URL"),
  required("RUBRIC_SHA256"),
  400n,
];

const before = JSON.parse(await read(buyerClient, address, "get_state"));
const zeroAttempt = await attempt(() => write(buyerClient, address, "open_bounty", baseArgs, 0n));
const afterZero = JSON.parse(await read(buyerClient, address, "get_state"));
assert(afterZero.bounty_count === before.bounty_count, "Zero-value call created a bounty", { before, afterZero, zeroAttempt });
assert(afterZero.total_received === before.total_received, "Zero-value call changed custody totals", { before, afterZero, zeroAttempt });
print({ check: "zero escrow rejected", verified: true, result: zeroAttempt });

const bountyId = BigInt(before.bounty_count);
const openTx = await write(buyerClient, address, "open_bounty", baseArgs, 1000n);
const opened = JSON.parse(await read(buyerClient, address, "get_bounty", [bountyId]));
assert(opened.status === "OPEN", "Adversarial record did not open", { openTx, opened });

async function expectUnchanged(label, operation) {
  const snapshot = await read(buyerClient, address, "get_bounty", [bountyId]);
  const result = await attempt(operation);
  const after = await read(buyerClient, address, "get_bounty", [bountyId]);
  assert(snapshot === after, `${label} changed contract state`, { snapshot, after, result });
  print({ check: label, verified: true, result });
}

await expectUnchanged("buyer cannot impersonate provider", () => write(buyerClient, address, "submit_dataset", [
  bountyId,
  required("MANIFEST_URL"),
  required("MANIFEST_SHA256"),
  required("SAMPLE_URL"),
  required("SAMPLE_SHA256"),
  "An unauthorized packet that must never be stored by the contract.",
]));
await expectUnchanged("early settlement rejected", () => write(buyerClient, address, "settle_bounty", [bountyId]));

await write(providerClient, address, "submit_dataset", [
  bountyId,
  required("MANIFEST_URL"),
  required("MANIFEST_SHA256"),
  required("SAMPLE_URL"),
  required("SAMPLE_SHA256"),
  "Authorized immutable packet for adversarial lifecycle verification.",
]);
await expectUnchanged("duplicate dataset core rejected", () => write(providerClient, address, "submit_dataset", [
  bountyId,
  required("MANIFEST_URL"),
  required("MANIFEST_SHA256"),
  required("SAMPLE_URL"),
  required("SAMPLE_SHA256"),
  "A second packet must not overwrite the original immutable evidence.",
]));
await expectUnchanged("buyer cannot cancel after submission begins", () => write(buyerClient, address, "cancel_open_bounty", [bountyId]));

await write(providerClient, address, "attach_license", [bountyId, required("LICENSE_URL"), required("LICENSE_SHA256")]);
await expectUnchanged("duplicate license rejected", () => write(providerClient, address, "attach_license", [
  bountyId,
  required("LICENSE_URL"),
  required("LICENSE_SHA256"),
]));

const reviewTx = await write(buyerClient, address, "review_dataset", [bountyId]);
const reviewed = JSON.parse(await read(buyerClient, address, "get_bounty", [bountyId]));
if (reviewed.status === "RULING_READY") {
  await write(providerClient, address, "settle_bounty", [bountyId]);
} else if (reviewed.status === "EVIDENCE_UNAVAILABLE") {
  await write(buyerClient, address, "approve_unavailable_refund", [bountyId]);
  await write(providerClient, address, "approve_unavailable_refund", [bountyId]);
} else {
  throw new Error(`Unexpected review status: ${reviewed.status}`);
}
await expectUnchanged("double settlement rejected", () => write(providerClient, address, "settle_bounty", [bountyId]));

const terminalBounty = JSON.parse(await read(buyerClient, address, "get_bounty", [bountyId]));
const finalState = JSON.parse(await read(buyerClient, address, "get_state"));
const conserved = BigInt(finalState.total_received)
  === BigInt(finalState.active_escrow) + BigInt(finalState.total_transferred)
  && BigInt(finalState.total_transferred)
  === BigInt(finalState.total_provider_paid) + BigInt(finalState.total_buyer_refunded);
assert(conserved, "Economic conservation invariant failed", finalState);
print({ reviewTx, terminalBounty, finalState, conserved, verified: true });
