import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from quality import read_checks,summarize,build_report
ROOT=Path(__file__).resolve().parents[1]

class QualityTests(unittest.TestCase):
    def test_finding_denominator(self):
        rows=summarize(read_checks(ROOT/'sample_data/checks.csv'))
        self.assertEqual([r['month'] for r in rows],['2026-07','2026-08','2026-09','2026-10'])
        self.assertEqual(rows[0]['checks'],6)
        self.assertEqual(rows[0]['checks_with_findings'],3)
        self.assertEqual(rows[0]['finding_rate'],50.0)
        self.assertEqual(rows[0]['repeat_rate'],50.0)

    def test_empty_returns_empty(self):
        self.assertEqual(summarize([]),[])
        self.assertIn('0.0%',build_report([]))

    def test_no_followups_is_na(self):
        rows=summarize([{'month':'2026-09','has_finding':False,'is_followup':False,'repeated_finding':False}])
        self.assertIsNone(rows[0]['repeat_rate'])
        self.assertIn('N/A',build_report(rows))

    def test_inconsistent_repeat_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'bad.csv'
            p.write_text('check_id,month,area,has_finding,is_followup,repeated_finding\nD-1,2026-10,Example,false,false,true\n',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'requires finding'):
                read_checks(p)

    def test_duplicate_check_ids_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'bad.csv'
            header='check_id,month,area,has_finding,is_followup,repeated_finding\n'
            row='D-1,2026-10,Example,false,false,false\n'
            p.write_text(header+row+row,encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'duplicate check_id'):
                read_checks(p)

if __name__=='__main__':unittest.main()
