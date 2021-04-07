from pyspectrum.mixins.models import SpectrumModelsMixin

__all__ = ["SpectrumClient"]


class SpectrumClient(SpectrumModelsMixin):
    """
    An instance SpectrumClient is used to interact with the Spectrum OneClick
    API via methods that abstract the underlying API calls.

    The SpectrumClient is composed of mixins, each of which address a different
    aspect of the Spectrum product.  This composition structure allows the
    Developer to define a client with only those feature aspects that they need
    for their program.

    To dynamically add a Mixin class, use the `mixin` method defined
    by `SpectrumBaseClient`

    Examples
    --------
        from pyspectrum import SpectrumClient
        from pyspectrum.mixins import SpectrumModelsMixin
        spectrum = SpectrumClient()
        spectrum.mixin(SpectrumModelsMixin)
    """
