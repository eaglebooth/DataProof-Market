# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import typing
import json


@gl.evm.contract_interface
class _Recipient:
    class View:
        pass

    class Write:
        pass


class DataProofMarket(gl.Contract):
    bounty_count: u256
    bounty_buyer: TreeMap[u256, str]
    bounty_provider: TreeMap[u256, str]
    bounty_title: TreeMap[u256, str]
    bounty_use_case: TreeMap[u256, str]
    bounty_rubric_url: TreeMap[u256, str]
    bounty_rubric_digest: TreeMap[u256, str]
    bounty_manifest_url: TreeMap[u256, str]
    bounty_manifest_digest: TreeMap[u256, str]
    bounty_sample_url: TreeMap[u256, str]
    bounty_sample_digest: TreeMap[u256, str]
    bounty_license_url: TreeMap[u256, str]
    bounty_license_digest: TreeMap[u256, str]
    bounty_submission_note: TreeMap[u256, str]
    bounty_submitter: TreeMap[u256, str]
    bounty_escrow: TreeMap[u256, u256]
    bounty_partial_reward: TreeMap[u256, u256]
    bounty_status: TreeMap[u256, str]
    bounty_decision: TreeMap[u256, str]
    bounty_score: TreeMap[u256, u256]
    bounty_reason: TreeMap[u256, str]
    bounty_buyer_recovery: TreeMap[u256, u256]
    bounty_provider_recovery: TreeMap[u256, u256]

    total_received: u256
    total_provider_paid: u256
    total_buyer_refunded: u256
    total_transferred: u256
    active_escrow: u256

    def __init__(self):
        self.bounty_count = u256(0)
        self.total_received = u256(0)
        self.total_provider_paid = u256(0)
        self.total_buyer_refunded = u256(0)
        self.total_transferred = u256(0)
        self.active_escrow = u256(0)

    def _valid_address(self, value: str) -> bool:
        return value.startswith("0x") and len(value) == 42

    def _valid_immutable_url(self, value: str) -> bool:
        lowered = value.lower()
        prefix = ""
        if lowered.startswith("https://ipfs.io/ipfs/"):
            prefix = "https://ipfs.io/ipfs/"
        elif lowered.startswith("https://arweave.net/"):
            prefix = "https://arweave.net/"
        if prefix == "":
            return False
        immutable_id = lowered[len(prefix):]
        return (
            len(value) <= 500
            and len(immutable_id) >= 32
            and "example" not in immutable_id
            and "replace" not in immutable_id
        )

    def _valid_digest(self, value: str) -> bool:
        if not value.startswith("sha256:") or len(value) != 71:
            return False
        digest = value[7:]
        if digest == ("0" * 64):
            return False
        try:
            int(digest, 16)
            return True
        except Exception:
            return False

    def _is_party(self, bounty_id: u256, sender: str) -> bool:
        return (
            sender == self.bounty_buyer[bounty_id]
            or sender == self.bounty_provider[bounty_id]
        )

    def _parse_review(self, result: typing.Any) -> typing.Any:
        if isinstance(result, str):
            try:
                data = json.loads(result)
            except Exception:
                return None
        else:
            data = result
        if not isinstance(data, dict):
            return None
        decision = str(data.get("decision", "UNAVAILABLE")).upper()
        if decision not in ("ACCEPT", "PARTIAL", "REJECT", "UNAVAILABLE"):
            return None
        try:
            score = int(data.get("score", 0))
        except Exception:
            return None
        score = max(0, min(100, score))
        reason = str(data.get("reason", "No evidence-based reason returned."))[:900]
        return (decision, score, reason)

    @gl.public.write.payable
    def open_bounty(
        self,
        provider_address: str,
        title: str,
        use_case: str,
        rubric_url: str,
        rubric_digest: str,
        partial_reward: u256,
    ) -> typing.Any:
        buyer = gl.message.sender_address.as_hex.lower()
        provider = provider_address.lower()
        amount = gl.message.value

        if not self._valid_address(provider) or provider == buyer:
            raise gl.vm.UserError("INVALID_PROVIDER")
        if len(title) < 4 or len(title) > 140:
            raise gl.vm.UserError("INVALID_TITLE")
        if len(use_case) < 30 or len(use_case) > 1200:
            raise gl.vm.UserError("INVALID_USE_CASE")
        if not self._valid_immutable_url(rubric_url):
            raise gl.vm.UserError("IMMUTABLE_RUBRIC_REQUIRED")
        if not self._valid_digest(rubric_digest):
            raise gl.vm.UserError("INVALID_RUBRIC_DIGEST")
        if amount == u256(0):
            raise gl.vm.UserError("ESCROW_REQUIRED")
        if partial_reward == u256(0) or partial_reward >= amount:
            raise gl.vm.UserError("INVALID_PARTIAL_REWARD")

        bounty_id = self.bounty_count
        self.bounty_buyer[bounty_id] = buyer
        self.bounty_provider[bounty_id] = provider
        self.bounty_title[bounty_id] = title
        self.bounty_use_case[bounty_id] = use_case
        self.bounty_rubric_url[bounty_id] = rubric_url
        self.bounty_rubric_digest[bounty_id] = rubric_digest.lower()
        self.bounty_manifest_url[bounty_id] = ""
        self.bounty_manifest_digest[bounty_id] = ""
        self.bounty_sample_url[bounty_id] = ""
        self.bounty_sample_digest[bounty_id] = ""
        self.bounty_license_url[bounty_id] = ""
        self.bounty_license_digest[bounty_id] = ""
        self.bounty_submission_note[bounty_id] = ""
        self.bounty_submitter[bounty_id] = ""
        self.bounty_escrow[bounty_id] = amount
        self.bounty_partial_reward[bounty_id] = partial_reward
        self.bounty_status[bounty_id] = "OPEN"
        self.bounty_decision[bounty_id] = "PENDING"
        self.bounty_score[bounty_id] = u256(0)
        self.bounty_reason[bounty_id] = "Waiting for the provider evidence packet."
        self.bounty_buyer_recovery[bounty_id] = u256(0)
        self.bounty_provider_recovery[bounty_id] = u256(0)
        self.total_received = self.total_received + amount
        self.active_escrow = self.active_escrow + amount
        self.bounty_count = bounty_id + u256(1)
        return bounty_id

    @gl.public.write
    def submit_dataset(
        self,
        bounty_id: u256,
        manifest_url: str,
        manifest_digest: str,
        sample_url: str,
        sample_digest: str,
        submission_note: str,
    ) -> str:
        if bounty_id >= self.bounty_count:
            raise gl.vm.UserError("BOUNTY_NOT_FOUND")
        sender = gl.message.sender_address.as_hex.lower()
        if sender != self.bounty_provider[bounty_id]:
            raise gl.vm.UserError("PROVIDER_ONLY")
        if self.bounty_status[bounty_id] != "OPEN":
            raise gl.vm.UserError("SUBMISSION_WINDOW_CLOSED")
        if not self._valid_immutable_url(manifest_url):
            raise gl.vm.UserError("IMMUTABLE_MANIFEST_REQUIRED")
        if not self._valid_digest(manifest_digest):
            raise gl.vm.UserError("INVALID_MANIFEST_DIGEST")
        if not self._valid_immutable_url(sample_url):
            raise gl.vm.UserError("IMMUTABLE_SAMPLE_REQUIRED")
        if not self._valid_digest(sample_digest):
            raise gl.vm.UserError("INVALID_SAMPLE_DIGEST")
        if len(submission_note) < 20 or len(submission_note) > 800:
            raise gl.vm.UserError("INVALID_SUBMISSION_NOTE")

        self.bounty_manifest_url[bounty_id] = manifest_url
        self.bounty_manifest_digest[bounty_id] = manifest_digest.lower()
        self.bounty_sample_url[bounty_id] = sample_url
        self.bounty_sample_digest[bounty_id] = sample_digest.lower()
        self.bounty_submission_note[bounty_id] = submission_note
        self.bounty_submitter[bounty_id] = sender
        self.bounty_status[bounty_id] = "PACKET_STARTED"
        self.bounty_decision[bounty_id] = "PENDING"
        self.bounty_score[bounty_id] = u256(0)
        self.bounty_reason[bounty_id] = "Manifest and sample locked; waiting for license evidence."
        return "DATASET_CORE_LOCKED"

    @gl.public.write
    def attach_license(
        self,
        bounty_id: u256,
        license_url: str,
        license_digest: str,
    ) -> str:
        if bounty_id >= self.bounty_count:
            raise gl.vm.UserError("BOUNTY_NOT_FOUND")
        sender = gl.message.sender_address.as_hex.lower()
        if sender != self.bounty_provider[bounty_id]:
            raise gl.vm.UserError("PROVIDER_ONLY")
        if self.bounty_status[bounty_id] != "PACKET_STARTED":
            raise gl.vm.UserError("LICENSE_WINDOW_CLOSED")
        if not self._valid_immutable_url(license_url):
            raise gl.vm.UserError("IMMUTABLE_LICENSE_REQUIRED")
        if not self._valid_digest(license_digest):
            raise gl.vm.UserError("INVALID_LICENSE_DIGEST")

        self.bounty_license_url[bounty_id] = license_url
        self.bounty_license_digest[bounty_id] = license_digest.lower()
        self.bounty_status[bounty_id] = "SUBMITTED"
        self.bounty_reason[bounty_id] = "Complete immutable packet locked; waiting for jury review."
        return "DATASET_PACKET_LOCKED"

    @gl.public.write
    def review_dataset(self, bounty_id: u256) -> str:
        if bounty_id >= self.bounty_count:
            raise gl.vm.UserError("BOUNTY_NOT_FOUND")
        sender = gl.message.sender_address.as_hex.lower()
        if not self._is_party(bounty_id, sender):
            raise gl.vm.UserError("PARTY_ONLY")
        if self.bounty_status[bounty_id] != "SUBMITTED":
            raise gl.vm.UserError("DATASET_NOT_READY")

        title = self.bounty_title[bounty_id]
        use_case = self.bounty_use_case[bounty_id]
        rubric_url = self.bounty_rubric_url[bounty_id]
        rubric_digest = self.bounty_rubric_digest[bounty_id]
        manifest_url = self.bounty_manifest_url[bounty_id]
        manifest_digest = self.bounty_manifest_digest[bounty_id]
        sample_url = self.bounty_sample_url[bounty_id]
        sample_digest = self.bounty_sample_digest[bounty_id]
        license_url = self.bounty_license_url[bounty_id]
        license_digest = self.bounty_license_digest[bounty_id]
        submission_note = self.bounty_submission_note[bounty_id]

        def evaluate() -> str:
            def render_source(url: str, label: str) -> str:
                try:
                    content = gl.nondet.web.render(url, mode="text").strip()
                    if len(content) < 80:
                        return label + "_UNAVAILABLE"
                    return content[:2800]
                except Exception:
                    return label + "_UNAVAILABLE"

            rubric = render_source(rubric_url, "RUBRIC")
            manifest = render_source(manifest_url, "MANIFEST")
            sample = render_source(sample_url, "SAMPLE")
            license_text = render_source(license_url, "LICENSE")
            prompt = f"""You are the independent GenLayer dataset procurement jury.
Real escrowed GEN depends on this judgment. Evaluate semantic usefulness, not JSON shape.

BOUNTY
Title: {title}
Intended use: {use_case}
Locked rubric digest: {rubric_digest}

PROVIDER PACKET
Manifest digest: {manifest_digest}
Sample digest: {sample_digest}
License digest: {license_digest}
Provider note: {submission_note}

LOCKED RUBRIC CONTENT
{rubric}

DATASET MANIFEST CONTENT
{manifest}

BOUNDED SAMPLE CONTENT
{sample}

LICENSE SNAPSHOT CONTENT
{license_text}

Judge:
- fitness for the stated use case and rubric coverage;
- documentation, schema clarity, and usable sample quality;
- provenance disclosures and duplicate/leakage risk;
- compatibility with the required license;
- whether unavailable or contradictory sources prevent a safe payout.

Scoring:
80-100 ACCEPT: useful, documented, provenance-aware, and license-compatible.
50-79 PARTIAL: meaningful value but material gaps justify only the locked partial reward.
0-49 REJECT: unusable, misleading, incompatible, or unsupported.
If any source ends in _UNAVAILABLE, return UNAVAILABLE.

Respond with ONLY:
{{"decision":"ACCEPT|PARTIAL|REJECT|UNAVAILABLE","score":0,"reason":"evidence-based reason under 700 chars"}}"""
            return gl.nondet.exec_prompt(prompt)

        principle = """Compare the substantive economic verdict. Outputs are equivalent only
when they choose the same decision band (ACCEPT, PARTIAL, REJECT, or UNAVAILABLE)
and their scores remain in that band's stated range. Wording and minor score
differences inside the same band may differ, but license compatibility, provenance,
and evidence availability must not contradict each other."""
        parsed = self._parse_review(
            gl.eq_principle.prompt_comparative(evaluate, principle)
        )
        if parsed is None:
            self.bounty_status[bounty_id] = "EVIDENCE_UNAVAILABLE"
            self.bounty_decision[bounty_id] = "UNAVAILABLE"
            self.bounty_score[bounty_id] = u256(0)
            self.bounty_reason[bounty_id] = "Validator output could not be safely interpreted."
            return "EVIDENCE_UNAVAILABLE"

        decision, score, reason = parsed
        if decision == "ACCEPT" and score < 80:
            decision = "PARTIAL" if score >= 50 else "REJECT"
        if decision == "PARTIAL" and (score < 50 or score >= 80):
            decision = "REJECT" if score < 50 else "ACCEPT"
        if decision == "REJECT" and score >= 50:
            decision = "PARTIAL" if score < 80 else "ACCEPT"

        self.bounty_decision[bounty_id] = decision
        self.bounty_score[bounty_id] = u256(score)
        self.bounty_reason[bounty_id] = reason
        if decision in ("ACCEPT", "PARTIAL", "REJECT"):
            self.bounty_status[bounty_id] = "RULING_READY"
        else:
            self.bounty_status[bounty_id] = "EVIDENCE_UNAVAILABLE"
        return self.bounty_status[bounty_id]

    @gl.public.write
    def settle_bounty(self, bounty_id: u256) -> str:
        if bounty_id >= self.bounty_count:
            raise gl.vm.UserError("BOUNTY_NOT_FOUND")
        sender = gl.message.sender_address.as_hex.lower()
        if not self._is_party(bounty_id, sender):
            raise gl.vm.UserError("PARTY_ONLY")
        if self.bounty_status[bounty_id] != "RULING_READY":
            raise gl.vm.UserError("RULING_NOT_READY")

        amount = self.bounty_escrow[bounty_id]
        if amount == u256(0) or amount > self.balance:
            raise gl.vm.UserError("ESCROW_INVARIANT_BROKEN")
        decision = self.bounty_decision[bounty_id]
        buyer = self.bounty_buyer[bounty_id]
        provider = self.bounty_provider[bounty_id]
        provider_amount = u256(0)
        buyer_amount = u256(0)
        terminal_status = ""

        if decision == "ACCEPT":
            provider_amount = amount
            terminal_status = "PAID_FULL"
        elif decision == "PARTIAL":
            provider_amount = self.bounty_partial_reward[bounty_id]
            buyer_amount = amount - provider_amount
            terminal_status = "PAID_PARTIAL"
        elif decision == "REJECT":
            buyer_amount = amount
            terminal_status = "REFUNDED"
        else:
            raise gl.vm.UserError("INVALID_SETTLEMENT_DECISION")

        self.bounty_escrow[bounty_id] = u256(0)
        self.active_escrow = self.active_escrow - amount
        self.total_provider_paid = self.total_provider_paid + provider_amount
        self.total_buyer_refunded = self.total_buyer_refunded + buyer_amount
        self.total_transferred = self.total_transferred + amount
        self.bounty_status[bounty_id] = terminal_status
        if provider_amount > u256(0):
            _Recipient(Address(provider)).emit_transfer(value=provider_amount)
        if buyer_amount > u256(0):
            _Recipient(Address(buyer)).emit_transfer(value=buyer_amount)
        return terminal_status

    @gl.public.write
    def cancel_open_bounty(self, bounty_id: u256) -> str:
        if bounty_id >= self.bounty_count:
            raise gl.vm.UserError("BOUNTY_NOT_FOUND")
        buyer = self.bounty_buyer[bounty_id]
        if gl.message.sender_address.as_hex.lower() != buyer:
            raise gl.vm.UserError("BUYER_ONLY")
        if self.bounty_status[bounty_id] != "OPEN":
            raise gl.vm.UserError("CANCELLATION_CLOSED")

        amount = self.bounty_escrow[bounty_id]
        self.bounty_escrow[bounty_id] = u256(0)
        self.active_escrow = self.active_escrow - amount
        self.total_buyer_refunded = self.total_buyer_refunded + amount
        self.total_transferred = self.total_transferred + amount
        self.bounty_status[bounty_id] = "CANCELLED"
        self.bounty_decision[bounty_id] = "REFUND"
        self.bounty_reason[bounty_id] = "Buyer cancelled before a dataset packet was submitted."
        _Recipient(Address(buyer)).emit_transfer(value=amount)
        return "CANCELLED"

    @gl.public.write
    def approve_unavailable_refund(self, bounty_id: u256) -> str:
        if bounty_id >= self.bounty_count:
            raise gl.vm.UserError("BOUNTY_NOT_FOUND")
        if self.bounty_status[bounty_id] != "EVIDENCE_UNAVAILABLE":
            raise gl.vm.UserError("RECOVERY_NOT_AVAILABLE")
        sender = gl.message.sender_address.as_hex.lower()
        buyer = self.bounty_buyer[bounty_id]
        provider = self.bounty_provider[bounty_id]
        if sender == buyer:
            self.bounty_buyer_recovery[bounty_id] = u256(1)
        elif sender == provider:
            self.bounty_provider_recovery[bounty_id] = u256(1)
        else:
            raise gl.vm.UserError("PARTY_ONLY")

        if (
            self.bounty_buyer_recovery[bounty_id] == u256(1)
            and self.bounty_provider_recovery[bounty_id] == u256(1)
        ):
            amount = self.bounty_escrow[bounty_id]
            self.bounty_escrow[bounty_id] = u256(0)
            self.active_escrow = self.active_escrow - amount
            self.total_buyer_refunded = self.total_buyer_refunded + amount
            self.total_transferred = self.total_transferred + amount
            self.bounty_status[bounty_id] = "REFUNDED"
            self.bounty_decision[bounty_id] = "MUTUAL_REFUND"
            self.bounty_reason[bounty_id] = "Both parties approved recovery after unavailable evidence."
            _Recipient(Address(buyer)).emit_transfer(value=amount)
            return "REFUNDED"
        return "RECOVERY_APPROVAL_RECORDED"

    @gl.public.view
    def get_bounty(self, bounty_id: u256) -> str:
        if bounty_id >= self.bounty_count:
            return "{}"
        data = {
            "id": str(bounty_id),
            "buyer": self.bounty_buyer[bounty_id],
            "provider": self.bounty_provider[bounty_id],
            "title": self.bounty_title[bounty_id],
            "use_case": self.bounty_use_case[bounty_id],
            "rubric_url": self.bounty_rubric_url[bounty_id],
            "rubric_digest": self.bounty_rubric_digest[bounty_id],
            "manifest_url": self.bounty_manifest_url[bounty_id],
            "manifest_digest": self.bounty_manifest_digest[bounty_id],
            "sample_url": self.bounty_sample_url[bounty_id],
            "sample_digest": self.bounty_sample_digest[bounty_id],
            "license_url": self.bounty_license_url[bounty_id],
            "license_digest": self.bounty_license_digest[bounty_id],
            "submission_note": self.bounty_submission_note[bounty_id],
            "submitter": self.bounty_submitter[bounty_id],
            "escrow": str(self.bounty_escrow[bounty_id]),
            "partial_reward": str(self.bounty_partial_reward[bounty_id]),
            "status": self.bounty_status[bounty_id],
            "decision": self.bounty_decision[bounty_id],
            "score": str(self.bounty_score[bounty_id]),
            "reason": self.bounty_reason[bounty_id],
            "buyer_recovery": str(self.bounty_buyer_recovery[bounty_id]),
            "provider_recovery": str(self.bounty_provider_recovery[bounty_id]),
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":"))

    @gl.public.view
    def get_state(self) -> str:
        data = {
            "active_escrow": str(self.active_escrow),
            "bounty_count": str(self.bounty_count),
            "total_buyer_refunded": str(self.total_buyer_refunded),
            "total_provider_paid": str(self.total_provider_paid),
            "total_received": str(self.total_received),
            "total_transferred": str(self.total_transferred),
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":"))
