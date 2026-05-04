import io
from pathlib import Path

# ctypes.CDLL(r"C:\Program Files\GTK3-Runtime Win64\bin\libcairo-2.dll")  # just in case
import cairosvg
from PIL import Image
from lxml import etree
import svgelements as se

_SVG_NS = {'svg': 'http://www.w3.org/2000/svg'}


def parse(svg_path: Path):
    return etree.parse(svg_path)


def fix_ukraine_colors(tree) -> None:
    """ДСТУ 4512:2006"""
    color_group = tree.find('.//svg:g[@id="color"]', _SVG_NS)
    if color_group is None:
        raise RuntimeError("Color group not found.")

    children = list(color_group)
    if len(children) < 2:
        raise RuntimeError("Expected at least 2 color elements.")

    children.sort(key=lambda el: float(el.get('y', 0)))

    children[0].set('fill', '#0057B8')
    children[1].set('fill', '#FFD700')


def remove_border_line(tree) -> None:
    line = tree.find('.//svg:g[@id="line"]', _SVG_NS)
    if line is not None:
        line.getparent().remove(line)


def render(tree, size: int) -> bytes:
    root = tree.getroot()

    svg = se.SVG.parse(io.StringIO(etree.tostring(root).decode()))
    x, y, w, h = svg.bbox(with_stroke=True)
    width, height = w - x, h - y

    root.set("viewBox", f"{x} {y} {width} {height}")

    root.set("width", str(size))
    root.set("height", str(size))

    return cairosvg.svg2png(bytestring=etree.tostring(root))


if __name__ == '__main__':
    _size: int = 64
    _country_code: str = (
        "UA"
        # "US"
        # "NP"
    )

    # ----------------

    _project_root: Path = Path(__file__).parent.parent
    _flag_path: Path = _project_root / f"build/flags/{_country_code}.svg"

    # ----------------

    _tree = etree.parse(_flag_path)

    remove_border_line(_tree)
    if _country_code == "UA":
        fix_ukraine_colors(_tree)

    _png: bytes = render(_tree, _size)

    Image.open(io.BytesIO(_png)).show()
