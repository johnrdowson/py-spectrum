from dataclasses import dataclass
from pyspectrum.attributes import SpectrumModelAttributes as Attrs
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

    # Default model attributes in a request

    MODEL_ATTRS = [
        Attrs.MODEL_HANDLE.value,
        Attrs.MODEL_NAME.value,
        Attrs.MODEL_TYPE_NAME.value,
    ]

    def get_all_devices(
        self,
        attrs: Optional[List[Union[int, str]]] = [],
        resolve_attrs: bool = True,
        **otherparams,
    ) -> SpectrumModelResponseList:
        """
        GET operation which will return all device models and include the
        specified attributes.
        """

        params = {
            "attr": self._normalize_attrs(self.MODEL_ATTRS + attrs),
            "throttlesize": self.api_throttle,
            **otherparams,
        }

        res = self.api.get(url=URIs.devices, params=params)
        res.raise_for_status()

        return SpectrumModelResponseList(res, resolve_attrs)

    def get_model(
        self,
        model_handle: int,
        attrs: Optional[List[Union[int, str]]] = [],
        resolve_attrs: bool = True,
    ) -> SpectrumModelResponseList:
        """ Fetch model with specific attributes """

        res = self.api.get(
            url=f"{URIs.model}/{hex(model_handle)}",
            params={"attr": self._normalize_attrs(self.MODEL_ATTRS + attrs)},
        )
        res.raise_for_status()

        return SpectrumModelResponseList(res, resolve_attrs)

    def get_models(
        self,
        filters: str,
        attrs: Optional[List[Union[int, str]]] = [],
        resolve_attrs: Optional[bool] = True,
        devices_only: Optional[bool] = False,
        **otheropts,
    ) -> SpectrumModelResponseList:
        """ Search models that match the given filter """

        try:
            filter_dict = parse_filter(filters)
        except Exception:
            raise ValueError(
                f"Unable to parse filter expression:\n\n{filters}"
            )

        payload = model_search_xml(
            filter=filter_dict,
            req_attrs=self._normalize_attrs(self.MODEL_ATTRS + attrs),
            throttlesize=self.api_throttle,
            devices_only=devices_only,
            **otheropts,
        )
        res = self.api.post(url=URIs.models, content=payload.encode())
        res.raise_for_status()

        return SpectrumModelResponseList(res, resolve_attrs)
