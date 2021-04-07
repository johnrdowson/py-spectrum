from lxml import etree

_xparser = etree.XMLParser(recover=True, remove_blank_text=True)


def fromstring(content):
    return etree.fromstring(content, parser=_xparser)


def tostring(ele):
    return etree.tostring(ele, pretty_print=True).decode()