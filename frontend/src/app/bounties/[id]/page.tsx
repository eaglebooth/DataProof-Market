"use client";

import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  ExternalLink,
  FileArchive,
  Fingerprint,
  Scale,
} from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { Notice } from "@/components/Notice";
import { StatusPill } from "@/components/StatusPill";
import { readContract, writeContract } from "@/lib/genlayer";
import { compactDigest, parseJsonResult, shortAddress } from "@/lib/format";
import { Bounty } from "@/lib/types";

const terminal = new Set(["PAID_FULL", "PAID_PARTIAL", "REFUNDED", "CANCELLED"]);

export default function BountyPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const [bounty, setBounty] = useState<Bounty | null>(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<{ tone: "info" | "error" | "success"; text: string }>({
    tone: "info",
    text: "Reading the selected on-chain record.",
  });
  const [core, setCore] = useState({ manifestUrl: "", manifestDigest: "", sampleUrl: "", sampleDigest: "", note: "" });
  const [license, setLicense] = useState({ url: "", digest: "" });

  const sync = useCallback(async () => {
    const result = await readContract("get_bounty", [BigInt(id)]);
    if (!result.success) {
      setNotice({ tone: "error", text: result.error || "Unable to read this request." });
      return null;
    }
    try {
      const next = parseJsonResult<Bounty>(result.data);
      if (!next.title) throw new Error("Bounty not found.");
      setBounty(next);
      setNotice({ tone: "success", text: `Live state verified: ${next.status.replaceAll("_", " ")}.` });
      return next;
    } catch (error) {
      setNotice({ tone: "error", text: error instanceof Error ? error.message : "Unreadable contract response." });
      return null;
    }
  }, [id]);

  useEffect(() => {
    const timer = window.setTimeout(() => void sync(), 0);
    return () => window.clearTimeout(timer);
  }, [sync]);

  async function transact(functionName: string, args: unknown[], expectedStatus: string | string[]) {
    setBusy(true);
    const result = await writeContract(functionName, args);
    if (!result.success) {
      setNotice({ tone: "error", text: result.error || `${functionName} failed.` });
      setBusy(false);
      return;
    }
    const next = await sync();
    const expected = Array.isArray(expectedStatus) ? expectedStatus : [expectedStatus];
    if (!next || !expected.includes(next.status)) {
      setNotice({
        tone: "error",
        text: `Transaction ${result.hash} reached ${result.status}, but the expected on-chain state was not verified.`,
      });
    } else {
      setNotice({ tone: "success", text: `On-chain state change verified. Transaction: ${result.hash}` });
    }
    setBusy(false);
  }

  async function submitCore(event: FormEvent) {
    event.preventDefault();
    await transact(
      "submit_dataset",
      [BigInt(id), core.manifestUrl, core.manifestDigest, core.sampleUrl, core.sampleDigest, core.note],
      "PACKET_STARTED",
    );
  }

  async function attachLicense(event: FormEvent) {
    event.preventDefault();
    await transact("attach_license", [BigInt(id), license.url, license.digest], "SUBMITTED");
  }

  if (!bounty) {
    return <section className="detail-page"><Notice tone={notice.tone}>{notice.text}</Notice></section>;
  }

  return (
    <section className="detail-page">
      <div className="detail-header">
        <Link className="back-link" href="/"><ArrowLeft size={16} /> Market</Link>
        <div className="detail-title">
          <span className="row-id">REQUEST #{bounty.id.padStart(2, "0")}</span>
          <h1>{bounty.title}</h1>
          <StatusPill status={bounty.status} />
        </div>
        <p>{bounty.use_case}</p>
      </div>

      <div className="evidence-ledger">
        <div>
          <span>BUYER</span><strong>{shortAddress(bounty.buyer)}</strong>
          <span>PROVIDER</span><strong>{shortAddress(bounty.provider)}</strong>
        </div>
        <div>
          <span>FULL ESCROW</span><strong>{bounty.escrow} wei</strong>
          <span>PARTIAL BAND</span><strong>{bounty.partial_reward} wei</strong>
        </div>
        <div>
          <span>RUBRIC SNAPSHOT</span>
          <a href={bounty.rubric_url} rel="noreferrer" target="_blank">Open source <ExternalLink size={13} /></a>
          <code>{compactDigest(bounty.rubric_digest)}</code>
        </div>
      </div>

      <Notice tone={notice.tone}>{notice.text}</Notice>

      {bounty.status === "OPEN" && (
        <div className="action-layout">
          <div className="action-context">
            <FileArchive />
            <p className="eyebrow">PROVIDER ACTION · 1 OF 2</p>
            <h2>Lock the dataset core.</h2>
            <p>Submit only immutable manifest and sample snapshots. The contract will not accept mutable web pages.</p>
          </div>
          <form className="action-form" onSubmit={submitCore}>
            <label>Manifest URL<input required value={core.manifestUrl} onChange={(e) => setCore({ ...core, manifestUrl: e.target.value })} placeholder="https://ipfs.io/ipfs/..." /></label>
            <label>Manifest digest<input required value={core.manifestDigest} onChange={(e) => setCore({ ...core, manifestDigest: e.target.value })} placeholder="sha256:..." /></label>
            <label>Sample URL<input required value={core.sampleUrl} onChange={(e) => setCore({ ...core, sampleUrl: e.target.value })} placeholder="https://arweave.net/..." /></label>
            <label>Sample digest<input required value={core.sampleDigest} onChange={(e) => setCore({ ...core, sampleDigest: e.target.value })} placeholder="sha256:..." /></label>
            <label>Provider note<textarea required value={core.note} onChange={(e) => setCore({ ...core, note: e.target.value })} placeholder="Explain coverage, collection method, schema, and known limitations." /></label>
            <button className="button button-primary" disabled={busy} type="submit">{busy ? "Locking..." : "Lock manifest and sample"} <ArrowRight size={17} /></button>
          </form>
        </div>
      )}

      {bounty.status === "PACKET_STARTED" && (
        <div className="action-layout">
          <div className="action-context">
            <Fingerprint />
            <p className="eyebrow">PROVIDER ACTION · 2 OF 2</p>
            <h2>Bind the license snapshot.</h2>
            <p>The separately hashed license makes commercial compatibility inspectable before the jury runs.</p>
          </div>
          <form className="action-form" onSubmit={attachLicense}>
            <label>License snapshot URL<input required value={license.url} onChange={(e) => setLicense({ ...license, url: e.target.value })} placeholder="https://ipfs.io/ipfs/..." /></label>
            <label>License digest<input required value={license.digest} onChange={(e) => setLicense({ ...license, digest: e.target.value })} placeholder="sha256:..." /></label>
            <button className="button button-primary" disabled={busy} type="submit">{busy ? "Binding..." : "Complete evidence packet"} <ArrowRight size={17} /></button>
          </form>
        </div>
      )}

      {bounty.status === "SUBMITTED" && (
        <div className="decision-panel">
          <Scale />
          <p className="eyebrow">PARTY ACTION</p>
          <h2>Ask validators to judge the packet.</h2>
          <p>Either recorded party may start review. The comparative principle checks the substantive economic band, not byte-identical reasoning.</p>
          <button className="button button-primary" disabled={busy} onClick={() => void transact("review_dataset", [BigInt(id)], ["RULING_READY", "EVIDENCE_UNAVAILABLE"])} type="button">
            {busy ? "Waiting for consensus..." : "Run GenLayer jury"} <ArrowRight size={17} />
          </button>
        </div>
      )}

      {bounty.status === "RULING_READY" && (
        <div className="verdict-panel">
          <div><p className="eyebrow">JURY VERDICT</p><strong>{bounty.decision}</strong><span>{bounty.score}/100</span></div>
          <p>{bounty.reason}</p>
          <button className="button button-primary" disabled={busy} onClick={() => void transact("settle_bounty", [BigInt(id)], ["PAID_FULL", "PAID_PARTIAL", "REFUNDED"])} type="button">
            {busy ? "Settling escrow..." : "Execute verdict"} <ArrowRight size={17} />
          </button>
        </div>
      )}

      {bounty.status === "EVIDENCE_UNAVAILABLE" && (
        <div className="recovery-panel">
          <p className="eyebrow">MUTUAL RECOVERY</p>
          <h2>One approval from each party.</h2>
          <p>{bounty.reason}</p>
          <div className="approval-grid">
            <span>Buyer {bounty.buyer_recovery === "1" ? <CheckCircle2 /> : "waiting"}</span>
            <span>Provider {bounty.provider_recovery === "1" ? <CheckCircle2 /> : "waiting"}</span>
          </div>
          <button className="button button-primary" disabled={busy} onClick={() => void transact("approve_unavailable_refund", [BigInt(id)], ["EVIDENCE_UNAVAILABLE", "REFUNDED"])} type="button">
            Approve recovery <ArrowRight size={17} />
          </button>
        </div>
      )}

      {terminal.has(bounty.status) && (
        <div className="terminal-panel">
          <CheckCircle2 />
          <p className="eyebrow">FINAL ON-CHAIN STATE</p>
          <h2>{bounty.status.replaceAll("_", " ")}</h2>
          <p>{bounty.reason}</p>
        </div>
      )}

      {bounty.status === "OPEN" && (
        <button className="danger-link" disabled={busy} onClick={() => void transact("cancel_open_bounty", [BigInt(id)], "CANCELLED")} type="button">
          Buyer: cancel before submission
        </button>
      )}

      {bounty.manifest_url && (
        <section className="packet">
          <div className="section-heading"><div><p className="eyebrow">IMMUTABLE PACKET</p><h2>Locked evidence</h2></div></div>
          <div className="packet-grid">
            <Evidence label="Manifest" url={bounty.manifest_url} digest={bounty.manifest_digest} />
            <Evidence label="Sample" url={bounty.sample_url} digest={bounty.sample_digest} />
            {bounty.license_url && <Evidence label="License" url={bounty.license_url} digest={bounty.license_digest} />}
          </div>
        </section>
      )}
    </section>
  );
}

function Evidence({ label, url, digest }: { label: string; url: string; digest: string }) {
  return (
    <article>
      <span>{label}</span>
      <a href={url} rel="noreferrer" target="_blank">Open snapshot <ExternalLink size={13} /></a>
      <code>{compactDigest(digest)}</code>
    </article>
  );
}
