"""Regression fixtures for known Synthea exporter shapes.

These are representative structural fixtures, not upstream conformance fixtures.
"""
import json

from healthcare_generator.validation import validate_output


def test_csv_includes_deceased_beyond_living_target(tmp_path):
    folder = tmp_path / 'csv'
    folder.mkdir()
    (folder / 'patients.csv').write_text(
        'Id,FIRST,DEATHDATE\np1,Alice,\np2,Bob,\np3,Carol,2019-01-01\n',
        encoding='utf-8',
    )
    (folder / 'encounters.csv').write_text('Id,PATIENT\ne1,p1\n', encoding='utf-8')
    result = validate_output(tmp_path, 'csv', expected_living=2)
    assert result['patient_rows'] == 3
    assert result['living_patient_rows'] == 2
    assert result['files'] == 2


def test_fhir_supplementary_organization_and_practitioner_files(tmp_path):
    folder = tmp_path / 'fhir'
    folder.mkdir()
    patient_bundle = {
        'resourceType': 'Bundle', 'type': 'collection',
        'entry': [{'resource': {'resourceType': 'Patient', 'id': 'p1'}}],
    }
    (folder / 'patient-1.json').write_text(json.dumps(patient_bundle), encoding='utf-8')
    (folder / 'hospitalInformation.json').write_text(
        json.dumps({'resourceType': 'Bundle', 'type': 'collection',
                    'entry': [{'resource': {'resourceType': 'Organization', 'id': 'o1'}}]}),
        encoding='utf-8',
    )
    (folder / 'practitionerInformation.json').write_text(
        json.dumps({'resourceType': 'Bundle', 'type': 'collection',
                    'entry': [{'resource': {'resourceType': 'Practitioner', 'id': 'd1'}}]}),
        encoding='utf-8',
    )
    result = validate_output(tmp_path, 'fhir', expected_living=1)
    assert result['files'] == 3
    assert result['patient_resources'] == 1


def test_ccda_clinical_document_with_namespace(tmp_path):
    folder = tmp_path / 'ccda'
    folder.mkdir()
    (folder / 'patient.xml').write_text(
        '<ClinicalDocument xmlns="urn:hl7-org:v3"><id root="p1"/></ClinicalDocument>',
        encoding='utf-8',
    )
    assert validate_output(tmp_path, 'ccda', expected_living=1)['files'] == 1
