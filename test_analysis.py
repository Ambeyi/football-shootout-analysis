import unittest
from analyze import analyze

def match(home='A',away='B',winner='A',first='',day='2020-01-01'):
    return dict(date=day,home_team=home,away_team=away,winner=winner,first_shooter=first)

class Tests(unittest.TestCase):
    def test_denominators_and_losses(self):
        teams,years,a=analyze([match(),match('B','C','C',day='2021-01-01')])
        t={r['team']:r for r in teams}
        self.assertEqual(t['B']['appearances'],2)
        self.assertEqual(t['B']['wins'],0)
        self.assertEqual(a['total_team_appearances'],4)
        self.assertEqual(a['total_team_wins'],2)
        self.assertEqual([r['shootouts'] for r in years],[1,1])
    def test_optional_first_shooter(self):
        _,_,a=analyze([match(first='A'),match(first='B',day='2020-01-02'),match(day='2020-01-03')])
        self.assertEqual(a['first_shooter_known'],2)
        self.assertEqual(a['first_shooter_win_rate'],.5)
        self.assertEqual(a['matches'],3)
    def test_unknown_first_shooter(self):
        self.assertIsNone(analyze([match()])[2]['first_shooter_win_rate'])
    def test_invalid_participants(self):
        for r in [match(winner='C'),match(away='A'),match(first='C'),match(day='invalid')]:
            with self.assertRaises(ValueError):analyze([r])
    def test_duplicate_reversed_teams(self):
        with self.assertRaises(ValueError):analyze([match(),match('B','A')])
    def test_empty_and_missing(self):
        for rows in [[],[{}],[match(winner='')]]:
            with self.assertRaises(ValueError):analyze(rows)

if __name__=='__main__':unittest.main()
