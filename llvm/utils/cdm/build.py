#!/usr/bin/env python3

import argparse
import os
import shutil
import subprocess
import sys

PROJECT_PATH=os.path.realpath(__file__ + "/../../../..")

def log(msg, verbose):
    if verbose:
        print(msg)

def find_linker(verbose):
    for linker in ["mold", "lld", "ld"]:
        path = shutil.which(linker)
        if path:
            log(f"Found linker: {linker} ({path})", verbose)
            return linker
    raise RuntimeError("No suitable linker found (mold, lld, ld)")

def run(cmd, verbose):
    if verbose:
        print("Running:", " ".join(cmd))
    subprocess.check_call(cmd)

def main():
    parser = argparse.ArgumentParser("Opinionated build script")

    parser.add_argument(
        "build_dir",
        nargs="?",
        default=PROJECT_PATH + "/llvm/build",
        help="build directory (default: cdm16-llvm-neo/llvm/build)"
    )
    parser.add_argument("-targets", default="", help="additional targets to build (e.g. \"RISCV;X86;Mips\")"),
    parser.add_argument("-exp-targets", default="", help="additional experimental targets (besides CDM) to build (e.g. \"M68k;DirectX\")")
    parser.add_argument("-host-target", action="store_true", help="enable host target")
    parser.add_argument("-debug", action="store_true", help="build with Debug configuration")
    parser.add_argument("-clang", default="clang", help="host clang to use (default: clang)")
    parser.add_argument("-clangxx", default="clang++", help="host clang++ to use (default: clang++)")
    parser.add_argument("-linker", default="", help="linker to use (default: {mold | lld | ld})")
    parser.add_argument("-j", type=int, default=1, help="number of linker jobs (default: 1)")
    parser.add_argument("-use-ninja", action="store_true", help="use Ninja build system")
    parser.add_argument("-no-assertions", action="store_true", help="disable assertions")
    parser.add_argument("-static", action="store_true", help="build with static linking")
    parser.add_argument("-configure-flags", default="", help="additional CMake configure flags")
    parser.add_argument("-verbose", action="store_true", help="verbose output")

    args = parser.parse_args()

    llvm_src_dir = PROJECT_PATH + "/llvm"
    build_dir = os.path.abspath(args.build_dir)

    os.makedirs(build_dir, exist_ok=True)

    build_type = "Debug" if args.debug else "Release"
    assertions = "OFF" if args.no_assertions else "ON"

    linker = args.linker if args.linker else find_linker(args.verbose)

    generator = "Ninja" if args.use_ninja else "Unix Makefiles"

    targets = args.targets
    if args.host_target:
        targets = "Native" + (f";{targets}" if targets else "")

    add_targets = ";" + args.exp_targets if args.exp_targets else ""

    cmake_cmd = [
        "cmake",
        "-S", llvm_src_dir,
        "-B", build_dir,
        "-G", generator,
        f"-DCMAKE_C_COMPILER={args.clang}", f"-DCMAKE_CXX_COMPILER={args.clangxx}",
        "-DLLVM_OPTIMIZED_TABLEGEN=ON",
        f"-DLLVM_TARGETS_TO_BUILD={args.targets}",
        f"-DLLVM_EXPERIMENTAL_TARGETS_TO_BUILD=CDM" + add_targets,
        "-DLLVM_DEFAULT_TARGET_TRIPLE=cdm",
        f"-DCMAKE_BUILD_TYPE={build_type}",
        f"-DLLVM_ENABLE_ASSERTIONS={assertions}",
        "-DLLVM_ENABLE_PROJECTS=clang;lld",
        "-DLLVM_INCLUDE_EXAMPLES=OFF",
        "-DLLVM_INCLUDE_BENCHMARKS=OFF",
        "-DLLVM_BUILD_DOCS=OFF",
        "-DLLVM_ENABLE_OCAMLDOC=OFF",
        "-DLLVM_ENABLE_BINDINGS=OFF",
        "-DLLVM_ENABLE_ZLIB=OFF",
        "-DLLVM_ENABLE_ZSTD=OFF",
        f"-DLLVM_USE_LINKER={linker}",
        f"-DLLVM_PARALLEL_LINK_JOBS={args.j}",
    ]

    if args.static:
        cmake_cmd.extend(["-DLLVM_STATIC_LINK_CXX_STDLIB=ON", "-DLLVM_BUILD_STATIC=ON", "-DLIBCLANG_BUILD_STATIC=ON"])

    if args.configure_flags:
        cmake_cmd.extend(args.configure_flags.split())

    log("Configuring LLVM...", args.verbose)
    run(cmake_cmd, args.verbose)

    build_cmd = [
        "cmake",
        "--build", build_dir
    ]

    log("Building LLVM...", args.verbose)
    run(build_cmd, args.verbose)

    print("\nLLVM build completed successfully.")
    print(f"Build directory: {build_dir}")
    print(f"Build type: {build_type}")
    print(f"Assertions: {'ON' if assertions == 'ON' else 'OFF'}")
    print(f"Linker used: {linker}")

if __name__ == "__main__":
    main()

