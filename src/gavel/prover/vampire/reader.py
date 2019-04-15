import re

proof_line_regex = re.compile(r"^\d+\. .* \[(?:input (?P<input>.*)|(.*))\]$")


def read_proof(path):
    with open(path, "r") as f:
        for line in f.readlines():
            if line[0] not in ["%", "\n"]:
                match = re.match(proof_line_regex, line)
                if match:
                    inp = match.groupdict().get("input")
                    if inp is not None:
                        print(inp)
                else:
                    raise Exception("Not matched:" + line)
