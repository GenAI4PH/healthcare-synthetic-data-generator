"""Fail-closed structural checks for generated Synthea patient exports.

This is not a complete FHIR/C-CDA conformance or referential-integrity validator.
"""
from __future__ import annotations

import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from .setup import SetupError


def _fail(path: Path, detail: str) -> None:
    raise SetupError(f"Invalid generated output {path}: {detail}")


def validate_output(out_dir: Path, fmt: str, expected_living: int | None = None) -> dict:
    """Validate every patient export, with minimum living population where measurable.

    When expected_living is omitted, preserve the public compatibility API used
    in existing unit tests. All production generation paths must pass it.
    """
    folder = out_dir / fmt
    if not folder.is_dir():
        _fail(folder, 'export directory not found')
    if expected_living is not None and expected_living < 1:
        raise SetupError('Expected living patient count must be positive')

    if fmt == 'csv':
        paths = sorted(folder.glob('*.csv'))
        patient_file = folder / 'patients.csv'
        if not patient_file.is_file():
            _fail(patient_file, 'patients.csv missing')
        # Validate all CSV files for parseability, column count and headers.
        patient_rows = 0
        living = 0
        seen = set()
        for path in paths:
            try:
                with path.open(encoding='utf-8-sig', newline='') as handle:
                    reader = csv.reader(handle, strict=True)
                    header = next(reader, None)
                    if not header or any(not h.strip() for h in header) or len(set(header)) != len(header):
                        _fail(path, 'missing, blank or duplicate header names')
                    if path == patient_file and 'Id' not in header:
                        _fail(path, 'patient Id column missing')
                    if path == patient_file and expected_living is not None and 'DEATHDATE' not in header:
                        _fail(path, 'DEATHDATE column required to verify living population')
                    for number, row in enumerate(reader, start=2):
                        if len(row) != len(header):
                            _fail(path, f'column mismatch at row {number}')
                        if path == patient_file:
                            identity = row[header.index('Id')].strip()
                            if not identity or identity in seen:
                                _fail(path, f'blank or duplicate patient Id at row {number}')
                            seen.add(identity)
                            patient_rows += 1
                            if 'DEATHDATE' in header and not row[header.index('DEATHDATE')].strip():
                                living += 1
            except (UnicodeError, csv.Error, OSError) as exc:
                _fail(path, str(exc))
        if patient_rows == 0:
            _fail(patient_file, 'no patient rows')
        if expected_living is not None and living < expected_living:
            _fail(patient_file, f'only {living} living patients for requested {expected_living}')
        return {'patient_rows': patient_rows, 'living_patient_rows': living, 'files': len(paths)}

    if fmt == 'fhir':
        paths = sorted(folder.glob('*.json'))
        if not paths:
            _fail(folder, 'FHIR JSON files missing')
        patient_bundles = 0
        for path in paths:
            try:
                document = json.loads(path.read_text(encoding='utf-8-sig'))
            except (ValueError, UnicodeError, OSError) as exc:
                _fail(path, str(exc))
            if not isinstance(document, dict) or not isinstance(document.get('resourceType'), str):
                _fail(path, 'resourceType missing or invalid')
            if document['resourceType'] == 'Bundle':
                entries = document.get('entry', [])
                if not isinstance(entries, list):
                    _fail(path, 'Bundle.entry must be a list')
                patient_count = 0
                for i, entry in enumerate(entries):
                    if not isinstance(entry, dict) or not isinstance(entry.get('resource'), dict):
                        _fail(path, f'invalid Bundle.entry[{i}].resource')
                    resource = entry['resource']
                    if not isinstance(resource.get('resourceType'), str):
                        _fail(path, f'missing resourceType in Bundle.entry[{i}]')
                    if resource['resourceType'] == 'Patient':
                        if not resource.get('id'):
                            _fail(path, f'Patient in Bundle.entry[{i}] lacks id')
                        patient_count += 1
                if patient_count:
                    patient_bundles += patient_count
                elif expected_living is not None:
                    # Synthea includes supplementary organization/provider bundles.
                    # These can lack Patient resources; they still must be valid bundles.
                    if not entries:
                        _fail(path, 'empty Bundle in patient export')
        if expected_living is not None and patient_bundles < expected_living:
            _fail(folder, f'only {patient_bundles} Patient resources for requested {expected_living} living patients')
        return {'files': len(paths), 'patient_resources': patient_bundles}

    if fmt == 'ccda':
        paths = sorted(folder.glob('*.xml'))
        if not paths:
            _fail(folder, 'C-CDA XML files missing')
        for path in paths:
            try:
                root = ET.parse(path).getroot()
            except (ET.ParseError, UnicodeError, OSError) as exc:
                _fail(path, str(exc))
            if root.tag.rsplit('}', 1)[-1] != 'ClinicalDocument':
                _fail(path, 'expected ClinicalDocument root element')
        if expected_living is not None and len(paths) < expected_living:
            _fail(folder, f'only {len(paths)} C-CDA documents for requested {expected_living} living patients')
        return {'files': len(paths)}

    raise SetupError(f'Unsupported format: {fmt}')
