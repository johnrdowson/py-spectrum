import os
import re
from datetime import datetime
from datetime import timedelta
from typing import Optional, List, Union
from jinja2 import FileSystemLoader, Environment

PATH = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_ENV = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, "templates")),
    trim_blocks=False,
)


TEMPLATE_FILES = {
    "model_search": "model_search.j2",
    "event_search": "event_search.j2",
}


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


def event_search_xml(
    model_handle: int,
    start_time: datetime,
    end_time: datetime,
    req_attrs: List[str],
    throttle_size: Optional[int] = 100,
    **params,
):
    """
    Uses Jinja2 to render the Spectrum Event Search XML payload using the
    supplied arguments.
    """

    params["model_handle"] = hex(model_handle)
    params["throttle_size"] = throttle_size
    params["start_time"] = int(start_time.timestamp()) * 1000
    params["end_time"] = int(end_time.timestamp()) * 1000
    params["req_attrs"] = req_attrs

    xml_string = _render_template(TEMPLATE_FILES["event_search"], params)
    return re.sub(r"^$\n", "", xml_string, flags=re.MULTILINE)
