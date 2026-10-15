import ast
import pathlib

from geometry import area, circle_area


def test_area_has_docstring_naming_params():
    doc = area.__doc__ or ""
    assert "width" in doc and "height" in doc, repr(doc)


def test_behaviour_unchanged():
    assert area(3, 4) == 12
    assert round(circle_area(1), 5) == 3.14159


def test_functions_unchanged():
    tree = ast.parse(pathlib.Path("geometry.py").read_text())
    names = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
    assert names == ["area", "circle_area"]
