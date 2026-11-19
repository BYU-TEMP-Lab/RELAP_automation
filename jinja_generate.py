"""Convert RELAP template lines into Jinja format strings for use in generating RELAP input files.

This script provides functionality to convert lines from a RELAP input template into Jinja format strings.
The main function, `get_jinja`, takes a header string, a value string, and a RELAP object number, and 
generates a Jinja format string that can be used to populate the template with values from a parameter 
dictionary. The script also includes a command-line interface for interactive use, allowing users to 
input RELAP object numbers, parameter names, and values, and receive the corresponding Jinja format strings.
"""

__author__ = "Samuel Nasman"
__version__ = "1.0"
__status__ = "Complete"

import sys

def get_jinja(header_str, val_str, num_str):
    params = header_str.split()

    vals = []
    widths = []
    val = ""
    width = 0
    mode = "val"

    for i in range(len(val_str)):
        char = val_str[i]

        if mode == "val":
            if char != " ":
                val += char
                width += 1
            else:
                vals.append(val)
                val = ""
                mode = "space"
                width += 1
        elif mode == "space":
            if char == " ":
                width += 1
            else:
                widths.append(width)
                width = 1
                val += char
                mode = "val"

        if i == len(val_str) - 1 and mode == "val":
            vals.append(val)
            widths.append(width)
        elif i == len(val_str) - 1 and mode == "space":
            widths.append(width)

    print(params)
    print(vals)
    print(widths)
    if not len(vals) == len(params) and not len(widths) == len(params):
        raise ValueError("Number of values/widths does not match number of parameters")

    final_str = ""
    for param, val, width in zip(params, vals, widths):

        if "e" in val.lower():
            exp_char = "e" if "e" in val else "E"
            mantissa = val.lower().split("e")[0]
            precision = len(mantissa.split(".")[1]) if "." in mantissa else 0
            format_str = f"{{{{ c{num_str}.{param} | relap_sci({width}, {precision}, '{exp_char}') }}}}"

        elif "." in val:
            precision = len(val.split(".")[1]) if "." in val else 0
            format_str = f"{{{{ \"%-{width}.{precision}f\" | format(c{num_str}.{param})}}}}"

        else:
            try:
                num_width = len(val)
                val = int(val)
                format_str = f"{{{{ \"%-{width}s\" | format( \"%0{num_width}d\" | format(c{num_str}.{param}) ) }}}}"
            except ValueError:
                format_str = f"{{{{ \"%-{width}s\" | format(c{num_str}.{param} ) }}}}"

        print("\nJinja format string:")
        final_str += format_str

    print(final_str)

if __name__ == "__main__":

    num = ""

    while True:

        if num != "":
            print(f"\nCurrent RELAP object number: {num}")
            print("Change? (y/N):")
            change = input()
            if change.lower() == "y":
                num = ""

        if num == "":
            print("Input RELAP object number (1st 3 or 4 digits typically):")
            num = input()
            if len(num) < 3 or len(num) > 4:
                raise ValueError("Input object number must be 3 or 4 digits")

        print("\nInput parameter variable name(s) (separated by at least 1 space):")
        header = input()

        print("\nInput parameter values in the proper format (include trailing whitespace):")
        vals = input()

        get_jinja(header, vals, num)

        print("\nContinue? (Y/n):")
        cont = input()
        if cont.lower() == "n":
            break
    