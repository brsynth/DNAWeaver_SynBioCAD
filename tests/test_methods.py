import os
import subprocess
import pandas

this_directory = os.path.dirname(os.path.realpath(__file__))


def get_sheet_length(filepath, sheet_name):
    return len(
        pandas.read_excel(
            filepath,
            sheet_name=sheet_name,
            engine='openpyxl'
        )
    )


def run_test_with_assembly_method(output_path, assembly_method):
    script_path = "python -m dnaweaver_synbiocad"
    input_path = os.path.join(
        this_directory,
        'data',
        'input',
        'test.xml'
    )
    parameters = [
        input_path,
        output_path,
        assembly_method,
        "--constructs=6",
    ]
    process = subprocess.run(
        script_path.split() + parameters,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if process.returncode:
        error = process.stderr.decode()
        parameters = " ".join(parameters)
        raise OSError("process failed:\n\n%s\n\n%s" % (error, parameters))
    return process.stdout


def test_with_any_assembly_method(tmpdir):
    output_path = os.path.join(str(tmpdir), "test_output.xlsx")
    run_test_with_assembly_method(output_path, assembly_method="any_method")
    expected = dict(primer_sequences=57, fragment_extensions=35, errors=0)
    for sheet_name, expected_size in expected.items():
        assert get_sheet_length(output_path, sheet_name) == expected_size


def test_with_gibson_assembly(tmpdir):
    output_path = os.path.join(str(tmpdir), "test_output.xlsx")
    run_test_with_assembly_method(output_path, assembly_method="gibson")
    expected = dict(primer_sequences=50, fragment_extensions=37, errors=0)
    for sheet_name, expected_size in expected.items():
        assert get_sheet_length(output_path, sheet_name) == expected_size


def test_with_golden_gate_assembly(tmpdir):
    output_path = os.path.join(str(tmpdir), "test_output.xlsx")
    run_test_with_assembly_method(output_path, assembly_method="golden_gate")
    # Here we expect 25 constructs to fail as they have internal BsmBI sites.
    expected = dict(primer_sequences=37, fragment_extensions=24, errors=2)
    for sheet_name, expected_size in expected.items():
        assert get_sheet_length(output_path, sheet_name) == expected_size
