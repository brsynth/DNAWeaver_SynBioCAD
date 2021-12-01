# DNA Weaver (for SynBioCAD)

[![Anaconda-Server Badge](https://anaconda.org/bioconda/dnaweaver_synbiocad/badges/version.svg)](https://anaconda.org/bioconda/dnaweaver_synbiocad) [![Anaconda-Server Badge](https://anaconda.org/bioconda/dnaweaver_synbiocad/badges/latest_release_date.svg)](https://anaconda.org/bioconda/dnaweaver_synbiocad) [![Build Status](https://travis-ci.org/Edinburgh-Genome-Foundry/galaxy_synbiocad_dnaweaver.svg?branch=master)](https://travis-ci.org/Edinburgh-Genome-Foundry/galaxy_synbiocad_dnaweaver)

This project finds assembly plans to buil the genetic designs generated by the SynBioCAD project using either Golden Gate or Gibson assembly. It leverages on [DNA Weaver](https://github.com/Edinburgh-Genome-Foundry/DnaWeaver) Python library to find optimal strategies for assembling large DNA constructs. Given an arbitrary sequence, DNA Weaver will select the most adapted commercial DNA providers, cloning methods and parts repositories (depending on your preferences), and will design all necessary assembly fragments and assembly steps. Try it online via the DNA Weaver web app.

DNA Weaver was written with versatility and extensibility in mind: each DNA source and assembly method can be customized, and assembly plans can be optimized with respect to total price, overall duration of the assembly, or assembly success probabilities.

## Installing
```bash
conda install -c bioconda dnaweaver_synbiocad
```

## Running

Run ``python -m dnaweaver_synbiocad --help`` for the description of the parameters.
The typical example is:

```bash
python -m dnaweaver_synbiocad tests/data/input/test.xml output.xlsx any_method
```

Where ``test.xml`` is a path to an .xml SBOL file containing constructs designs and sequences, ``output.xlsx`` is a spreadsheet report of the assembly
plan, and ``any_method`` (which can also be only ``gibson`` or ``golden_gate``)
indicates to consider both methods.

## Testing

The .travis.yml file describes the testing procedure. To run the test install pytest:

```
pip install pytest
```

or

```
conda install -c conda-forge pytest
```

Then run the tests with:

```
python3 -m pytest
```

## What this program does

**Problem:**

Given a set of designs (one design is a construct name and list of
its parts), find a valid and efficient assembly plan to build all the designs.
The designs and part sequences are provided as an SBOL file
(see ``tests/data/input/test.xml`` for an example)

**Method:**

- We assume that the different standard parts are available or will be ordered,
  with the exact sequence provided in the input file (in the future it would be easy to automatically break long parts into smaller fragments).
- The desired construct sequence for a design is simply the contenation of that design's part sequences in the right order (no assembly overhang is included).
- Buy primers with overhangs to extend the parts fragments via PCR and create   homologies between them so they can be assembled together.
- Assemble each construct in a single step with Golden Gate assembly if possible (that is if at least one site out of BsaI, BbsI and BsmBI is totally absent from the construct sequence), else with Gibson assembly. It can also be only one of the two methods if the option ``gibson`` or ``golden_gate`` is selected instead of ``any_method``.
- Start with the first design, and for each subsequence design assembly plan   reuse the primers ordered and fragments PCRed in previous designs, if   relevant.

Here is a schema of the supply network used:


<p align="center"><img width="400" src="docs/illustration.png"></p>

**Output:**

See ``example_output.xlsx`` for an example. The output is an Excel spreadsheet with the following sub-sheets:

- ``construct_parts``: the ID and list of part names (in the right order) for each design.
- ``construct_sequences``: the final sequence of the constructs to build.
- ``part_sequences``: the list of each standard part and its sequence (same information as in the input SBOL file).
- ``fragment_extensions``: for each PCR fragment, the standard part and the primers to use
- ``assembly_plan``: for each design, the list of PCR fragments to use. 
- ``errors``: list of errors to help troubleshooting assemblies for which no valid assembly plan was found.

## Description of the example/testing sample

The example input SBOL is from an example file provided by @pablocarb, with a random sequence used for the terminator (Ter) part. The example has 48 designs which are well representative. Some have type-2s sites preventing golden gate, some use the same part more than once, making it a challenging scenario for scarless Golden Gate assembly.

The output ``example_output.xlsx`` shows the plan generated to build all the designs. The plan has:

- 19 different base parts (provided by the SBOL input)
- 125 primers to be ordered to extend the parts in various ways (that's less than 3 primers per design to build, thanks to primer reuse)
- 116 fragments to be PCRed (less than 3 PCRs per design to build, thanks to fragment reuse).
- 15 designs seem to need Gibson assembly as they contain BsaI, BsmBI, and BbsI sites, the rest use Golden Gate assembly. 

## Limitations

For constructs with repeated parts and other homologies (such as, in the example, the designs with several "Ter" in a row, ), Gibson assembly (and probably LCR assembly too) may create misanealled constructs and more clones will need to be picked. This is not taken into account by the script at the moment. This could be fixed by buying custom fragments from a commercial vendor for the extreme cases (i.e. by amending the current implementation to forbid gibson cuts in regions with homologies elsewhere, and add a DNA vendor in the supply network).

## Code organisation

- ``dnaweaver_synbiocad/generate_supply_network.py`` -- implements the DnaWeaver supply network from the figure above.
- ``dnaweaver_synbiocad/compute_all_constructs.py`` -- main loop to iterate over all constructs and get assembly plans using the supply network.
- ``dnaweaver_synbiocad/write_output_spreadsheet.py`` -- method to write the data collected into the output spreadsheet.

Written by [Zulko](https://github.com/Zulko) at the [Edinburgh Genome Foundry](https://edinburgh-genome-foundry.github.io/), and maintained by [Joan Hérisson](https://github.com/breakthewall).