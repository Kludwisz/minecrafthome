#!/usr/bin/env python
from assimilator import *
from Boinc import boinc_project_path
import re, os

class panoPaleAssimilator(Assimilator):
        def __init__(self):
                Assimilator.__init__(self)

        def assimilate_handler(self, wu, results, canonical_result):
                try:
                    if canonical_result == None:
                            return

                    path = boinc_project_path.project_path("panopale_results")
                    input_path = self.get_file_path(canonical_result)

                    with open(input_path) as input_file:
                        input_str = input_file.read()

                    try:
                        os.makedirs(path)
                    except OSError:
                        pass

                    lines = set()
                    with open(os.path.join(path, "results.txt"), "a") as f:
                        for line in input_str.splitlines():
                            # only assimilate actual results, lines that begin with ##
                            # contain the prng checksum used in the validation step
                            if "##" not in line:
                                lines.add(line) 
                        for line in lines:
                            f.write("{}\n".format(line))
                except Exception as e: print(e)

if __name__ == "__main__":
        asm = panoPaleAssimilator()
        asm.run()