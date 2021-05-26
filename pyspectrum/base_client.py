from .consts import ENV
from .attributes import SpectrumModelAttributes as Attrs
from .attributes import attr_name_to_id
from .api import SpectrumSession
from .responses import SpectrumLandscapeResponse
from os import environ, getenv
from typing import Optional, AnyStr, DefaultDict, List, Dict, Union


__all__ = ["SpectrumBaseClient"]

URI_MAPPINGS = {"landscapes": "/landscapes"}


class SpectrumBaseClient:
    """ Spectrum Base class """

    API_PATH = "/spectrum/restful"
    API_THROTTLE = 9999

    def __init__(
        self,
        *mixin_classes,
        base_url: Optional[AnyStr] = None,
        username: Optional[AnyStr] = None,
        password: Optional[AnyStr] = None,
        **clientopts,
    ) -> None:
        """
        Initialize the base client
        """

        # API Throttle - Largest number of results to return in single request
        self.api_throttle = clientopts.pop("api_throttle", self.API_THROTTLE)

        # Error will be thrown is base_url not present in either args or env
        base_url = base_url or environ[ENV["base_url"]]
        username = username or getenv(ENV["username"])
        password = password or getenv(ENV["password"])

        self.api = SpectrumSession(
            base_url=base_url + self.API_PATH,
            auth=(username, password),
            **clientopts,
        )

        # Dynamically add any Mixins at the time of client creation. This
        # enables the caller to perform the mixin at runtime without having to
        # define a specific class.

        if mixin_classes:
            self.mixin(*mixin_classes)

        # Default model attributes in a request
        self.base_attrs = [
            Attrs.MODEL_HANDLE.value,
            Attrs.MODEL_NAME.value,
            Attrs.MODEL_TYPE_NAME.value,
        ]

        self.landscape = None

    def __enter__(self):
        """ Returns self when using Context Manager """
        return self

    def __exit__(self, type, value, traceback):
        """
        Gracefully close the httpx.Client object when exiting Context Manager
        """
        self.api.close()

    def __repr__(self):
        """ override the default repr to show the Spectrum base URL """
        cls_name = self.__class__.__name__
        base_url = self.api.base_url
        return f"{cls_name}: {base_url}"

    def close(self):
        """ Gracefully close the httpx.Client object """
        self.api.close()

    @staticmethod
    def _normalize_attrs(attrs: List[Union[int, str]]) -> List[str]:
        """
        Helper function to ingest a user-supplied list of attributes, either
        named or as hexadecimals, and output in a consistent list of hexadecimal
        strings for use in a Spectrum REST API call
        """
        return [
            hex(attr_name_to_id(attr)) if isinstance(attr, str) else attr
            for attr in attrs
        ]

    def mixin(self, *mixin_cls):
        """
        This method allows the Caller to dynamically add a Mixin class
        to the existing Spectrum client instance.
        Parameters
        ----------
        mixin_cls: subclasses of SpectrumBaseCl
            The mixin classes whose methods will be added to the existing
            Spectrum client instance (self).
        """
        self.__class__ = type(
            self.__class__.__name__, (self.__class__, *mixin_cls), {}
        )

    def fetch_landscapes(self) -> SpectrumLandscapeResponse:
        """ Gets the Landscape IDs """
        res = self.api.get(url=URI_MAPPINGS["landscapes"])
        res.raise_for_status()
        return SpectrumLandscapeResponse(res)
