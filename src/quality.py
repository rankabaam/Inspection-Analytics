"""Compute simple quality-report metrics from entirely synthetic records."""
import argparse
import csv
from collections import defaultdict
from datetime import date
from html import escape
from pathlib import Path

FIELDS = ('check_id', 'month', 'area', 'has_finding', 'is_followup', 'repeated_finding')


def parse_bool(value, line):
    if value == 'true':
        return True
    if value == 'false':
        return False
    raise ValueError(f'Line {line}: boolean values must be true/false')


def read_checks(path):
    checks = []
    with Path(path).open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not set(FIELDS).issubset(reader.fieldnames):
            raise ValueError('CSV must contain: ' + ', '.join(FIELDS))
        seen = set()
        for line, raw in enumerate(reader, 2):
            if any(not (raw.get(k) or '').strip() for k in FIELDS):
                raise ValueError(f'Line {line}: missing required value')
            item = {k:(raw[k] or '').strip() for k in FIELDS}
            if item['check_id'] in seen:
                raise ValueError(f'Line {line}: duplicate check_id')
            seen.add(item['check_id'])
            try:
                date.fromisoformat(item['month']+'-01')
            except ValueError as exc:
                raise ValueError(f'Line {line}: invalid YYYY-MM month') from exc
            if len(item['month']) != 7:
                raise ValueError(f'Line {line}: month must be YYYY-MM')
            for key in ('has_finding','is_followup','repeated_finding'):
                item[key] = parse_bool(item[key], line)
            if item['repeated_finding'] and not (item['has_finding'] and item['is_followup']):
                raise ValueError(f'Line {line}: repeated finding requires finding and follow-up')
            checks.append(item)
    return checks


def summarize(checks):
    grouped=defaultdict(list)
    for row in checks:
        grouped[row['month']].append(row)
    result=[]
    for month in sorted(grouped):
        rows=grouped[month]
        total=len(rows)
        findings=sum(row['has_finding'] for row in rows)
        followups=sum(row['is_followup'] for row in rows)
        repeat=sum(row['repeated_finding'] for row in rows)
        result.append({'month':month, 'checks':total, 'checks_with_findings':findings,
                       'finding_rate':round(findings/total*100,1), 'followups':followups,
                       'repeated_findings':repeat, 'repeat_rate':round(repeat/followups*100,1) if followups else None})
    return result


def build_report(summary):
    all_checks=sum(r['checks'] for r in summary)
    all_findings=sum(r['checks_with_findings'] for r in summary)
    rate=(100*all_findings/all_checks) if all_checks else 0
    cards=[]
    for r in summary:
        rep='N/A' if r['repeat_rate'] is None else f'{r["repeat_rate"]:.1f}%'
        cards.append('<tr><td><b>'+escape(r['month'])+'</b></td><td>'+str(r['checks'])+'</td><td>'+str(r['checks_with_findings'])+'</td><td>'+f'{r["finding_rate"]:.1f}%'+
            '<div class="bar"><span style="width:'+str(r['finding_rate'])+'%"></span></div></td><td>'+str(r['followups'])+'</td><td>'+str(r['repeated_findings'])+'</td><td>'+rep+'</td></tr>')
    return """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Quality Review Demo</title><style>body{font:15px system-ui,Arial;color:#203048;background:#f3f6fa;max-width:1000px;margin:36px auto;padding:0 18px}
h1{margin:8px 0}p{color:#5a6c83}.pill{font-size:12px;display:inline-block;padding:7px 11px;background:#e2ebf2;border-radius:30px}
.row{display:flex;gap:12px;margin:24px 0}.stat{flex:1;background:white;padding:17px;border-radius:12px;border:1px solid #d9e3ec}.stat b{display:block;font-size:29px}.stat small{color:#607189}
table{width:100%;border-collapse:collapse;background:white}th{text-align:left;background:#e5ebf2}th,td{padding:13px 9px;border-bottom:1px solid #dce3eb}.bar{background:#edf0f4;height:7px;border-radius:30px;margin-top:5px;width:100px}.bar span{background:#4c83a9;display:block;height:100%;border-radius:30px}
.note{font-size:12px;line-height:1.6;margin:22px 0}@media(max-width:650px){.row{flex-direction:column}table{font-size:11px}th,td{padding:8px 4px}.bar{width:54px}}</style></head><body>
<span class="pill">SYNTHETIC DEMO</span><h1>Quality Review</h1><p>Monthly inspection summary using invented community-facility checks.</p>
<div class="row"><div class="stat"><small>Check records</small><b>"""+str(all_checks)+"""</b></div><div class="stat"><small>Checks with findings</small><b>"""+str(all_findings)+"""</b></div>
<div class="stat"><small>Overall finding rate</small><b>"""+f'{rate:.1f}%'+"""</b></div></div>
<table><thead><tr><th>Month</th><th>Checks</th><th>Findings</th><th>Finding rate</th><th>Follow-ups</th><th>Repeats</th><th>Repeat rate</th></tr></thead>
<tbody>"""+''.join(cards)+"""</tbody></table><p class="note">Finding rate uses all checks as denominator. Repeat rate uses follow-up checks as denominator; N/A is displayed if there are no follow-ups. Observations are synthetic and do not imply causal improvements.</p></body></html>"""


def export_summary(path, rows):
    columns=('month','checks','checks_with_findings','finding_rate','followups','repeated_findings','repeat_rate')
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=columns)
        writer.writeheader();writer.writerows(rows)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',default='sample_data/checks.csv',type=Path)
    p.add_argument('--output',default='output/report.html',type=Path)
    p.add_argument('--summary',default='output/summary.csv',type=Path)
    a=p.parse_args()
    checks=read_checks(a.input)
    rows=summarize(checks)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(build_report(rows),encoding='utf-8')
    export_summary(a.summary,rows)
    print(f'Created {a.output} and {a.summary} from {len(checks)} invented checks')


if __name__=='__main__':main()
