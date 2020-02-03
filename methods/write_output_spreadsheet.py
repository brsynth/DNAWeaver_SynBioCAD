import pandas

filepath = "output.xlsx"


def write_output_spreadsheet(
    quotes,
    primer_sequences,
    fragment_quotes,
    errors,
    part_sequences,
    construct_parts,
    construct_sequences,
    target="output.xlsx",
):
    """Write the result of DNA construction plan computations as a spreadsheet.

    Parameters
    ----------

    quotes, primer_sequences, fragments_quotes, errors
      Output of ``compute_all_construct_quotes()`` (see docs of this method)
    
    part_sequences, construct_parts, construct_sequences
      Output of ``get_assembly_plan_from_sbol()`` (cf that method's doc)
    
    target
      Path to the output file
    """

    # HELPER FUNCTIONS

    def list_to_spreadsheet(spreadsheet_name, column_names, mylist):
        """Writes the provided list as a sheet of an Excel spreadsheet.
        """
        records = [dict(zip(column_names, row)) for row in mylist]
        dataframe = pandas.DataFrame.from_records(
            records, index=column_names[0], columns=column_names
        )
        dataframe.to_excel(writer, sheet_name=spreadsheet_name)

    def quote_components_ids(quote):
        """Return the list of ids of all fragments or primers in a quote."""

        def _subquote_to_id(subquote):
            "Return the ID of either the quote or the re-used sequence"
            if subquote.source.operation_type == "library":
                return subquote.metadata["part_name"]
            else:
                return subquote.id

        return [
            _subquote_to_id(subquote)
            for loc, subquote in quote.assembly_plan.items()
        ]

    # WRITE THE CONSTRUCTS PARTS SPREADSHEET

    writer = pandas.ExcelWriter(target)

    parts_per_construct = [
        (name, " + ".join(parts)) for name, parts in construct_parts.items()
    ]
    list_to_spreadsheet(
        "construct_parts", ["construct", "parts"], parts_per_construct
    )

    # WRITE THE CONSTRUCT SEQUENCES SPREADSHEET

    list_to_spreadsheet(
        "construct_sequences",
        ["construct", "sequence"],
        construct_sequences.items(),
    )

    # WRITE THE PRIMERS SEQUENCES SPREADSHEET

    list_to_spreadsheet(
        "primer_sequences",
        ["primer", "sequence"],
        sorted(primer_sequences.items()),
    )

    # WRITE THE PARTS SEQUENCES SPREADSHEET

    list_to_spreadsheet(
        "part_sequences", ["part", "sequence"], sorted(part_sequences.items())
    )

    # WRITE THE PCR_EXTENSIONS SPREADSHEET

    fragments_list = [
        (
            fragment,
            quote.metadata["subject"],
            " + ".join(quote_components_ids(quote)),
            quote.sequence,
        )
        for fragment, quote in fragment_quotes.items()
    ]
    list_to_spreadsheet(
        "fragment_extensions",
        ["fragment_id", "part", "primers", "fragment_sequence"],
        fragments_list,
    )

    # WRITE THE ASSEMBLY PLAN SPREADSHEET

    assembly_plan = [
        (construct, quote.source.name, " + ".join(quote_components_ids(quote)))
        for construct, quote in quotes.items()
    ]
    list_to_spreadsheet(
        "assembly_plan", ["construct", "method", "fragments"], assembly_plan,
    )

    # WRITE THE ERRORED CONSTRUCTS SPREADSHEET

    list_to_spreadsheet("errors", ["construct", "error"], list(errors.items()))

    writer.close()
