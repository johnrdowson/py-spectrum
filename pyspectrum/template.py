import os
import re
from jinja2 import FileSystemLoader, Environment

PATH = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_ENV = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, "templates")),
    trim_blocks=False,
)


TEMPLATE_FILES = {"model_search": "model_search.j2"}


def _render_template(template_file, context):
    """ Helper function to return the correct Jinja2 temaplate file """
    return TEMPLATE_ENV.get_template(template_file).render(context)


def model_search_xml(**params):
    """
    Uses Jinja2 to render the Spectrum Model Search XML payload using the
    supplied arguments.
    """
    xml_string = _render_template(TEMPLATE_FILES["model_search"], params)
    return re.sub(r"^$\n", "", xml_string, flags=re.MULTILINE)
