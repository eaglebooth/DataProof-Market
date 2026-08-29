"use client";

import { ExternalLink, RadioTower } from "lucide-react";
import { useState } from "react";
import { Notice } from "@/components/Notice";
import { configuredAddress, readContract } from "@/lib/genlayer";
import { parseJsonResult } from "@/lib/format";
import { MarketState } from "@/lib/types";

export default function ContractPage() {
  const address = configuredAddress();
  const [notice, setNotice] = useState("Read the canonical deployment directly from Studionet.");
  const [tone, setTone] = useState<"info" | "error" | "success">("info");

  async function verify() {
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

  const explorer = `https://explorer-studio.genlayer.com/address/${address}`;

  return (
    <section className="contract-page">
      <div className="work-intro">
        <p className="eyebrow">CANONICAL STUDIONET DEPLOYMENT</p>
        <h1>One market. One verifiable contract.</h1>
        <p>The production app is locked to the reviewed deployment. Browser storage cannot silently redirect contract reads or writes.</p>
      </div>
      <div className="connection-panel">
        <div className="contract-identity">
          <span><RadioTower size={17} /> Studionet contract</span>
          <strong>{address}</strong>
        </div>
        <Notice tone={tone}>{notice}</Notice>
        <div className="button-row">
          <button className="button button-primary" onClick={() => void verify()} type="button">Read live state</button>
          <a className="text-link" href={explorer} rel="noreferrer" target="_blank">Open Explorer <ExternalLink size={15} /></a>
        </div>
      </div>
    </section>
  );
}
