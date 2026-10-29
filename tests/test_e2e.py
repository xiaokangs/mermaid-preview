"""End-to-end tests: the real index.html in headless Chromium with a fake Mermaid."""

from playwright.sync_api import expect


def calls(page):
    return page.evaluate("() => window.__mermaid.calls.length")


def last_code(page):
    return page.evaluate("() => window.__mermaid.calls[window.__mermaid.calls.length - 1].code")


def wait_status(page, text):
    expect(page.locator("#status")).to_have_text(text)


# ---------- initial load ----------

def test_initial_render(app):
    expect(app).to_have_title("Mermaid Flowchart Preview")
    expect(app.locator("header h1")).to_have_text("Mermaid Preview")
    expect(app.locator("#status")).to_have_text("Rendered OK")
    expect(app.locator("#status")).to_have_class("status ok")
    expect(app.locator("#diagram svg")).to_be_visible()
    expect(app.locator("#diagram svg")).to_contain_text("Is it working?")
    expect(app.locator("#error-box")).to_be_hidden()
    default = app.evaluate("() => document.getElementById('editor').value.trim()")
    assert last_code(app) == default


def test_mermaid_config(app):
    cfg = app.evaluate("() => window.__mermaid.initConfig")
    assert cfg["startOnLoad"] is False
    assert cfg["theme"] == "base"
    assert cfg["themeVariables"]["primaryColor"] == "#0071e3"
    assert cfg["themeVariables"]["edgeLabelBackground"] == "#ffffff"
    flow = cfg.get("flowchart") or {}
    assert flow.get("htmlLabels") is not True


def test_layout_css_invariants(app):
    overflow = app.evaluate(
        "() => getComputedStyle(document.getElementById('preview-container')).overflow")
    assert overflow == "hidden"
    # edge label text forced dark
    color = app.evaluate("""() => {
        const g = document.createElement('div');
        g.className = 'edgeLabel';
        const s = document.createElement('span');
        s.textContent = 'Yes';
        g.appendChild(s);
        document.getElementById('diagram').appendChild(g);
        const c = getComputedStyle(s).color;
        g.remove();
        return c;
    }""")
    assert color == "rgb(29, 29, 31)"
    # header title is white on dark header
    assert app.evaluate("() => getComputedStyle(document.querySelector('header h1')).color") \
        == "rgb(255, 255, 255)"


# ---------- editing / rendering ----------

def test_typing_renders_preprocessed_code(app):
    app.fill("#editor", "flowchart TD\n  A{Check (x)} --> B[Run (fast)]\n")
    app.wait_for_function("() => window.__mermaid.calls.length >= 2")
    wait_status(app, "Rendered OK")
    assert last_code(app) == 'flowchart TD\n  A{"Check (x)"} --> B["Run (fast)"]'
    expect(app.locator("#diagram svg")).to_contain_text('A{"Check (x)"}')


def test_debounce_coalesces_rapid_input(app):
    before = calls(app)
    app.locator("#editor").fill("")
    app.locator("#editor").press_sequentially("graph LR\nX-->Y", delay=10)
    app.wait_for_function(f"() => window.__mermaid.calls.length > {before}")
    app.wait_for_timeout(600)
    assert calls(app) == before + 1
    assert last_code(app) == "graph LR\nX-->Y"


def test_parse_error_then_recovery(app):
    app.fill("#editor", "flowchart TD\n  INVALID ->> ???")
    wait_status(app, "Parse error")
    expect(app.locator("#status")).to_have_class("status err")
    expect(app.locator("#error-box")).to_be_visible()
    expect(app.locator("#error-box")).to_have_text("Parse error on line 2: INVALID token")
    expect(app.locator("#diagram")).to_be_hidden()

    app.fill("#editor", "flowchart TD\n  A --> B")
    wait_status(app, "Rendered OK")
    expect(app.locator("#error-box")).to_be_hidden()
    expect(app.locator("#error-box")).to_have_text("")
    expect(app.locator("#diagram svg")).to_be_visible()
    expect(app.locator("#diagram svg")).to_contain_text("A --> B")


def test_non_error_throw_shown_as_string(app):
    app.fill("#editor", "flowchart TD\n  THROWSTRING")
    wait_status(app, "Parse error")
    expect(app.locator("#error-box")).to_have_text("bare string failure")


def test_blank_input_does_not_render(app):
    before = calls(app)
    app.fill("#editor", "   \n\t  ")
    app.wait_for_timeout(700)
    assert calls(app) == before
    # previous diagram stays
    expect(app.locator("#status")).to_have_text("Rendered OK")
    expect(app.locator("#diagram svg")).to_be_visible()


# ---------- zoom / pan / reset ----------

def _center(page):
    box = page.locator("#preview-container").bounding_box()
    assert box
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def test_wheel_zoom_in_and_out(app):
    cx, cy = _center(app)
    app.mouse.move(cx, cy)
    app.mouse.wheel(0, -100)
    app.wait_for_function("() => Math.abs(scale - 1.1) < 1e-9")
    assert "scale(1.1)" in app.evaluate("() => document.getElementById('diagram').style.transform")
    app.mouse.wheel(0, 100)
    app.wait_for_function("() => Math.abs(scale - 1.0) < 1e-9")


def test_zoom_clamped_to_min(app):
    cx, cy = _center(app)
    app.mouse.move(cx, cy)
    for _ in range(15):
        app.mouse.wheel(0, 100)
    app.wait_for_function("() => Math.abs(scale - 0.2) < 1e-9")
    app.wait_for_timeout(100)
    assert abs(app.evaluate("() => scale") - 0.2) < 1e-9


def test_zoom_clamped_to_max_30(app):
    app.evaluate("() => { scale = 29.95; }")
    cx, cy = _center(app)
    app.mouse.move(cx, cy)
    app.mouse.wheel(0, -100)
    app.wait_for_function("() => scale === 30")
    app.mouse.wheel(0, -100)
    app.wait_for_timeout(150)
    assert app.evaluate("() => scale") == 30


def test_zoom_toward_cursor_shifts_translation(app):
    box = app.locator("#preview-container").bounding_box()
    assert box
    # point 100px right of center: tx = cx + ratio*(0 - cx) = -0.1 * 100
    app.mouse.move(box["x"] + box["width"] / 2 + 100, box["y"] + box["height"] / 2)
    app.mouse.wheel(0, -100)
    app.wait_for_function("() => Math.abs(scale - 1.1) < 1e-9")
    tx = app.evaluate("() => tx")
    assert abs(tx - (-10)) < 1.0


def test_drag_pans_diagram(app):
    cx, cy = _center(app)
    app.mouse.move(cx, cy)
    app.mouse.down()
    app.mouse.move(cx + 50, cy + 30, steps=3)
    app.mouse.up()
    tx, ty = app.evaluate("() => [tx, ty]")
    assert abs(tx - 50) < 0.01 and abs(ty - 30) < 0.01
    transform = app.evaluate("() => document.getElementById('diagram').style.transform")
    assert transform.startswith("translate(") and "scale(1)" in transform
    # moving after release does not pan
    app.mouse.move(cx + 200, cy + 200)
    assert app.evaluate("() => [tx, ty]") == [tx, ty]


def test_reset_view_button(app):
    cx, cy = _center(app)
    app.mouse.move(cx, cy)
    app.mouse.wheel(0, -100)
    app.wait_for_function("() => scale > 1")
    app.mouse.down()
    app.mouse.move(cx + 40, cy + 40)
    app.mouse.up()
    app.click("#reset-view-btn")
    assert app.evaluate("() => [scale, tx, ty]") == [1, 0, 0]
    assert app.evaluate("() => document.getElementById('diagram').style.transform") == ""


def test_new_render_resets_view(app):
    cx, cy = _center(app)
    app.mouse.move(cx, cy)
    app.mouse.down()
    app.mouse.move(cx + 60, cy + 10)
    app.mouse.up()
    assert abs(app.evaluate("() => tx") - 60) < 0.01
    before = calls(app)
    app.fill("#editor", "graph LR\n  P --> Q")
    app.wait_for_function(f"() => window.__mermaid.calls.length > {before}")
    app.wait_for_function("() => tx === 0 && ty === 0 && scale === 1")
    assert app.evaluate("() => document.getElementById('diagram').style.transform") == ""


# ---------- copy SVG ----------

def test_copy_svg(app):
    btn = app.locator("#copy-svg-btn")
    expect(btn).to_have_text("Copy SVG")
    btn.click()
    expect(btn).to_have_text("Copied!")
    copied = app.evaluate("() => window.__copied")
    assert copied.startswith("<svg")
    assert copied == app.evaluate("() => document.getElementById('diagram').innerHTML")
    expect(btn).to_have_text("Copy SVG", timeout=4000)


def test_copy_svg_noop_when_empty(app):
    app.evaluate("() => { document.getElementById('diagram').innerHTML = ''; }")
    app.click("#copy-svg-btn")
    app.wait_for_timeout(200)
    assert app.evaluate("() => window.__copied") is None
    expect(app.locator("#copy-svg-btn")).to_have_text("Copy SVG")
