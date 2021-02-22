from typing import List, Dict
from types import SimpleNamespace
import gzip
import io
import blackboxprotobuf


def pbuf_dimensions_to_dict(pbuf_dimensions: List[Dict[str, any]]) -> Dict[str, str]:
    """
    Convert pbuf decoded message dimensions array to dict
    :param pbuf_dimensions: List of dimensions
    :type pbuf_dimensions: list
    :return: Dict Of pbuf message dimensions
    :rtype: dict
    """

    pbuf_dimensions_dict = dict()
    for pbuf_msg in pbuf_dimensions:
        pbuf_dimensions_dict[pbuf_msg["1"].decode("utf-8")] = pbuf_msg["2"].decode("utf-8")

    return pbuf_dimensions_dict


def pbuf_dimensions_to_namespace(pbuf_dimensions: List[Dict[str, any]]) -> SimpleNamespace:
    """
    Create a SimpleNameSpace from pbuf dimensions message
    :param pbuf_dimensions: List of dimensions from pbuf message
    :return: SimpleNamespace
    :rtype: SimpleNamespace
    """

    pbufdict = pbuf_dimensions_to_dict(pbuf_dimensions)
    return SimpleNamespace(**pbufdict)


def decode_sfx_request(request_content: bytes) -> Dict[str, any]:
    """
    Decode signalfx requests message
    :param request_content: Gziped message
    :type request_content: bytes
    :return: Decoded protobuf message as dict
    :rtype: dict
    """
    gunziped_message = gzip.GzipFile(fileobj=io.BytesIO(request_content)).read()
    decoded_messge, _ = blackboxprotobuf.decode_message(gunziped_message)

    return decoded_messge
