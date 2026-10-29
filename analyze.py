"""Analyze match-level penalty shootout outcomes from a CSV file."""
import argparse
import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

REQUIRED = {'date', 'home_team', 'away_team', 'winner'}

def validate(rows):
    if not rows:
        raise ValueError('Input has no matches')
    clean, seen = [], set()
    for i, row in enumerate(rows, 2):
        if not REQUIRED.issubset(row):
            raise ValueError('Missing required columns')
        r = {k: (v or '').strip() for k,v in row.items() if k is not None}
        if any(not r[k] for k in REQUIRED):
            raise ValueError(f'Row {i}: missing required value')
        date.fromisoformat(r['date'])
        teams = {r['home_team'], r['away_team']}
        if len(teams) != 2 or r['winner'] not in teams:
            raise ValueError(f'Row {i}: invalid participants or winner')
        if r.get('first_shooter') and r['first_shooter'] not in teams:
            raise ValueError(f'Row {i}: first shooter must be a participant')
        key = (r['date'], tuple(sorted(teams)))
        if key in seen:
            raise ValueError(f'Row {i}: duplicate match key')
        seen.add(key); clean.append(r)
    return clean

def analyze(rows):
    rows = validate(rows)
    appearances, wins, annual = Counter(), Counter(), Counter()
    known = first_wins = 0
    for r in rows:
        appearances.update([r['home_team'], r['away_team']])
        wins[r['winner']] += 1
        annual[r['date'][:4]] += 1
        if r.get('first_shooter'):
            known += 1
            first_wins += r['winner'] == r['first_shooter']
    teams = [{'team':t,'appearances':n,'wins':wins[t],'losses':n-wins[t],
              'win_rate':wins[t]/n} for t,n in appearances.items()]
    teams.sort(key=lambda r:(-r['wins'],-r['appearances'],r['team']))
    audit = {'matches':len(rows),'teams':len(teams),'first_date':min(r['date'] for r in rows),
             'last_date':max(r['date'] for r in rows),'first_shooter_known':known,
             'first_shooter_missing':len(rows)-known,'first_shooter_wins':first_wins,
             'first_shooter_win_rate':first_wins/known if known else None,
             'total_team_appearances':sum(appearances.values()),'total_team_wins':sum(wins.values())}
    years = [{'year':y,'shootouts':annual[y]} for y in sorted(annual)]
    return teams, years, audit

def write_csv(path, rows):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def run(input_path, output):
    with open(input_path,encoding='utf-8-sig',newline='') as f:
        teams, years, audit = analyze(list(csv.DictReader(f)))
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    write_csv(out/'team_summary.csv',teams)
    write_csv(out/'annual_shootouts.csv',years)
    (out/'summary.json').write_text(json.dumps(audit,indent=2)+'\n')
    top=teams[:10][::-1]
    fig,ax=plt.subplots(figsize=(9,6))
    bars=ax.barh([r['team'] for r in top],[r['wins'] for r in top],color='#177b91')
    ax.bar_label(bars,padding=4)
    ax.set(title='Most shootout wins in the supplied dataset',xlabel='Shootout wins')
    ax.set_xlim(0,max(r['wins'] for r in top)*1.15)
    ax.spines[['top','right']].set_visible(False)
    fig.tight_layout();fig.savefig(out/'top_shootout_wins.svg');plt.close(fig)
    return audit

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input');p.add_argument('--output',default='results')
    a=p.parse_args();print(json.dumps(run(a.input,a.output),indent=2))
