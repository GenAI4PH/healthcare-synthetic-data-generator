import json
from pathlib import Path
import pytest
from healthcare_generator.storage import plan, upload, _safe_prefix
from healthcare_generator.setup import SetupError

@pytest.fixture
def example(tmp_path):
    run = tmp_path/'output'/'runs'/'csv'/'run-001'
    folder = run/'csv'; folder.mkdir(parents=True)
    (run/'manifest.json').write_text(json.dumps({'status':'completed'}))
    (folder/'patients.csv').write_text('Id\nA\n')
    cfg = tmp_path/'config'/'storage.yaml';cfg.parent.mkdir()
    cfg.write_text('storage:\n  provider: local\n  local:\n    path: ./exports\n')
    return run,cfg

def test_local_preview_is_readonly(example):
    run,cfg=example
    item=plan(run,cfg)
    assert item['file_count']==2
    assert not (cfg.parent.parent/'exports').exists()

def test_approval_required(example):
    run,cfg=example
    with pytest.raises(SetupError,match='approve'):
        upload(run,cfg,None,False)

def test_local_copy_and_receipt(example):
    run,cfg=example
    result=upload(run,cfg,None,True)
    assert result['file_count']==2
    assert (cfg.parent.parent/'exports'/'csv'/'run-001'/'csv'/'patients.csv').exists()
    assert (run/'storage-receipt.json').exists()

def test_no_overwrite(example):
    run,cfg=example
    upload(run,cfg,None,True)
    with pytest.raises(SetupError): upload(run,cfg,None,True)

def test_not_completed(example):
    run,cfg=example
    (run/'manifest.json').write_text('{"status":"failed"}')
    with pytest.raises(SetupError,match='completed'):
        plan(run,cfg)

def test_traversal_rejected():
    with pytest.raises(SetupError): _safe_prefix('abc/../secret')

def test_symlinks_rejected(example):
    run,cfg=example
    try: (run/'link.csv').symlink_to(run/'csv'/'patients.csv')
    except (NotImplementedError, OSError): pytest.skip('Symlinks not supported')
    with pytest.raises(SetupError, match='Symlink'): plan(run,cfg)
