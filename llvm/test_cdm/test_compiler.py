from enum import IntEnum
import json
from pathlib import Path
import subprocess


class ReturnCode(IntEnum):
    SUCCESS = 0
    ERROR = 1
    TIMEOUT = 13


def assert_nested_subset(expected, actual, path=""):
    if isinstance(expected, dict):
        assert isinstance(
            actual, dict
        ), f"Type mismatch at {path}: expected dict, got {type(actual).__name__}"
        for key, value in expected.items():
            assert key in actual, f"Missing key '{key}' at {path}"
            assert_nested_subset(value, actual[key], path + f".{key}" if path else key)
    elif isinstance(expected, list):
        assert isinstance(
            actual, list
        ), f"Type mismatch at {path}: expected list, got {type(actual).__name__}"
        assert len(expected) == len(
            actual
        ), f"Length mismatch at {path}: expected {len(expected)}, got {len(actual)}"
        for i, (exp_item, act_item) in enumerate(zip(expected, actual)):
            assert_nested_subset(exp_item, act_item, path + f"[{i}]")
    else:
        assert (
            expected == actual
        ), f"Mismatch at {path}: expected {expected}, got {actual}"


def test_compiler():
    test_dir = Path(__file__).parent.absolute()
    output_dir = test_dir / "output"
    src_dir = test_dir / "src"
    build_dir = test_dir / "build"
    gen_dir = build_dir / "gen"
    bin_dir = (test_dir / ".." / "build" / "bin").absolute()
    resources = build_dir / "resources"
    ivt = test_dir / "ivt.asm"

    build_dir.mkdir(parents=True, exist_ok=True)
    gen_dir.mkdir(parents=True, exist_ok=True)

    for expected in filter(Path.is_file, output_dir.iterdir()):
        src_file = src_dir / f"{expected.stem}.c"
        assert src_file.exists()

        asm_res = gen_dir / f"{expected.stem}.asm"
        asm_gen_process = subprocess.run(
            [
                "./clang",
                "-g",
                "-target",
                "cdm",
                "-S",
                "-O1",
                str(src_file),
                "-o",
                str(asm_res),
            ],
            cwd=str(bin_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert asm_gen_process.returncode == ReturnCode.SUCCESS

        bin_res = gen_dir / f"{expected.stem}.img"
        bin_gen_process = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{build_dir}:/root",
                "-v",
                f"{ivt}:/root/ivt.img",
                "cdm-devkit",
                "cocas",
                "-t",
                "cdm16",
                "-o",
                f"/root/gen/{expected.stem}.img",
                "/root/ivt.img",
                f"/root/gen/{expected.stem}.asm",
            ],
            cwd=str(bin_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert bin_gen_process.returncode == ReturnCode.SUCCESS

        mem_res = gen_dir / f"mem_{expected.stem}.img"
        run_process = subprocess.run(
            [
                "java",
                "-jar",
                resources / "logisim-runner-all.jar",
                bin_res,
                resources / "test_circuit_emu.circ",
                mem_res,
                resources / "config.properties",
                "10000",
            ],
            cwd=resources,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        assert run_process.returncode == ReturnCode.SUCCESS
        output = json.loads(run_process.stdout)
        output["memory"] = json.loads(Path(mem_res).read_text("UTF-8"))
        data_expected = json.loads(Path(expected).read_text("UTF-8"))

        assert_nested_subset(data_expected, output)
