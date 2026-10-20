import csv
import json
from pathlib import Path
import pytest
from healthcare_generator.generate import prepare, validate_output
from healthcare_generator.setup import SetupError, OFFICIAL_REPO

@pytest.fixture
def cfg(tmp_path):
    p = tmp_path/'config'/'generator.yaml'
    p.parent.mkdir()
    p.write_text(f'synthea:\n  install_dir: ./external/synthea\n  source_repo: {OFFICIAL_REPO}\n  version: v4.0.0\n')
    return p

@pytest.mark.parametrize('format', ['csv','fhir','ccda'])
def test_prepare(cfg, format):
    d = prepare(cfg,format,10,'Massachusetts',12)
    assert d['format']==format and d['patients']==10
    assert d['output_dir'].parent.name == format

@pytest.mark.parametrize('count',[10,1000,100000,1000000,42])
def test_counts(cfg,count):
    assert prepare(cfg,'csv',count,'New Jersey',None)['patients']==count

@pytest.mark.parametrize('count',[0,-1,1000001])
def test_bad_counts(cfg,count):
    with pytest.raises(SetupError):prepare(cfg,'csv',count,'Massachusetts',None)

def test_csv_validation(tmp_path):
    f=tmp_path/'csv'/'patients.csv';f.parent.mkdir()
    f.write_text('Id,FIRST\na,Alex\nb,Taylor\n')
    assert validate_output(tmp_path,'csv')['patient_rows']==2

def test_fhir_validation(tmp_path):
    f=tmp_path/'fhir'/'record.json';f.parent.mkdir()
    f.write_text(json.dumps({'resourceType':'Bundle','entry':[]}))
    assert validate_output(tmp_path,'fhir')['files']==1

def test_ccda_validation(tmp_path):
    f=tmp_path/'ccda'/'record.xml';f.parent.mkdir()
    f.write_text('<ClinicalDocument/>')
    assert validate_output(tmp_path,'ccda')['files']==1
