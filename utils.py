import re


def parse_numbers(csv_string: str):
    numbers = re.split(r"[,.]", csv_string)
    output = []

    for number in numbers:
        # Remove any white space at the start and end
        num = number.strip()
        # Remove any other characters ie "(OL)" in "19-21 (OL)"
        # Only returns a list of digits and - symbol
        num = re.findall(r"[\d-]", num)
        # Join list back into string
        num = "".join(num)

        if num == "":
            pass
        elif "-" in num:
            expanded_numbers = expand_number_range(num)
            output.extend(expanded_numbers)
        else:
            n = int(num)
            output.append(n)

    return output


def expand_number_range(ran: str):
    ends = ran.split(sep="-")
    start, end = ends

    start = int(start.strip())
    end = int(end.strip())

    numbers = list(range(start, end + 1))
    return numbers


def add_leading_zero(val: str | int | float) -> str:
    return f"{val:0>2}"


def sort_dict(dct):
    keys = list(dct.keys())
    keys.sort()

    sorted_dict = {}

    for key in keys:
        sorted_dict[key] = dct[key]

    return sorted_dict
