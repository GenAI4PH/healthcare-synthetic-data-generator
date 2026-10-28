import json
import pytest
from pathlib import Path
from healthcare_generator.run_integrity import run_lock, inventory, check_csv_relationships
from healthcare_generator.setup import SetupError

def test_lock_prevents_concurrent_run(tmp_path):
    with run_lock(tmp_path):
        with pytest.raises(SetupError, match='locked'):
            with run_lock(tmp_path):
                pass
    assert not (tmp_path / '.hsg-run.lock').exists()

def test_stale_lock_requires_inspection(tmp_path):
    (tmp_path / '.hsg-run.lock').write_text('{"pid":999999}')
    with pytest.raises(SetupError, match='locked'):
        with run_lock(tmp_path):
            pass
    assert (tmp_path / '.hsg-run.lock').exists()

def test_inventory_sha(tmp_path):
    (tmp_path/'patients.csv').write_text('Id\na\n')
    result=inventory(tmp_path)
    assert result['file_count']==1 and len(result['files'][0]['sha256'])==64

def test_csv_orphan_fails(tmp_path):
    (tmp_path/'patients.csv').write_text('Id\np1\n')
    (tmp_path/'encounters.csv').write_text('Id,PATIENT\ne1,p2\n')
    with pytest.raises(SetupError,match='Unknown PATIENT'):
        check_csv_relationships(tmp_path)

def test_csv_valid(tmp_path):
    (tmp_path/'patients.csv').write_text('Id\np1\n')
    (tmp_path/'encounters.csv').write_text('Id,PATIENT\ne1,p1\n')
    (tmp_path/'conditions.csv').write_text('PATIENT,ENCOUNTER\np1,e1\n')
    assert check_csv_relationships(tmp_path)['related_rows_checked']==1
