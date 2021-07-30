from pyspectrum.attributes import SpectrumModelAttributes as Attrs
from pyspectrum.attributes import attr_name_to_id
from pyspectrum.api import SpectrumSession
from pyspectrum.responses import SpectrumLandscapeResponse
from pyspectrum.responses import SpectrumModelResponseList
from pyspectrum.responses import SpectrumAssociationResponseList
from pyspectrum.filters import parse_filter
from pyspectrum.template import model_search_xml
from os import environ, getenv
from typing import Optional, AnyStr, DefaultDict, List, Dict, Union


__all__ = ["SpectrumClient"]

URI = {
    "associations": "/associations/relation",
    "landscapes": "/landscapes",
    "devices": "/devices",
    "model": "/model",
    "models": "/models",
}

ENV = {
    "base_url": "SPECTRUM_URL",
    "username": "SPECTRUM_USERNAME",
    "password": "SPECTRUM_PASSWORD",
}


class SpectrumClient:
    """ Spectrum Client """

    API_PATH = "/spectrum/restful"
    API_THROTTLE = 9999

    def __init__(
        self,
        base_url: Optional[AnyStr] = None,
        username: Optional[AnyStr] = None,
        password: Optional[AnyStr] = None,
        resolve_attrs: Optional[bool] = True,
        **clientopts,
    ) -> None:
        """
        Initialize the client
        """

        # API Throttle - Largest number of results to return in single request

        self.api_throttle = clientopts.pop("api_throttle", self.API_THROTTLE)

        # Error will be thrown is base_url not present in either args or env

        base_url = base_url or environ[ENV["base_url"]]
        username = username or getenv(ENV["username"])
        password = password or getenv(ENV["password"])

        # HTTP client session to Spectrum OneClick server

        self.api = SpectrumSession(
            base_url=base_url + self.API_PATH,
            auth=(username, password),
            **clientopts,
        )

        # Default attributes to request

        self.base_attrs = [
            Attrs.MODEL_HANDLE.value,
            Attrs.MODEL_NAME.value,
            Attrs.MODEL_TYPE_NAME.value,
        ]

        self.resolve_attrs = resolve_attrs

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

    def get_landscapes(self) -> SpectrumLandscapeResponse:
        """ Gets the Landscape IDs """
        res = self.api.get(url=URI["landscapes"])
        res.raise_for_status()
        return SpectrumLandscapeResponse(res)

    def get_devices(
        self,
        attrs: Optional[List[Union[int, str]]] = [],
        resolve_attrs: bool = True,
        **otherparams,
    ) -> SpectrumModelResponseList:
        """
        Returns all device models along with the specified attributes
        """

        params = {
            "attr": self._normalize_attrs(self.base_attrs + attrs),
            "throttlesize": self.api_throttle,
            **otherparams,
        }

        res = self.api.get(url=URI["devices"], params=params)
        res.raise_for_status()

        return SpectrumModelResponseList(res, resolve_attrs)

    def get_model(
        self,
        model_handle: int,
        attrs: Optional[List[Union[int, str]]] = [],
        resolve_attrs: bool = True,
    ) -> SpectrumModelResponseList:
        """ Returns specific model and attributes """

        res = self.api.get(
            url=f"{URI['model']}/{hex(model_handle)}",
            params={"attr": self._normalize_attrs(self.base_attrs + attrs)},
        )
        res.raise_for_status()

        return SpectrumModelResponseList(res, resolve_attrs)

    def get_models(
        self,
        filters: str,
        attrs: Optional[List[Union[int, str]]] = [],
        resolve_attrs: bool = True,
        **otheropts,
    ) -> SpectrumModelResponseList:
        """ Fetch all models that match the given filter """

        try:
            filter_dict = parse_filter(filters)
        except Exception:
            raise ValueError(
                f"Unable to parse filter expression:\n\n{filters}"
            )

        payload = model_search_xml(
            filter=filter_dict,
            req_attrs=self._normalize_attrs(self.base_attrs + attrs),
            throttlesize=self.api_throttle,
            **otheropts,
        )
        res = self.api.post(url=URI["models"], content=payload.encode())
        res.raise_for_status()

        return SpectrumModelResponseList(res, resolve_attrs)

    def get_associations(
        self,
        model_handle: int,
        rel_handle: int,
        side: Optional[str] = "either",
    ):
        """
        Get associations for a specific relation and model.
        """

        if side.lower() not in ["left", "right", "either"]:
            raise ValueError("Associations supported: left, right, either")

        res = self.api.get(
            url=f"{URI['associations']}/{rel_handle}/model/{model_handle}",
            params={"side": side.lower()},
        )

        return SpectrumAssociationResponseList(res)