DNAWeaver's Documentation
=========================

Indices and tables
##################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Introduction
############

.. _RetroRules: https://retrorules.org/
.. _RetroPath2.0: https://github.com/Galaxy-SynBioCAD/RetroPath2
.. _rp2paths: https://github.com/Galaxy-SynBioCAD/rp2paths
.. _rpSBML: https://github.com/Galaxy-SynBioCAD/rpBase
.. _rpBase: https://github.com/Galaxy-SynBioCAD/rpBase
.. _rpCache: https://github.com/Galaxy-SynBioCAD/rpCache
.. _rpVisualiser: https://github.com/brsynth/rpVisualiser
.. _rpSelenzyme: https://github.com/brsynth/rpSelenzyme
.. _SBOL: https://sbolstandard.org/
.. _doebase: https://github.com/pablocarb/doebase
.. _PartsGenie: https://github.com/neilswainston/PartsGenie-legacy
.. _DNAWeaver: https://github.com/Edinburgh-Genome-Foundry/DnaWeaver

Welcome to DNAWeaver's documentation. This tool provides a docker that calls a DNAWeaver_ REST service to generate the assembly protocols for the input SBOL.

.. code-block:: bash

   docker build -t brsynth/dnaweaver-standalone .

API
###

.. currentmodule:: rpTool

.. autoclass:: runDNAWeaver
    :show-inheritance:
    :members:
    :inherited-members:

.. autoclass:: runDNAWeaver_hdd
    :show-inheritance:
    :members:
    :inherited-members:

.. currentmodule:: methods/compute_all_construct_quotes

.. autoclass:: methods/compute_all_construct_quotes
    :show-inheritance:
    :members:
    :inherited-members:

.. currentmodule:: methods/generate_supply_network

.. autoclass:: methods/generate_supply_network
    :show-inheritance:
    :members:
    :inherited-members:

.. currentmodule:: methods/get_assembly_plan_from_sbol

.. autoclass:: methods/get_assembly_plan_from_sbol
    :show-inheritance:
    :members:
    :inherited-members:

.. currentmodule:: methods/write_output_spreadsheet

.. autoclass:: methods/write_output_spreadsheet
    :show-inheritance:
    :members:
    :inherited-members:

