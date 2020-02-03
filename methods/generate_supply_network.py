import dnaweaver as dw


def generate_supply_network(
    parts_sequences,
    already_amplified_fragments,
    already_ordered_primers,
    assembly_method,
):
    """Build the supply network, return the main station.

    See the docs for an overview of the supply network.

    Parameters
    ----------

    parts_sequences
      A dictionary {part_id: "ATGCGC..."} of the base genetic parts, which will
      be considered as available for free.
    
    already_amplified_fragments
      A dictionary {fragment_id: "ATGCTGA"} providing sequences of fragments
      made for previous assemblies, which will be considered as available for
      free.
    
    already_ordered_primers
      A dictionary {primer_id: "ATGCTGA"} providing sequences of primers
      ordered for previous assemblies, which will be considered as available
      for free.
    
    assembly_method
      Either "gibson", "golden_gate", or "any_method" (each construct will
      then be assembled using any method, with a preference for Golden Gate
      Assembly)
    """
    # PRIMERS SUPPLIERS

    already_ordered_primers_library = dw.PartsLibrary(
        name="already_ordered_primers", parts_dict=already_ordered_primers,
    )
    primers_company = dw.CommercialDnaOffer(
        name="oligo_supplier", pricing=dw.FixedCostPricing(1), lead_time=0,
        sequence_constraints=(dw.SequenceLengthConstraint(max_length=100),)

    )

    primers_comparator = dw.DnaSuppliersComparator(
        suppliers=[primers_company, already_ordered_primers_library]
    )

    # STATIONS FOR PARTS EXTENSION VIA PCR

    primer_homology_selector = dw.TmSegmentSelector(
        min_size=19, max_size=25, min_tm=50, max_tm=70
    )
    parts_pcr_station = dw.PcrExtractionStation(
        name="pcr_part_extension_station",
        primers_supplier=primers_comparator,
        sequences=parts_sequences,
        max_overhang_length=30,
        extra_cost=2,
        homology_selector=primer_homology_selector,
    )

    already_amplified_fragments_library = dw.PartsLibrary(
        name="already_amplified_fragments",
        parts_dict=already_amplified_fragments,
    )
    fragments_comparator = dw.DnaSuppliersComparator(
        name="fragments_comparator",
        suppliers=[parts_pcr_station, already_amplified_fragments_library],
    )

    # ASSEMBLY STATIONS

    gibson_assembly_station = dw.DnaAssemblyStation(
        name="gibson_assembly",
        supplier=fragments_comparator,
        assembly_method=dw.GibsonAssemblyMethod(
            overhang_selector=dw.FixedSizeSegmentSelector(40),
            cost=50
        ),
        coarse_grain=600,
        fine_grain=None,
        a_star_factor="auto"
    )
    golden_gate_stations_comparator = dw.DnaSuppliersComparator(
        name="golden_gate_comparator",
        return_first_accepted_quote=True,
        suppliers=[
            dw.DnaAssemblyStation(
                name="golden_gate_assembly_%s" % enzyme,
                supplier=fragments_comparator,
                assembly_method=dw.GoldenGateAssemblyMethod(
                    enzyme=enzyme
                ),
                coarse_grain=600,
                fine_grain=None,
                cut_spread_radius=2,
                a_star_factor="auto"
            )
            for enzyme in ["BsmBI", "BsaI", "BbsI"]
        ]
    )

    # SELECT SUPPLIERS DEPENDING ON THE SELECTED ASSEMBLY METHOD

    suppliers = []
    if assembly_method in ["golden_gate", "any_method"]:
        suppliers.append(golden_gate_stations_comparator)
    if assembly_method in ["gibson", "any_method"]:
        suppliers.append(gibson_assembly_station)

    # RETURN THE METHODS COMPARATOR

    main_station = dw.DnaSuppliersComparator(name="main", suppliers=suppliers)
    return main_station
