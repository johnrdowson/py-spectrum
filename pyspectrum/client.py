import csv
from pyspectrum.mixins.models import SpectrumModelsMixin
from typing import AnyStr, List, Dict, Optional

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

    @staticmethod
    def to_csv(
        datalist: List[Dict],
        filepath: AnyStr,
        exclude: Optional[List[str]] = None,
        orderby: Optional[str] = None,
    ) -> None:
        """
        This method will store the given list of dict items to a CSV file.  The
        CSV column headers will be taken from the first list item keys.  The
        `exclude` list can be used to omit designated columns from the CSV file,
        for example ['model_type_id'] would omit the 'model_type_id' column.

        Parameters
        ----------
        datalist
        filepath
        exclude
        orderby
        """
        fieldnames = datalist[0].keys()

        if exclude:
            fieldnames = [col for col in fieldnames if col not in exclude]
            for rec in datalist:
                for key in exclude:
                    del rec[key]

        if orderby in fieldnames:
            datalist = sorted(datalist, key=lambda d: d[orderby].lower())

        with open(filepath, "w+", newline="") as outfile:
            csv_wr = csv.DictWriter(
                outfile, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC
            )
            csv_wr.writeheader()
            csv_wr.writerows(datalist)