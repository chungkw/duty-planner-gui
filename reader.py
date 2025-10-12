import re

from utils import parse_numbers

# Regex is way better and more reliable than simply matching the start of a string
# This will capture key inputs from the template
DATA_REGEX = r"^(Name|PC|MA|Army Reason \(.+\)|Offs|Leaves|Requests):(.*)"


def ingest_dates(text_input):
    person = {}
    results: list[tuple[str, str]] = re.findall(
        DATA_REGEX, text_input, flags=re.MULTILINE
    )

    for category, user_input in results:
        if category == "Name":
            person["name"] = user_input.strip()

        if category == "PC":
            dates = parse_numbers(user_input)
            person["pc"] = dates

        if category == "MA":
            dates = parse_numbers(user_input)
            person["ma"] = dates

        if category.startswith("Army Reason"):
            dates = parse_numbers(user_input)
            person["ar"] = dates

        if category == "Offs":
            dates = parse_numbers(user_input)
            person["offs"] = dates

        if category == "Leaves":
            dates = parse_numbers(user_input)
            person["leaves"] = dates

        if category == "Requests":
            dates = parse_numbers(user_input)
            person["requests"] = dates

    return person
