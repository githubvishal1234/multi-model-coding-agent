from ferrule.cli import main


def test_missing_workspace_fails_before_calling_a_model(tmp_path, capsys):
    missing = tmp_path / "does-not-exist"
    assert main(["run", "do something", "--workspace", str(missing)]) == 2
    assert "does not exist" in capsys.readouterr().err
