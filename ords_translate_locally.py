#!/usr/bin/env python3

"""
Testing local translation.

See https://private.mt/ for online demo.

Requirements:

    * [translateLocally](https://github.com/XapaJIaMnu/translateLocally)
    * [Marian](https://marian-nmt.github.io/quickstart)
    * [NVidia cuBLAS](https://docs.nvidia.com/cuda/cublas/index.html)
    * [openBLAS](https://www.openblas.net/)

Set up and tested with

    * Ubuntu 22. kernel 5.15.0-105-generic
    * NVidia RTX 4070 with driver 535.171.04
    * libcublas.so.11.7.4.6
    * Marian v1.12.0
    * translateLocally-v0.0.2+3cbe86d-Ubuntu-22.04.AVX.deb

1. MAKE Marian

    [Marian docs](https://marian-nmt.github.io/quickstart/)

    ERROR due to CUDA 11:

    `CMake Error at CMakeLists.txt:415 (message):`
    `cuBLASLt library not found`

    <https://github.com/marian-nmt/marian/pull/416/commits/2f11a94dd92a3ed13937399ed9412af6ed8b7b26>

    FIX with symlink:

    `sudo ln -s /usr/lib/x86_64-linux-gnu/stubs/libcublas.so /usr/lib64/`

    OR edit CMake file:

    `# find_library(CUDA_cublasLt_LIBRARY NAMES cublasLt PATHS ${CUDA_TOOLKIT_ROOT_DIR}/lib64 ${CUDA_TOOLKIT_ROOT_DIR}/lib/x64 NO_DEFAULT_PATH)`
    `find_library(CUDA_cublasLt_LIBRARY NAMES cublasLt PATHS ${CUDA_TOOLKIT_ROOT_DIR}/lib64 ${CUDA_TOOLKIT_ROOT_DIR}/lib/x64 ${CUDA_TOOLKIT_ROOT_DIR} /usr/lib/x86_64-linux-gnu/ /usr/lib/x86_64-linux-gnu/stubs NO_DEFAULT_PATH)`

2. Install translateLocally

    Either from [repo](https://github.com/XapaJIaMnu/translateLocally) or binary pkg.

3. Install language models

    The software provides a GUI through which models can be downloaded. Or via cli:

    -l, --list-models              List locally installed models.
    -a, --available-models         Connect to the Internet and list available
                                    models. Only shows models that are NOT
                                    installed locally or have a new version
                                    available online.
    -d, --download-model <output>  Connect to the Internet and download a model.

    `$ translateLocally -l
    English-German type: tiny version: 2; To invoke do -m en-de-tiny
    English-French type: tiny version: 1; To invoke do -m en-fr-tiny
    French-English type: tiny version: 1; To invoke do -m fr-en-tiny`

NOTES:

    * Currently Dutch and Danish language models not available via the GUI.
    * Next steps: try to train own models for this.

"""

from funcs import *
import pandas as pd
import subprocess


# Select function to run.
def exec_opt(options):
    while True:
        for i, desc in options.items():
            print("{} : {}".format(i, desc))
        choice = input("Type a number: ")
        try:
            choice = int(choice)
        except ValueError:
            print("Invalid choice")
        else:
            if choice >= len(options):
                print("Out of range")
            else:
                f = options[choice]
                print(f)
                eval(f)


# Requires the translation table. See ords_deepl_1setup.py.
def _pd_from_db():

    sql = r"SELECT id_ords, problem as fr, en FROM ords_problem_translations WHERE language_known = 'fr' ORDER BY id_ords"
    return pd.DataFrame(dbfuncs.query_fetchall(sql))


# Create the source text file, in this case French.
def file_in():

    pathfuncs.rm_file(path_in)
    df = _pd_from_db()
    with open(path_in, "w") as f:
        f.writelines("\n".join(df.fr.to_list()))


# Shell out to the software with command to translate French to English.
def translate():
    if not pathfuncs.check_path(path_in):
        print("FILE NOT FOUND {}".format(path_in))
        exit()
    pathfuncs.rm_file(path_out)
    command = "translateLocally -m fr-en-tiny -i {} -o {}".format(path_in, path_out)
    subprocess.run(command, shell=True, executable="/bin/bash")
    if not pathfuncs.check_path(path_out):
        print("FAILED TO CREATE {}".format(path_out))


# Put the translations into a csv file for checking against DeepL translations.
def check():

    with open(path_out, "r") as f:
        l = list(f.readlines())
    dfen = pd.DataFrame(columns=["en"], data=l)
    logger.debug(dfen)
    df = _pd_from_db()
    df["translation"] = dfen.en.str.strip()
    logger.debug(df)
    df.to_csv(
        pathfuncs.OUT_DIR + "/ords_problem_translations_locally_fr2en.csv", index=False
    )


def do_all():
    file_in()
    translate()
    check()
    exit()


def get_options():
    return {
        0: "exit()",
        1: "file_in()",
        2: "translate()",
        3: "check()",
        4: "do_all()",
    }


if __name__ == "__main__":

    logger = logfuncs.init_logger(__file__)

    path_in = pathfuncs.OUT_DIR + "/ords_problem_translations_locally_fr.txt"
    path_out = pathfuncs.OUT_DIR + "/ords_problem_translations_locally_en.txt"

    exec_opt(get_options())
