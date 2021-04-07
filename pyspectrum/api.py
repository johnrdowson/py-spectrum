from httpx import Client, Timeout


__all__ = ["SpectrumSession"]


class SpectrumSession(Client):
    """
    Low-level instance to interact with the Spectrum API via REST calls.
    """

    API_DEFAULT_TIMEOUT = Timeout(5.0, read=30.0)
    API_DEFAULT_VERIFY = False

    def __init__(self, base_url: str, *args, **kwargs) -> None:
        """
        Initialize the client session with the Spectrum API
        """

        kwargs.setdefault("verify", self.API_DEFAULT_VERIFY)

        super().__init__(
            base_url=str(base_url),
            timeout=kwargs.pop("timeout", self.API_DEFAULT_TIMEOUT),
            proxies=kwargs.pop("proxies", {"all://": None}),
            *args,
            **kwargs,
        )

        self.headers["Content-Type"] = "application/xml"
        self.headers["Accept"] = "application/xml"
