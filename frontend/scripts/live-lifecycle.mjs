import { accountFrom, assert, clientFor, print, read, required, write } from "./live-helpers.mjs";

const address = required("CONTRACT_ADDRESS");
const buyer = accountFrom("BUYER_PRIVATE_KEY");
const provider = accountFrom("PROVIDER_PRIVATE_KEY");
const buyerClient = clientFor(buyer);
const providerClient = clientFor(provider);
const escrow = BigInt(process.env.ESCROW_WEI || "1000");
const partial = BigInt(process.env.PARTIAL_WEI || "400");

const stateBefore = JSON.parse(await read(buyerClient, address, "get_state"));
const bountyId = BigInt(stateBefore.bounty_count);
const openedTx = await write(buyerClient, address, "open_bounty", [
  provider.address,
  process.env.DATASET_TITLE || "Verified public mobility sample",
  process.env.USE_CASE || "Train and validate an urban accessibility model using documented public mobility observations with clear provenance and commercial reuse rights.",
  required("RUBRIC_URL"),
  required("RUBRIC_SHA256"),
  partial,
], escrow);
const opened = JSON.parse(await read(buyerClient, address, "get_bounty", [bountyId]));
assert(opened.status === "OPEN", "Funded request was not created", { openedTx, opened });
assert(opened.buyer === buyer.address.toLowerCase(), "Buyer is not bound to sender", opened);
assert(opened.provider === provider.address.toLowerCase(), "Provider was not recorded", opened);
assert(BigInt(opened.escrow) === escrow, "Escrow does not match transaction value", opened);
print({ step: "open_bounty", verified: true, transaction: openedTx, bounty: opened });

const coreTx = await write(providerClient, address, "submit_dataset", [
  bountyId,
  required("MANIFEST_URL"),
  required("MANIFEST_SHA256"),
  required("SAMPLE_URL"),
  required("SAMPLE_SHA256"),
  process.env.SUBMISSION_NOTE || "The immutable packet documents schema, collection boundaries, provenance, quality checks, and known limitations for the supplied sample.",
]);
const core = JSON.parse(await read(buyerClient, address, "get_bounty", [bountyId]));
assert(core.status === "PACKET_STARTED", "Dataset core was not locked", { coreTx, core });
print({ step: "submit_dataset", verified: true, transaction: coreTx, bounty: core });

const licenseTx = await write(providerClient, address, "attach_license", [
  bountyId,
  required("LICENSE_URL"),
  required("LICENSE_SHA256"),
]);
const submitted = JSON.parse(await read(buyerClient, address, "get_bounty", [bountyId]));
assert(submitted.status === "SUBMITTED", "License snapshot did not complete the packet", { licenseTx, submitted });
print({ step: "attach_license", verified: true, transaction: licenseTx, bounty: submitted });

const reviewTx = await write(buyerClient, address, "review_dataset", [bountyId]);
const reviewed = JSON.parse(await read(buyerClient, address, "get_bounty", [bountyId]));
assert(["RULING_READY", "EVIDENCE_UNAVAILABLE"].includes(reviewed.status), "Jury did not produce a valid state", { reviewTx, reviewed });
print({ step: "review_dataset", verified: true, transaction: reviewTx, bounty: reviewed });

if (reviewed.status === "RULING_READY") {
  const settleTx = await write(providerClient, address, "settle_bounty", [bountyId]);
  const settled = JSON.parse(await read(buyerClient, address, "get_bounty", [bountyId]));
  assert(["PAID_FULL", "PAID_PARTIAL", "REFUNDED"].includes(settled.status), "Escrow was not settled", { settleTx, settled });
  assert(settled.escrow === "0", "Settlement did not zero record escrow", settled);
  print({ step: "settle_bounty", verified: true, transaction: settleTx, bounty: settled });
} else {
  const buyerRecovery = await write(buyerClient, address, "approve_unavailable_refund", [bountyId]);
  const providerRecovery = await write(providerClient, address, "approve_unavailable_refund", [bountyId]);
  const recovered = JSON.parse(await read(buyerClient, address, "get_bounty", [bountyId]));
  assert(recovered.status === "REFUNDED" && recovered.escrow === "0", "Mutual recovery did not refund escrow", recovered);
  print({ step: "mutual_recovery", verified: true, transactions: [buyerRecovery, providerRecovery], bounty: recovered });
}

const finalState = JSON.parse(await read(buyerClient, address, "get_state"));
const conserved = BigInt(finalState.total_received)
  === BigInt(finalState.active_escrow) + BigInt(finalState.total_transferred)
  && BigInt(finalState.total_transferred)
  === BigInt(finalState.total_provider_paid) + BigInt(finalState.total_buyer_refunded);
assert(conserved, "Economic conservation invariant failed", finalState);
print({ finalState, conserved, verified: true });
