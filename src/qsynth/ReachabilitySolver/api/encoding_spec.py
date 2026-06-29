from dataclasses import dataclass

@dataclass
class EncodingSpec:
    """
    Contains the specification of a reachability problem encoding.
    """
    encoding_type: str
    payload: dict
