from pyspectrum.attributes import attr_id_to_name
from lxml import etree
from httpx import Response
from typing import List, Dict, Tuple
import re


__all__ = [
    "SpectrumLandscapeResponse",
    "SpectrumModelResponseList",
    "SpectrumAssociationResponseList",
]


def _camel_to_snake(name: str) -> str:
    """
    The XML elements in Spectrum's API are returned in camel case format. This
    function will convert them the PEP8 recommended format - lower-case with
    underscores (aka snake case).
    """
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def _strip_ns(root: etree.Element) -> etree.Element:
    """
    Removes all namespaces from an XML Element tree. This will make parsing the
    XML element much simpler.
    """

    for elem in root.getiterator():
        elem.tag = etree.QName(elem).localname

    etree.cleanup_namespaces(root)
    return root


class SpectrumXMLResponse:
    def __init__(self, response: Response):
        """
        Base response object which will check we have valid XML and will, by
        default, strip the XML namespaces to avoid issues with parsing
        """
        # Attempt to parse the response payload as XML
        try:
            root = etree.fromstring(response.content)
        except etree.XMLSyntaxError as err:
            raise ValueError(f"Unable to parse XML response\n\n{err}")

        # Store original HTTPX response object
        self.response = response

        # Strip namespaces from the XML payload
        self.xml = _strip_ns(root)

    def __repr__(self) -> str:
        """ Magic repr method for Response class """
        return f"Response <Success: {str(not self.response.is_error)}>"


class SpectrumLandscapeResponse(SpectrumXMLResponse):
    """
    Subclass which adds properties for parsing the output of Spectrum's
    LandscapeResponse model.
    """

    @property
    def total_landscapes(self) -> int:
        return self.xml.get("total-landscapes")

    @property
    def data(self) -> List[Dict[str, str]]:
        """ Parsed output of a Spectrum LandscapeResponse object """
        result = []
        for landscape in self.xml:
            subdict = {}
            for elem in landscape:
                subdict.update({_camel_to_snake(elem.tag): elem.text})
            result.append(subdict)
        return result


class SpectrumModelResponseList(SpectrumXMLResponse):
    """
    Subclass which adds properties for parsing the output of Spectrum's
    ModelResponseList model.
    """

    # Regex objexts used to match the elements in a paginated response

    id_re = re.compile(
        "id=([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"
    )
    start_re = re.compile(r"start=(\d+)")
    throttle_re = re.compile(r"throttlesize=(\d+)")

    def __init__(self, response: Response, resolve_attrs: bool = True):
        self.resolve_attrs = resolve_attrs
        super().__init__(response)

    @property
    def total_models(self) -> int:
        return self.xml.get("total-models")

    @property
    def throttle(self) -> int:
        return self.xml.get("throttle")

    @property
    def next_info(self):
        """
        Provides the necessary parameters to make a subsequent request if not
        all devices were returned.
        """
        next_info = {}
        if not self.xml.get("error"):
            link = self.xml[1].get("href")
            next_info["id"] = self.id_re.search(link).group(1)
            next_info["start"] = self.start_re.search(link).group(1)
            next_info["throttle_size"] = self.throttle_re.search(link).group(1)
        return next_info

    @property
    def data(self) -> List[Dict[str, str]]:
        """ Parsed output of a Spectrum ModelResponseList object """

        parsed_models = []

        # Parse each returned model
        for model in self.xml[0]:

            model_dict = {}

            for attr in model:

                # Try to resolve the attribute ID to corresponding name
                attr_name = (
                    attr_id_to_name(attr.get("id"))
                    if self.resolve_attrs
                    else attr.get("id")
                )

                # Some data may be an attribute list, in which case this is
                # handled by adding a dictionary of the unique OIDs and values
                attr_data = (
                    {
                        instance.get("oid", ""): instance.get("value", "")
                        for instance in attr
                    }
                    if attr.tag == "attribute-list"
                    else attr.text
                )

                model_dict.update({attr_name: attr_data})

            parsed_models.append(model_dict)

        return parsed_models


class SpectrumAssociationResponseList(SpectrumXMLResponse):
    """
    Subclass which adds properties for parsing the output of Spectrum's
    AssociationListResponse model.
    """

    @property
    def data(self) -> List[Tuple[str, str]]:
        """ Associations """
        return [
            {
                "leftmh": assoc.attrib.get("leftmh"),
                "rightmh": assoc.attrib.get("rightmh"),
            }
            for assoc in self.xml[0]
        ]