import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";
import { TransactionStatus } from "genlayer-js/types";

type NetworkName = "studionet";

declare global {
  interface Window {
    ethereum?: {
      request: (args: { method: string; params?: unknown[] }) => Promise<unknown>;
    };
  }
}

const network: NetworkName = "studionet";
const endpoint = process.env.NEXT_PUBLIC_GENLAYER_RPC;
export const canonicalContractAddress = "0x6e2F654E69562129aC62ea0a0289CAf960e6b168";
const readClient = createClient({
  chain: studionet,
  ...(endpoint ? { endpoint } : {}),
});

type ReceiptLike = {
  statusName?: string;
  txExecutionResultName?: string;
  txDataDecoded?: unknown;
};

type RuntimeClient = {
  connect?: (name: NetworkName) => Promise<unknown>;
  readContract: (args: { address: string; functionName: string; args: unknown[] }) => Promise<unknown>;
  writeContract: (args: { address: string; functionName: string; args: unknown[]; value: bigint }) => Promise<string>;
  waitForTransactionReceipt: (args: {
    hash: `0x${string}`;
    status: string;
    interval?: number;
    retries?: number;
    fullTransaction?: boolean;
  }) => Promise<ReceiptLike>;
  getTransaction: (args: { hash: `0x${string}` }) => Promise<ReceiptLike>;
};

export type ContractResult = {
  success: boolean;
  pending?: boolean;
  data?: unknown;
  hash?: string;
  status?: string;
  error?: string;
  verification?: "receipt" | "state_required";
};

export function configuredAddress() {
  return canonicalContractAddress;
}

export async function connectWallet(): Promise<ContractResult> {
  if (typeof window === "undefined" || !window.ethereum) {
    return { success: false, error: "Install or enable a browser wallet to continue." };
  }
  try {
    const accounts = (await window.ethereum.request({
      method: "eth_requestAccounts",
      params: [],
    })) as string[];
    return accounts[0]
      ? { success: true, data: accounts[0] }
      : { success: false, error: "No wallet account selected." };
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : "Wallet connection failed." };
  }
}

export async function readContract(functionName: string, args: unknown[] = []): Promise<ContractResult> {
  const address = configuredAddress();
  if (!address) return { success: false, error: "Add a deployed contract address first." };
  try {
    const data = await (readClient as unknown as RuntimeClient).readContract({
      address,
      functionName,
      args,
    });
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : "Contract read failed." };
  }
}

const terminalStatuses = new Set(["ACCEPTED", "FINALIZED"]);

export async function writeContract(
  functionName: string,
  args: unknown[] = [],
  value = BigInt(0),
): Promise<ContractResult> {
  if (typeof window === "undefined" || !window.ethereum) {
    return { success: false, error: "Connect a wallet before writing." };
  }
  const address = configuredAddress();
  if (!address) return { success: false, error: "Add a deployed contract address first." };

  let hash = "";
  let runtime: RuntimeClient | null = null;
  try {
    const accounts = (await window.ethereum.request({
      method: "eth_requestAccounts",
      params: [],
    })) as string[];
    if (!accounts[0]) return { success: false, error: "No wallet account selected." };
    runtime = createClient({
      chain: studionet,
      ...(endpoint ? { endpoint } : {}),
      provider: window.ethereum,
      account: accounts[0] as `0x${string}`,
    }) as unknown as RuntimeClient;
    if (runtime.connect) await runtime.connect(network);
    hash = await runtime.writeContract({
      address,
      functionName,
      args,
      value,
    });
    const receipt = await runtime.waitForTransactionReceipt({
      hash: hash as `0x${string}`,
      status: TransactionStatus.ACCEPTED,
      interval: 2000,
      retries: 120,
      fullTransaction: false,
    });
    let observed = receipt;
    if (!observed.txExecutionResultName) {
      try {
        observed = await runtime.getTransaction({ hash: hash as `0x${string}` });
      } catch {
        observed = receipt;
      }
    }
    const status = observed.statusName || receipt.statusName;
    if (!terminalStatuses.has(status || "")) {
      return { success: false, pending: true, hash, status, error: `Transaction is still ${status || "processing"}.` };
    }
    const execution = observed.txExecutionResultName;
    if (execution && !["SUCCESS", "SUCCEEDED", "ACCEPTED"].includes(execution)) {
      return { success: false, hash, status, error: `Contract execution returned ${execution}.` };
    }
    return {
      success: true,
      hash,
      status,
      data: observed.txDataDecoded ?? receipt.txDataDecoded,
      verification: observed.txDataDecoded ? "receipt" : "state_required",
    };
  } catch (error) {
    if (hash && runtime) {
      try {
        const transaction = await runtime.getTransaction({ hash: hash as `0x${string}` });
        const status = transaction.statusName || "PROCESSING";
        if (!terminalStatuses.has(status)) {
          return { success: false, pending: true, hash, status, error: `Do not resubmit. Existing transaction is ${status}.` };
        }
      } catch {
        // Preserve the originating SDK or contract error.
      }
    }
    return { success: false, hash: hash || undefined, error: error instanceof Error ? error.message : "Contract write failed." };
  }
}

export const networkLabel = network === "studionet" ? "Studionet" : network;
