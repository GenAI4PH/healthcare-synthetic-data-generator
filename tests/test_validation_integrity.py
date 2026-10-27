import json
import pytest
from healthcare_generator.validation import validate_output
from healthcare_generator.setup import SetupError


def test_short_living_csv_rejected(tmp_path):
    folder = tmp_path / 'csv'; folder.mkdir()
    (folder / 'patients.csv').write_text('Id,DEATHDATE\na,\nb,2020-01-01\n')
    with pytest.raises(SetupError, match='only 1 living'):
        validate_output(tmp_path, 'csv', expected_living=2)


def test_total_rows_can_exceed_living_target(tmp_path):
    folder = tmp_path / 'csv'; folder.mkdir()
    (folder / 'patients.csv').write_text('Id,DEATHDATE\na,\nb,2020-01-01\n')
    stats = validate_output(tmp_path, 'csv', expected_living=1)
    assert stats['patient_rows'] == 2 and stats['living_patient_rows'] == 1


def test_duplicate_patient_id_rejected(tmp_path):
    folder = tmp_path / 'csv'; folder.mkdir()
    (folder / 'patients.csv').write_text('Id,DEATHDATE\na,\na,\n')
    with pytest.raises(SetupError, match='duplicate'):
        validate_output(tmp_path, 'csv', expected_living=1)


def test_corrupt_second_fhir_rejected(tmp_path):
    folder = tmp_path / 'fhir'; folder.mkdir()
    payload = {'resourceType':'Bundle', 'entry':[{'resource':{'resourceType':'Patient','id':'p1'}}]}
    (folder / 'a.json').write_text(json.dumps(payload))
    (folder / 'b.json').write_text('{invalid')
    with pytest.raises(SetupError, match='b.json'):
        validate_output(tmp_path, 'fhir', expected_living=1)


def test_short_fhir_rejected(tmp_path):
    folder = tmp_path / 'fhir'; folder.mkdir()
    payload = {'resourceType':'Bundle', 'entry':[{'resource':{'resourceType':'Patient','id':'p1'}}]}
    (folder / 'a.json').write_text(json.dumps(payload))
    with pytest.raises(SetupError, match='only 1 Patient'):
        validate_output(tmp_path, 'fhir', expected_living=2)


def test_invalid_second_ccda_rejected(tmp_path):
    folder = tmp_path / 'ccda'; folder.mkdir()
    (folder / 'a.xml').write_text('<ClinicalDocument/>')
    (folder / 'b.xml').write_text('<NotAClinicalDocument/>')
    with pytest.raises(SetupError, match='b.xml'):
        validate_output(tmp_path, 'ccda', expected_living=1)


def test_short_ccda_rejected(tmp_path):
    folder = tmp_path / 'ccda'; folder.mkdir()
    (folder / 'a.xml').write_text('<ClinicalDocument/>')
    with pytest.raises(SetupError, match='only 1 C-CDA'):
        validate_output(tmp_path, 'ccda', expected_living=2)
