import { createAccount, createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";
import { TransactionStatus } from "genlayer-js/types";

export function required(name) {
  const value = process.env[name];
  if (!value) throw new Error(`Missing ${name}`);
  return value;
}

export function accountFrom(name) {
  const raw = required(name);
  return createAccount(raw.startsWith("0x") ? raw : `0x${raw}`);
}

export function clientFor(account) {
  const endpoint = process.env.GENLAYER_RPC;
  return createClient({ chain: studionet, account, ...(endpoint ? { endpoint } : {}) });
}

export async function read(client, address, functionName, args = []) {
  return client.readContract({ address, functionName, args });
}

export async function write(client, address, functionName, args = [], value = 0n) {
  const hash = await client.writeContract({ address, functionName, args, value });
  const receipt = await client.waitForTransactionReceipt({
    hash,
    status: TransactionStatus.ACCEPTED,
    interval: 2000,
    retries: 180,
    fullTransaction: false,
  });
  const transaction = receipt.txExecutionResultName ? receipt : await client.getTransaction({ hash });
  const result = {
    functionName,
    hash,
    status: transaction.statusName || receipt.statusName,
    execution: transaction.txExecutionResultName || receipt.txExecutionResultName || "NOT_EXPOSED_BY_SDK",
    returned: transaction.txDataDecoded,
  };
  assert(["ACCEPTED", "FINALIZED"].includes(result.status), `${functionName} did not reach a terminal accepted state`, result);
  assert(["SUCCESS", "SUCCEEDED", "ACCEPTED", "NOT_EXPOSED_BY_SDK"].includes(result.execution), `${functionName} execution failed`, result);
  return result;
}

export async function attempt(operation) {
  try {
    return { accepted: true, transaction: await operation() };
  } catch (error) {
    return { accepted: false, error: error instanceof Error ? error.message : String(error) };
  }
}

export function assert(condition, message, details = undefined) {
  if (condition) return;
  const suffix = details === undefined ? "" : `\n${JSON.stringify(details, null, 2)}`;
  throw new Error(`${message}${suffix}`);
}

export function print(record) {
  process.stdout.write(`${JSON.stringify(record, null, 2)}\n`);
}
