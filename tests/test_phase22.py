from pathlib import Path
import pytest
from healthcare_generator.setup import SetupError, java_runtime_major, windows_path_warning
from unittest.mock import patch

@pytest.mark.parametrize('text,expected', [
    ('openjdk version "17.0.12" 2024-07-16',17),
    ('java version "1.8.0_401"',8),
    ('openjdk version "26" 2026-03-17',26),
])
def test_java_version_parsing(text, expected):
    assert java_runtime_major(text) == expected

def test_windows_long_path_warning():
    with patch('healthcare_generator.setup.platform.system', return_value='Windows'):
        assert windows_path_warning(Path('C:/') / ('very-long-directory-'*6)) is not None

def test_non_windows_no_warning():
    with patch('healthcare_generator.setup.platform.system', return_value='Linux'):
        assert windows_path_warning(Path('/some/very/long/directory')) is None
