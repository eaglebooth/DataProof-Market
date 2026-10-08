import { accountFrom, assert, clientFor, print, read, required, write } from "./live-helpers.mjs";

const address = required("CONTRACT_ADDRESS");
const buyer = accountFrom("BUYER_PRIVATE_KEY");
const providerA = accountFrom("PROVIDER_A_PRIVATE_KEY");
const providerB = accountFrom("PROVIDER_B_PRIVATE_KEY");
const buyerClient = clientFor(buyer);
const aClient = clientFor(providerA);
const bClient = clientFor(providerB);
const prize = BigInt(process.env.PRIZE_WEI || "1000");
const bond = BigInt(process.env.BOND_WEI || "100");

const state0 = JSON.parse(await read(buyerClient, address, "get_state"));
const tournamentId = BigInt(state0.tournament_count);
const openedTx = await write(buyerClient, address, "open_tournament", [
  process.env.DATASET_TITLE || "Sealed public mobility dataset tournament",
  process.env.USE_CASE || "Select the strongest documented dataset for training and validating an urban accessibility model with traceable provenance and compatible reuse rights.",
  required("RUBRIC_URL"), required("RUBRIC_SHA256"), bond, 3n,
], prize);
print({ step: "open_tournament", transaction: openedTx, tournamentId: tournamentId.toString() });

for (const [client, suffix] of [[aClient, "A"], [bClient, "B"]]) {
  const tx = await write(client, address, "commit_submission", [tournamentId, required(`MANIFEST_${suffix}_SHA256`), required(`SAMPLE_${suffix}_SHA256`), required(`LICENSE_${suffix}_SHA256`)], bond);
  print({ step: `commit_${suffix}`, transaction: tx });
}

async function waitUntil(timestamp) {
  while (Math.floor(Date.now() / 1000) < timestamp) {
    const remaining = timestamp - Math.floor(Date.now() / 1000);
    print({ waitingSeconds: remaining });
    await new Promise((resolve) => setTimeout(resolve, Math.min(15, remaining) * 1000));
  }
}

let tournament = JSON.parse(await read(buyerClient, address, "get_tournament", [tournamentId]));
await waitUntil(Number(tournament.commit_deadline));
print({ step: "start_reveal", transaction: await write(buyerClient, address, "start_reveal", [tournamentId]) });

for (const [client, suffix] of [[aClient, "A"], [bClient, "B"]]) {
  const tx = await write(client, address, "reveal_dataset", [tournamentId, required(`MANIFEST_${suffix}_URL`), required(`SAMPLE_${suffix}_URL`), required(`LICENSE_${suffix}_URL`), `Provider ${suffix} discloses provenance, schema, collection limits, leakage controls, and license compatibility in this immutable packet.`]);
  print({ step: `reveal_${suffix}`, transaction: tx });
}

tournament = JSON.parse(await read(buyerClient, address, "get_tournament", [tournamentId]));
await waitUntil(Number(tournament.reveal_deadline));
print({ step: "close_reveal", transaction: await write(buyerClient, address, "close_reveal", [tournamentId]) });
print({ step: "judge", transaction: await write(buyerClient, address, "judge_tournament", [tournamentId]) });
tournament = JSON.parse(await read(buyerClient, address, "get_tournament", [tournamentId]));
assert(["RULING_READY", "EVIDENCE_UNAVAILABLE"].includes(tournament.status), "Unexpected jury state", tournament);
if (tournament.status === "RULING_READY") {
  print({ step: "settle_tournament", transaction: await write(buyerClient, address, "settle_tournament", [tournamentId]) });
} else {
  print({ step: "buyer_recovery_approval", transaction: await write(buyerClient, address, "recover_unavailable", [tournamentId]) });
  print({ step: "provider_recovery_approval", transaction: await write(aClient, address, "recover_unavailable", [tournamentId]) });
}

const finalState = JSON.parse(await read(buyerClient, address, "get_state"));
const finalTournament = JSON.parse(await read(buyerClient, address, "get_tournament", [tournamentId]));
assert(finalTournament.status === "SETTLED", "Tournament did not settle", finalTournament);
assert(BigInt(finalState.active_prizes) === 0n, "Prize remained active after settlement", finalState);
assert(BigInt(finalState.active_bonds) === 0n, "Bond remained active after settlement", finalState);
const conserved = BigInt(finalState.total_received) === BigInt(finalState.active_prizes) + BigInt(finalState.active_bonds) + BigInt(finalState.total_credited) + BigInt(finalState.total_withdrawn);
assert(conserved, "Custody invariant failed", finalState);

for (const [client, label, account] of [[buyerClient, "buyer", buyer], [aClient, "provider_a", providerA], [bClient, "provider_b", providerB]]) {
  const credit = BigInt(await read(client, address, "get_withdrawable", [account.address]));
  if (credit > 0n) print({ step: `withdraw_${label}`, amount: credit.toString(), transaction: await write(client, address, "withdraw") });
  assert(BigInt(await read(client, address, "get_withdrawable", [account.address])) === 0n, `${label} credit was not withdrawn`);
}
const withdrawnState = JSON.parse(await read(buyerClient, address, "get_state"));
assert(BigInt(withdrawnState.total_credited) === 0n, "Withdrawable credits remain", withdrawnState);
assert(BigInt(withdrawnState.total_withdrawn) === BigInt(withdrawnState.total_received), "Final custody totals do not match", withdrawnState);
print({ verified: true, tournament: finalTournament, settledState: finalState, withdrawnState, conserved });
