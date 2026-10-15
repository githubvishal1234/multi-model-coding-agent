from wordcount import main


def test_counts_words(tmp_path, capsys):
    f = tmp_path / "t.txt"
    f.write_text("hello big world")
    main([str(f)])
    assert capsys.readouterr().out == "3 words\n"
