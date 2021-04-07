from dataclasses import dataclass
from pyspectrum.base_client import SpectrumBaseClient
from pyspectrum.responses import SpectrumModelResponseList
from pyspectrum.filters import parse_filter
from pyspectrum.template import model_search_xml
from typing import Optional, List, Union


@dataclass
class URIs:
    """ Identifies API URL endpoints used"""

    devices = "/devices"
    model = "/model"
    models = "/models"


class SpectrumModelsMixin(SpectrumBaseClient):
    """
    Spectrum client mixin supporting the following features:
        - devices
        - model
        - models
    """

    def fetch_all_devices(
        self,
        attrs: Optional[List[Union[int, str]]] = [],
        **otherparams,
    ) -> SpectrumModelResponseList:
        """
        GET operation which will return all device models and include the
        specified attributes.
        """

        params = {
            "attr": self._normalize_attrs(self.base_attrs + attrs),
            "throttlesize": self.api_throttle,
            **otherparams,
        }

        res = self.api.get(url=URIs.devices, params=params)
        res.raise_for_status()

        return SpectrumModelResponseList(res)

    def fetch_model(
        self, model_handle: int, attrs: Optional[List[Union[int, str]]] = []
    ) -> SpectrumModelResponseList:
        """ Fetch model with specific attributes """

        res = self.api.get(
            url=f"{URIs.model}/{hex(model_handle)}",
            params={"attr": self._normalize_attrs(self.base_attrs + attrs)},
        )
        res.raise_for_status()

        return SpectrumModelResponseList(res)

    def fetch_models(
        self,
        filters: str,
        attrs: Optional[List[Union[int, str]]] = [],
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
        res = self.api.post(url=URIs.models, content=payload.encode())
        res.raise_for_status()

        return SpectrumModelResponseList(res)
