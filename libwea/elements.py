#
# WeaBase elements and unit conversions.
#

from ..settings import ELEMENTS_FILE, WEA_ELEMENTS_FILE, WEA_ELEMENTS2_FILE

# Define display formats
DEFAULT_FORMAT = "%f"
FORMATS = {
    1: "%.2f",
    2: "%.0f",
    3: "%.1f",
    4: "%.0f",
    5: "%.1f",
    6: "%.0f",
    7: "%.3f",
    8: "%.2f",
    9: "%.0f",
    10: "%.3f",
}

WeaElements = {}
elements_file = open(ELEMENTS_FILE, 'r')
header = elements_file.readline()
for line in [l.strip() for l in elements_file.readlines()]:
    pcode, name, scale_max, scale_min, unused, fmt = [i.strip() for i in line.split(',')]
    name = name[1:-1].strip()  # remove " surround name
    elem = {
        "name": name,
        "scaling_max": float(scale_max),
        "scaling_min": float(scale_min)
    }

    # Determine display format
    try:
        elem["format"] = FORMATS[int(fmt)]
    except KeyError:
        elem["format"] = DEFAULT_FORMAT

    WeaElements[pcode] = elem
elements_file.close()


# Supplement WeaElements with info from wea_elements.dat
wea_elements_file = open(WEA_ELEMENTS_FILE, 'r')
header = wea_elements_file.readline()
for line in [l.strip() for l in wea_elements_file.readlines()]:
    try:
        pcode, units, desc1, desc2, desc_long = line.split(',')
    except ValueError:
        continue
    pcode = pcode.strip()
    if not pcode in WeaElements:
        WeaElements[pcode] = {}  # noqa
    WeaElements[pcode].update({
        "units": units.strip(),
        "name": desc_long
    })
wea_elements_file.close()


Conversions = {}
wea_elements2_file = open(WEA_ELEMENTS2_FILE, 'r')
header = wea_elements2_file.readline()
for line in [l.strip() for l in wea_elements2_file.readlines()]:
    system, units1, units2, multiplier, offset = line.split(',')
    # Convert units1 to system by muliplying multiplier and adding
    # offset, resulting in units2
    Conversions[(units1.strip(), system.strip())] = (float(multiplier), float(offset), units2.strip())
wea_elements2_file.close()


"""
# These are used for the ingest process. Not sure if needed here.
WeaConvert = {}
elemunits_file = open(ELEMUNITS_FILE, 'r')
# First read available units
header = elemunits_file.readline()
n1 = int(elemunits_file.readline().strip())
for i in range(n1):
    _ = elemunits_file.readline()
# Next, read conversions
header = elemunits_file.readline()
n2 = int(elemunits_file.readline().strip())
for i in range(n2):
    line = elemunits_file.readline().strip()
    name, multiplier, offset = line.split(',')
    names = name.split("\xaf", 1)
    name1 = names[0].replace('"','').strip()
    if len(names) > 1:
        name2 = names[1].replace('"','').strip()
    else:
        name2 = ""

    WeaConvert[i] = {
        "in_unit": name1,
        "out_unit": name2,
        "multiplier": float(multiplier),
        "offset": float(offset)
    }
elemunits_file.close()
"""

# Only allow the import of objects listed here:
__all__ = (
    'WeaElements', 'Conversions', 'DEFAULT_FORMAT'
)
