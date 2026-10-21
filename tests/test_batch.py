import csv
import json
from pathlib import Path
import pytest
from typer.testing import CliRunner
from healthcare_generator.batch import US_STATES, allocation, plan, merge_csv
from healthcare_generator.cli import app
from healthcare_generator.setup import SetupError

def test_states():
    assert len(US_STATES)==50 and len(set(US_STATES.values()))==50

def test_split_50():
    jobs=plan('csv',100,'NJ',False,'total',30)
    assert sum(x['patients'] for x in jobs)==100 and len(jobs)==4

def test_all_states_even():
    jobs=plan('fhir',100,None,True,'total',10)
    assert len(jobs)==50 and all(j['patients']==2 for j in jobs)

def test_per_state():
    jobs=plan('ccda',10,None,True,'per-state',10)
    assert len(jobs)==50 and sum(j['patients'] for j in jobs)==500

@pytest.mark.parametrize('patients,all_states,allocation_mode', [(49,True,'total'),(1000000,True,'per-state'),(0,False,'total')])
def test_invalid_request(patients,all_states,allocation_mode):
    with pytest.raises(SetupError):plan('csv',patients,None,all_states,allocation_mode)

def test_seed_guard():
    with pytest.raises(SetupError):plan('csv',10,'NJ',False,'total',10,-1)

def test_preview_is_no_side_effects():
    result=CliRunner().invoke(app,['generate-batch','csv','--patients','20','--batch-size','10','--state','NJ'])
    assert result.exit_code==0 and 'Preview only' in result.output

def test_merge_headers(tmp_path):
    root=tmp_path/'run'
    (root/'batches'/'a'/'csv').mkdir(parents=True)
    (root/'batches'/'b'/'csv').mkdir(parents=True)
    (root/'manifest.json').write_text(json.dumps({'schema_version':1,'format':'csv','status':'completed','batches':[{'id':'a'},{'id':'b'}]}))
    for ident in ['a','b']:
        (root/'batches'/ident/'csv'/'patients.csv').write_text(f'Id,FIRST\n{ident},Test\n')
    result=merge_csv(root)
    assert result['rows_by_file']['patients.csv']==2
    rows=list(csv.reader((root/'merged'/'csv'/'patients.csv').open()))
    assert rows==[['Id','FIRST'],['a','Test'],['b','Test']]

def test_merge_mismatch(tmp_path):
    root=tmp_path/'run'
    for id,header in [('a','Id'),('b','Wrong')]:
        target=root/'batches'/id/'csv';target.mkdir(parents=True)
        (target/'patients.csv').write_text(header+'\n1\n')
    (root/'manifest.json').write_text(json.dumps({'schema_version':1,'format':'csv','status':'completed','batches':[{'id':'a'},{'id':'b'}]}))
    with pytest.raises(SetupError,match='header mismatch'):
        merge_csv(root)
    assert not (root/'merged').exists()
