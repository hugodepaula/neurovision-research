"""Contract and privacy tests use synthetic responses exclusively."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('usability',Path(__file__).parents[1]/'scripts/analyze_usability.py')
u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)

def row(i=1, tr=None, f='Fácil', text='N/A'):
    return {'submission_id':i,'submitted_at':'2026-03-01T12:00:00', 'answers':[
        {'caption':'TR1','selected_option_texts':[u.CORRECT if tr is None else tr], 'score':0},
        {'caption':'F1','selected_option_texts':[f], 'score':999},
        {'caption':'F2','text_response':text},
        {'caption':'QS2','text_response':'02/03/2000'},
        {'caption':'QS8','selected_option_texts':['Pós-graduação']},
        {'caption':'Q1','text_response':'SECRET_CLINICAL_VALUE'},
        {'caption':'QS1','text_response':'SECRET_NAME'},
    ]}
def run(rows, review=None):return u.analyze({'data':{'submissions':rows}},review)

class UsabilityTests(unittest.TestCase):
    def test_filter_uses_text_not_historical_score(self):
        s=run([row(1),row(2,tr='Perturbador')]);self.assertEqual(s['eligible'],1)
        self.assertEqual(sum(s['exclusions'].values()),1)
    def test_duplicate_tr1_and_multiselection_exclude(self):
        a=row();a['answers'].append(a['answers'][0].copy())
        b=row(2);b['answers'][0]['selected_option_texts'].append('Perturbador')
        self.assertEqual(run([a,b])['eligible'],0)
    def test_refusal_is_not_midpoint(self):
        s=run([row(1,f='Difícil'),row(2,f='Prefiro não responder'),row(3,f='Fácil')])
        self.assertEqual(s['difficulty']['denominator'],2);self.assertEqual(s['difficulty']['proportion'],.5)
    def test_age_at_birthday_and_invalid_dates(self):
        self.assertEqual(u.age_at('02/03/2000','2026-03-01')[0],25)
        self.assertEqual(u.age_at('02/03/2000','2026-03-02')[0],26)
        self.assertIsNone(u.age_at('31/02/2000','2026-03-02')[0])
        self.assertIsNone(u.age_at('02/03/2030','2026-03-02')[0])
    def test_wilson_boundary_and_empty(self):
        self.assertIsNone(u.wilson(0,0));lo,hi=u.wilson(0,10)
        self.assertAlmostEqual(lo,0);self.assertAlmostEqual(hi,.27753279986)
    def test_placeholders_are_not_comments(self):
        self.assertEqual(u.f2_status(' N/A '),'marcador_na')
        self.assertEqual(u.f2_status(''),'ausente')
        self.assertEqual(u.f2_status('Nenhuma'),'sem_observacao_explicita')
    def test_private_text_cannot_reach_aggregate(self):
        import json
        s=run([row(text='SECRET_FREE_TEXT')],{'labels_by_submission_id':{},'method':'SECRET_REVIEW'})
        output=json.dumps(s)+u.render(s)
        self.assertNotIn('SECRET',output);self.assertNotIn('submission_id',json.dumps(s))
    def test_review_labels_and_eligibility_validated(self):
        with self.assertRaises(ValueError):run([row(tr='Perturbador')],{'labels_by_submission_id':{'1':['clareza_linguagem']}})
        with self.assertRaises(ValueError):run([row(text='Comentário sintético')],{'labels_by_submission_id':{'1':['unknown']}})
    def test_duplicate_submission_id_fails(self):
        with self.assertRaises(ValueError):run([row(),row()])
    def test_git_checkout_private_input_refused(self):
        with self.assertRaises(ValueError):u.private_file(Path(__file__))
    def test_multiple_themes_count_once_per_comment(self):
        s=run([row(text='Comentário sintético')],{'labels_by_submission_id':{'1':['clareza_linguagem','navegacao']}})
        self.assertEqual(s['f2']['comments_tagged'],1)
        self.assertEqual(sum(s['f2']['themes'].values()),2)

class PublicationTests(unittest.TestCase):
    def test_detector_rejects_private_text_and_response_exports(self):
        import sys,json
        sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
        from verify_usability_publication import verify
        with tempfile.TemporaryDirectory() as directory:
            d=Path(directory); private=d/'input.json';public=d/'report.md'
            private.write_text(json.dumps({'data':{'submissions':[{'answers':[{'caption':'QS3','text_response':'synthetic@example.invalid'}]}]}}))
            public.write_text('synthetic@example.invalid')
            with self.assertRaises(ValueError):verify(private,[public])
            public.write_text(json.dumps(dict(submissions=[])))
            with self.assertRaises(ValueError):verify(private,[public])
    def test_detector_allows_aggregates(self):
        import sys,json
        sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
        from verify_usability_publication import verify
        with tempfile.TemporaryDirectory() as directory:
            d=Path(directory);private=d/'input.json';public=d/'report.json'
            private.write_text(json.dumps({'data':{'submissions':[{'answers':[{'caption':'F2','text_response':'PRIVATE '*20}]}]}}))
            public.write_text('{"eligible": 10, "difficulty": 2}')
            self.assertEqual(verify(private,[public]),1)
