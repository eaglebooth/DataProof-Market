"""Development-only behavioral model.

These tests exercise intended invariants quickly. They do not prove GenLayer
runtime behavior; deployed lifecycle and adversarial scripts remain mandatory.
"""

import unittest
from dataclasses import dataclass


@dataclass
class Bounty:
    buyer: str
    provider: str
    escrow: int
    partial: int
    status: str = "OPEN"
    decision: str = "PENDING"
    buyer_recovery: bool = False
    provider_recovery: bool = False


class Model:
    def __init__(self):
        self.balance = 0
        self.provider_paid = 0
        self.buyer_refunded = 0
        self.items: list[Bounty] = []

    def open(self, buyer, provider, escrow, partial):
        if buyer == provider:
            raise ValueError("INVALID_PROVIDER")
        if escrow <= 0:
            raise ValueError("ESCROW_REQUIRED")
        if partial <= 0 or partial >= escrow:
            raise ValueError("INVALID_PARTIAL_REWARD")
        self.items.append(Bounty(buyer, provider, escrow, partial))
        self.balance += escrow
        return len(self.items) - 1

    def submit_core(self, bounty_id, sender):
        item = self.items[bounty_id]
        if sender != item.provider:
            raise PermissionError("PROVIDER_ONLY")
        if item.status != "OPEN":
            raise ValueError("SUBMISSION_WINDOW_CLOSED")
        item.status = "PACKET_STARTED"

    def attach_license(self, bounty_id, sender):
        item = self.items[bounty_id]
        if sender != item.provider:
            raise PermissionError("PROVIDER_ONLY")
        if item.status != "PACKET_STARTED":
            raise ValueError("LICENSE_WINDOW_CLOSED")
        item.status = "SUBMITTED"

    def review(self, bounty_id, sender, decision):
        item = self.items[bounty_id]
        if sender not in (item.buyer, item.provider):
            raise PermissionError("PARTY_ONLY")
        if item.status != "SUBMITTED":
            raise ValueError("DATASET_NOT_READY")
        item.decision = decision
        item.status = "EVIDENCE_UNAVAILABLE" if decision == "UNAVAILABLE" else "RULING_READY"

    def settle(self, bounty_id, sender):
        item = self.items[bounty_id]
        if sender not in (item.buyer, item.provider):
            raise PermissionError("PARTY_ONLY")
        if item.status != "RULING_READY":
            raise ValueError("RULING_NOT_READY")
        if item.decision == "ACCEPT":
            provider_amount, buyer_amount, status = item.escrow, 0, "PAID_FULL"
        elif item.decision == "PARTIAL":
            provider_amount, buyer_amount, status = item.partial, item.escrow - item.partial, "PAID_PARTIAL"
        elif item.decision == "REJECT":
            provider_amount, buyer_amount, status = 0, item.escrow, "REFUNDED"
        else:
            raise ValueError("INVALID_SETTLEMENT_DECISION")
        self.balance -= item.escrow
        self.provider_paid += provider_amount
        self.buyer_refunded += buyer_amount
        item.escrow = 0
        item.status = status

    def cancel(self, bounty_id, sender):
        item = self.items[bounty_id]
        if sender != item.buyer:
            raise PermissionError("BUYER_ONLY")
        if item.status != "OPEN":
            raise ValueError("CANCELLATION_CLOSED")
        self.balance -= item.escrow
        self.buyer_refunded += item.escrow
        item.escrow = 0
        item.status = "CANCELLED"

    def approve_recovery(self, bounty_id, sender):
        item = self.items[bounty_id]
        if item.status != "EVIDENCE_UNAVAILABLE":
            raise ValueError("RECOVERY_NOT_AVAILABLE")
        if sender == item.buyer:
            item.buyer_recovery = True
        elif sender == item.provider:
            item.provider_recovery = True
        else:
            raise PermissionError("PARTY_ONLY")
        if item.buyer_recovery and item.provider_recovery:
            self.balance -= item.escrow
            self.buyer_refunded += item.escrow
            item.escrow = 0
            item.status = "REFUNDED"


class LifecycleModelTests(unittest.TestCase):
    def test_all_settlement_bands_conserve_value(self):
        cases = [
            ("ACCEPT", 100, 0, "PAID_FULL"),
            ("PARTIAL", 35, 65, "PAID_PARTIAL"),
            ("REJECT", 0, 100, "REFUNDED"),
        ]
        for decision, provider_paid, buyer_refunded, status in cases:
            with self.subTest(decision=decision):
                model = Model()
                bounty_id = model.open("buyer", "provider", 100, 35)
                model.submit_core(bounty_id, "provider")
                model.attach_license(bounty_id, "provider")
                model.review(bounty_id, "buyer", decision)
                model.settle(bounty_id, "provider")
                self.assertEqual(model.provider_paid, provider_paid)
                self.assertEqual(model.buyer_refunded, buyer_refunded)
                self.assertEqual(model.provider_paid + model.buyer_refunded, 100)
                self.assertEqual(model.balance, 0)
                self.assertEqual(model.items[bounty_id].status, status)

    def test_wrong_value_and_same_party_are_rejected(self):
        model = Model()
        with self.assertRaisesRegex(ValueError, "ESCROW_REQUIRED"):
            model.open("buyer", "provider", 0, 1)
        with self.assertRaisesRegex(ValueError, "INVALID_PARTIAL_REWARD"):
            model.open("buyer", "provider", 100, 100)
        with self.assertRaisesRegex(ValueError, "INVALID_PROVIDER"):
            model.open("buyer", "buyer", 100, 40)

    def test_unauthorized_and_early_calls_are_rejected(self):
        model = Model()
        bounty_id = model.open("buyer", "provider", 100, 40)
        with self.assertRaisesRegex(PermissionError, "PROVIDER_ONLY"):
            model.submit_core(bounty_id, "outsider")
        with self.assertRaisesRegex(ValueError, "LICENSE_WINDOW_CLOSED"):
            model.attach_license(bounty_id, "provider")
        with self.assertRaisesRegex(ValueError, "DATASET_NOT_READY"):
            model.review(bounty_id, "buyer", "ACCEPT")
        with self.assertRaisesRegex(ValueError, "RULING_NOT_READY"):
            model.settle(bounty_id, "buyer")

    def test_packet_and_settlement_cannot_be_replayed(self):
        model = Model()
        bounty_id = model.open("buyer", "provider", 100, 40)
        model.submit_core(bounty_id, "provider")
        with self.assertRaisesRegex(ValueError, "SUBMISSION_WINDOW_CLOSED"):
            model.submit_core(bounty_id, "provider")
        model.attach_license(bounty_id, "provider")
        with self.assertRaisesRegex(ValueError, "LICENSE_WINDOW_CLOSED"):
            model.attach_license(bounty_id, "provider")
        model.review(bounty_id, "buyer", "ACCEPT")
        model.settle(bounty_id, "provider")
        with self.assertRaisesRegex(ValueError, "RULING_NOT_READY"):
            model.settle(bounty_id, "provider")

    def test_cancel_is_buyer_only_and_open_only(self):
        model = Model()
        bounty_id = model.open("buyer", "provider", 100, 40)
        with self.assertRaisesRegex(PermissionError, "BUYER_ONLY"):
            model.cancel(bounty_id, "provider")
        model.cancel(bounty_id, "buyer")
        self.assertEqual(model.balance, 0)
        self.assertEqual(model.buyer_refunded, 100)
        with self.assertRaisesRegex(ValueError, "CANCELLATION_CLOSED"):
            model.cancel(bounty_id, "buyer")

    def test_unavailable_recovery_requires_both_parties(self):
        model = Model()
        bounty_id = model.open("buyer", "provider", 100, 40)
        model.submit_core(bounty_id, "provider")
        model.attach_license(bounty_id, "provider")
        model.review(bounty_id, "buyer", "UNAVAILABLE")
        model.approve_recovery(bounty_id, "buyer")
        self.assertEqual(model.balance, 100)
        with self.assertRaisesRegex(PermissionError, "PARTY_ONLY"):
            model.approve_recovery(bounty_id, "outsider")
        model.approve_recovery(bounty_id, "provider")
        self.assertEqual(model.balance, 0)
        self.assertEqual(model.buyer_refunded, 100)
        self.assertEqual(model.items[bounty_id].status, "REFUNDED")


if __name__ == "__main__":
    unittest.main()
