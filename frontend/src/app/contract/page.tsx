"use client";

import { ExternalLink, RotateCcw } from "lucide-react";
import { useEffect, useState } from "react";
import { Notice } from "@/components/Notice";
import {
  configuredAddress,
  readContract,
  restoreConfiguredAddress,
  setConfiguredAddress,
} from "@/lib/genlayer";
import { parseJsonResult, shortAddress } from "@/lib/format";
import { MarketState } from "@/lib/types";

export default function ContractPage() {
  const [address, setAddress] = useState("");
  const [notice, setNotice] = useState("Paste a Studionet deployment to verify it at runtime.");
  const [tone, setTone] = useState<"info" | "error" | "success">("info");

  useEffect(() => {
    const timer = window.setTimeout(() => setAddress(configuredAddress()), 0);
    return () => window.clearTimeout(timer);
  }, []);

  async function verify() {
    if (!/^0x[a-fA-F0-9]{40}$/.test(address)) {
      setTone("error");
      setNotice("Enter a valid 42-character contract address.");
      return;
    }
    setConfiguredAddress(address);
    const result = await readContract("get_state");
    if (!result.success) {
      setTone("error");
      setNotice(result.error || "The selected contract did not respond.");
      return;
    }
    try {
      const state = parseJsonResult<MarketState>(result.data);
      setTone("success");
      setNotice(`Live DataProof state received: ${state.bounty_count} requests, ${state.active_escrow} wei active escrow.`);
    } catch (error) {
      setTone("error");
      setNotice(error instanceof Error ? error.message : "Unreadable state response.");
    }
  }

  function restore() {
    restoreConfiguredAddress();
    const next = process.env.NEXT_PUBLIC_CONTRACT_ADDRESS || "";
    setAddress(next);
    setTone("info");
    setNotice(next ? `Production default restored: ${shortAddress(next)}` : "No production address is configured yet.");
  }

  const explorer = address ? `https://explorer-studio.genlayer.com/address/${address}` : "";

  return (
    <section className="contract-page">
      <div className="work-intro">
        <p className="eyebrow">REVIEWER-SELECTABLE DEPLOYMENT</p>
        <h1>Verify the contract you use.</h1>
        <p>A runtime override lets reviewers inspect another deployment without rebuilding the frontend.</p>
      </div>
      <div className="connection-panel">
        <label>Studionet contract address<input value={address} onChange={(event) => setAddress(event.target.value)} placeholder="0x..." /></label>
        <Notice tone={tone}>{notice}</Notice>
        <div className="button-row">
          <button className="button button-primary" onClick={() => void verify()} type="button">Use and verify</button>
          <button className="button button-quiet" onClick={restore} type="button"><RotateCcw size={16} /> Restore default</button>
          {explorer && <a className="text-link" href={explorer} rel="noreferrer" target="_blank">Open Explorer <ExternalLink size={15} /></a>}
        </div>
      </div>
    </section>
  );
}
