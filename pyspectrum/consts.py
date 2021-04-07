from dataclasses import dataclass


@dataclass
class ENV:
    """ Identifies enviornment variables used """

    base_url = "SPECTRUM_URL"
    username = "SPECTRUM_USERNAME"
    password = "SPECTRUM_PASSWORD"
