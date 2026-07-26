"use client";

import { ArrowLeft, ArrowRight, LockKeyhole } from "lucide-react";
import Link from "next/link";
import { FormEvent, useState } from "react";
import { Notice } from "@/components/Notice";
import { readContract, writeContract } from "@/lib/genlayer";
import { parseJsonResult } from "@/lib/format";
import { MarketState } from "@/lib/types";

const initial = {
  provider: "",
  title: "",
  useCase: "",
  rubricUrl: "",
  rubricDigest: "",
  escrow: "100",
  partial: "40",
};

export default function NewBountyPage() {
  const [form, setForm] = useState(initial);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<{ tone: "info" | "error" | "success"; text: string }>({
    tone: "info",
    text: "The connected wallet becomes the buyer. Escrow is transferred with this transaction.",
  });

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    const before = await readContract("get_state");
    const beforeCount = before.success ? Number(parseJsonResult<MarketState>(before.data).bounty_count) : -1;
    const result = await writeContract(
      "open_bounty",
      [form.provider, form.title, form.useCase, form.rubricUrl, form.rubricDigest, BigInt(form.partial)],
      BigInt(form.escrow),
    );
    if (!result.success) {
      setNotice({ tone: "error", text: result.error || "The funded request was not created." });
      setBusy(false);
      return;
    }
    const after = await readContract("get_state");
    if (!after.success) {
      setNotice({ tone: "info", text: `Transaction ${result.hash} reached ${result.status}. Sync the market before retrying.` });
      setBusy(false);
      return;
    }
    const afterCount = Number(parseJsonResult<MarketState>(after.data).bounty_count);
    if (beforeCount >= 0 && afterCount !== beforeCount + 1) {
      setNotice({ tone: "error", text: `Transaction ${result.hash} was accepted, but a new on-chain record was not verified.` });
    } else {
      setNotice({ tone: "success", text: `Funded request #${afterCount - 1} verified on-chain. Transaction: ${result.hash}` });
      setForm(initial);
    }
    setBusy(false);
  }

  return (
    <section className="work-page new-bounty-page">
      <div className="work-intro">
        <Link className="back-link" href="/"><ArrowLeft size={16} /> Market</Link>
        <p className="eyebrow">BUYER ACTION · PAYABLE</p>
        <h1>Fund one dataset outcome.</h1>
        <p>Define the provider, public use case, immutable rubric, and fixed partial-payout band before any evidence arrives.</p>
      </div>
      <form className="workbench" onSubmit={submit}>
        <div className="workbench-title"><LockKeyhole /><div><span>STEP 01</span><h2>Request specification</h2></div></div>
        <div className="form-grid">
          <label>Provider wallet<input required value={form.provider} onChange={(e) => setForm({ ...form, provider: e.target.value })} placeholder="0x..." /></label>
          <label>Dataset title<input required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="Verified urban tree canopy tiles" /></label>
          <label className="span-2">Intended use<textarea required value={form.useCase} onChange={(e) => setForm({ ...form, useCase: e.target.value })} placeholder="Describe the exact model, decision, or analysis this dataset must support." /></label>
          <label>Immutable rubric URL<input required value={form.rubricUrl} onChange={(e) => setForm({ ...form, rubricUrl: e.target.value })} placeholder="https://ipfs.io/ipfs/..." /></label>
          <label>Rubric SHA-256 digest<input required value={form.rubricDigest} onChange={(e) => setForm({ ...form, rubricDigest: e.target.value })} placeholder="sha256:..." /></label>
          <label>Escrow (wei)<input min="1" required type="number" value={form.escrow} onChange={(e) => setForm({ ...form, escrow: e.target.value })} /></label>
          <label>Partial reward (wei)<input min="1" required type="number" value={form.partial} onChange={(e) => setForm({ ...form, partial: e.target.value })} /></label>
        </div>
        <Notice tone={notice.tone}>{notice.text}</Notice>
        <button className="button button-primary" disabled={busy} type="submit">
          {busy ? "Funding request..." : "Lock request and escrow"} <ArrowRight size={17} />
        </button>
      </form>
    </section>
  );
}
