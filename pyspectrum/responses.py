from pyspectrum.attributes import attr_id_to_name
from lxml import etree
from httpx import Response
from typing import List, Dict, Tuple
import re


__all__ = [
    "SpectrumLandscapeResponse",
    "SpectrumModelResponseList",
    "SpectrumAssociationResponseList",
    "SpectrumGetEventResponseList",
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

        _xparser = etree.XMLParser(recover=True, remove_blank_text=True)

        try:
            root = etree.fromstring(response.content, parser=_xparser)
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
    def result(self) -> List[Dict[str, str]]:
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

    def __init__(self, response: Response, resolve_attrs: bool = True):
        self.resolve_attrs = resolve_attrs
        super().__init__(response)

    @property
    def total_models(self) -> int:
        return self.xml.get("total-models")

    @property
    def result(self) -> List[Dict[str, str]]:
        """ Parsed output of a Spectrum ModelResponseList object """

        parsed_models = []

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
    def result(self) -> List[Tuple[str, str]]:
        """ Associations """
        return [
            {
                "leftmh": assoc.attrib.get("leftmh"),
                "rightmh": assoc.attrib.get("rightmh"),
            }
            for assoc in self.xml[0]
        ]


class SpectrumGetEventResponseList(SpectrumXMLResponse):
    """
    Subclass which adds properties for parsing the output of Spectrum's
    GetEventResponseList model.
    """

    def __init__(self, response: Response, resolve_attrs: bool = True):
        self.resolve_attrs = resolve_attrs
        super().__init__(response)

    @property
    def result(self) -> List[Dict[str, str]]:
        """ Parsed output of a Spectrum GetEventResponseList object """

        parsed_events = []

        for event in self.xml[0]:

            event_dict = {}

            for attr in event:

                # Try to resolve the attribute ID to corresponding name

                attr_name = (
                    attr_id_to_name(attr.get("id"))
                    if self.resolve_attrs
                    else attr.get("id")
                )
                attr_data = attr.text
                event_dict.update({attr_name: attr_data})

            parsed_events.append(event_dict)

        return parsed_events