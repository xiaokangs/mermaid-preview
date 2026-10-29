"""Unit tests for preprocess() in index.html, executed inside the real page."""

import pytest

BS_N = "\\n"  # literal backslash + n, as pasted from LLM output

CASES = [
    # literal \n in box labels -> <br/>
    (f"A[Line1{BS_N}Line2]", "A[Line1<br/>Line2]"),
    (f'A["Line1{BS_N}Line2"]', 'A["Line1<br/>Line2"]'),
    # two \n in one label both converted
    (f"A[a{BS_N}b{BS_N}c]", "A[a<br/>b<br/>c]"),
    # diamond labels with parens get quoted
    ("B{Is it ok (yes)?}", 'B{"Is it ok (yes)?"}'),
    # box labels with parens get quoted
    ("C[Call API (v2)]", 'C["Call API (v2)"]'),
    # \n fix + paren quoting combined
    (f"A[foo{BS_N}(bar)]", 'A["foo<br/>(bar)"]'),
    # already-quoted labels untouched
    ('B{"Check (x)"}', 'B{"Check (x)"}'),
    ('C["Call (v2)"]', 'C["Call (v2)"]'),
    # labels without parens untouched
    ("B{Is it working?}", "B{Is it working?}"),
    ("C[Great!]", "C[Great!]"),
    # stadium node shape untouched
    ("A([Start]) --> F([End])", "A([Start]) --> F([End])"),
    # subroutine [[...]] with parens untouched
    ("A[[Sub (x)]]", "A[[Sub (x)]]"),
    # plain edges / empty
    ("A --> B", "A --> B"),
    ("", ""),
    # mixed-language label with parens
    ("N[检查（cache）(hit)]", 'N["检查（cache）(hit)"]'),
]


@pytest.mark.parametrize("src,expected", CASES)
def test_preprocess(app, src, expected):
    assert app.evaluate("code => preprocess(code)", src) == expected


def test_preprocess_multiline_diagram(app):
    src = "\n".join([
        "flowchart TD",
        f"    A[Load data{BS_N}from disk] --> B{{Valid (schema)?}}",
        "    B -- Yes --> C[Save (db)]",
        "    B -- No --> D([Stop])",
    ])
    out = app.evaluate("code => preprocess(code)", src)
    assert out.splitlines() == [
        "flowchart TD",
        "    A[Load data<br/>from disk] --> B{\"Valid (schema)?\"}",
        "    B -- Yes --> C[\"Save (db)\"]",
        "    B -- No --> D([Stop])",
    ]


def test_preprocess_default_example_is_identity(app):
    code = app.evaluate("() => document.getElementById('editor').value.trim()")
    assert app.evaluate("code => preprocess(code)", code) == code
