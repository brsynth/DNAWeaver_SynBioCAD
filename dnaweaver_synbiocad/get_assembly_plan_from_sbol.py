import sbol2 as sbol
from collections import OrderedDict

def id_sort(i: iter):
    """Sort a collection of SBOL objects and/or URIs by identity URI"""
    return sorted(i, key=lambda x: x.identity if isinstance(x, sbol.Identified) else x)


def get_assembly_plan_from_sbol(sbol_doc=None, path=None):
    """Extract an assembly plan from sbol

    :param sbol_doc: A PySBOL Document() containing the designs and parts sequences. A path to a SBOL .xml file can be provided instead.
    :param path: A path to a SBOL .xml file

    :type sbol_doc: sbol.Document
    :type path: str
    
    :rtype: tuple
    :return: Return a tuple with parts_sequences, parts_per_construct and constructs_sequences
      Assembly plan data:
      - parts_sequences is of the form ``{part_id: "ATTTGTGTGC..."}``,
      - parts_per_constructs is of the form ``{construct_id: [part_id_1,...]}``
      - constructs_sequences is of the form ``{construct_id: "ATGCCC..."}``.
    """
    if path is not None:
        sbol_doc = sbol.Document()
        sbol_doc.read(path)

    parts_sequences = {
        seq.displayId.replace('_sequence', '').replace('_seq', ''): seq.elements.upper()
        for seq in sbol_doc.sequences
    }
    parts_per_construct = [
        (component.displayId.replace('_sequence', '').replace('_seq', ''),
         [c.displayId[:-2] for c in id_sort(component.components)])
        for component in sbol_doc.componentDefinitions
        if len(component.components)
    ]

    constructs_sequences = [
        (construct_name, "".join([parts_sequences[part] for part in id_sort(parts)]))
        for construct_name, parts in parts_per_construct
    ]
    parts_per_construct = OrderedDict(parts_per_construct)
    constructs_sequences = OrderedDict(constructs_sequences)
    return (parts_sequences, parts_per_construct, constructs_sequences)
