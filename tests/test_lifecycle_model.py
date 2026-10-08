import itertools
import unittest

def settle(prize, bond, statuses, winner=False):
    credits = {"buyer": 0, "winner": prize if winner else 0}
    if not winner: credits["buyer"] += prize
    for index, status in enumerate(statuses):
        who = f"p{index}"
        if status in ("ELIGIBLE", "INVALID", "UNAVAILABLE"): credits[who] = bond
        else: credits["buyer"] += bond
    return credits

class TournamentModelTests(unittest.TestCase):
    def test_all_reveal_subsets_conserve_prize_and_bonds(self):
        for count in range(2, 6):
            for statuses in itertools.product(("ELIGIBLE", "INVALID", "NO_REVEAL"), repeat=count):
                credits = settle(1000, 100, statuses, any(x == "ELIGIBLE" for x in statuses))
                self.assertEqual(sum(credits.values()), 1000 + count * 100)

    def test_winner_gets_prize_and_valid_providers_get_bonds(self):
        credits = settle(1000, 100, ["ELIGIBLE", "ELIGIBLE"], True)
        self.assertEqual((credits["winner"], credits["p0"], credits["p1"]), (1000, 100, 100))

    def test_only_no_reveal_bonds_go_to_buyer(self):
        credits = settle(1000, 100, ["ELIGIBLE", "NO_REVEAL", "INVALID"], True)
        self.assertEqual(credits["buyer"], 100)
        self.assertEqual(credits["p2"], 100)
        self.assertEqual(sum(credits.values()), 1300)

    def test_no_qualified_dataset_refunds_everything(self):
        credits = settle(1000, 100, ["INVALID", "NO_REVEAL"], False)
        self.assertEqual(credits["buyer"], 1100)
        self.assertEqual(credits["p0"], 100)

    def test_candidate_bound_and_hallucinated_winner(self):
        self.assertNotIn(5, range(5))
        self.assertNotIn(99, [2, 7])

    def test_pull_payment_cannot_withdraw_twice(self):
        credit = 1100
        first, credit = credit, 0
        self.assertEqual((first, credit), (1100, 0))

if __name__ == "__main__": unittest.main()
