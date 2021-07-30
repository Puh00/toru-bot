EDGE = "+"
V_BAR = "| "
H_BAR = "-"

"""
EXAMPLE_TABLE_DATA = [
    ["Company", "Contact", "Country"],
    ["Alfreds Futterkiste", "Maria Anders", "Germany"],
    ["Centro comercial Moctezuma", "Francisco Chang", "Mexico"],
    ["Ernst Handel", "Roland Mendel", "Austria"],
    ["Laughing Bacchus Winecellars", "Yoshi Tannamuri", "Canada"],
    ["Magazzini Alimentari Riuniti", "Giovanni Rovelli", "Italy"],
]
"""

def _lengthOfLongestWordInColumn(row: int, data: list[list[str]]) -> int:
    length = -1
    for col in data:
        current = len(col[row])
        if current > length:
            length = current
    return length


def _separator(wordLengths: list[int]) -> str:
    table = EDGE
    for num in wordLengths:
        table += H_BAR * (num + 2)
        table += EDGE
    return table + "\n"


def _row(wordLengths: list[int], row: int) -> str:
    r = V_BAR
    for i in range(len(row)):
        diff = wordLengths[i] - len(row[i])
        spaces = diff + 1 if diff > 0 else 1
        r += row[i] + " " * spaces + V_BAR
    return r + "\n"


def _header(wordLengths: list[int], data: list[list[str]]) -> str:
    table = _separator(wordLengths)
    table += _row(wordLengths, data[0])
    table += _separator(wordLengths)
    return table


def _body(wordLengths, data: list[list[str]]) -> str:
    table = ""
    for i in range(1, len(data)):
        table += _row(wordLengths, data[i])
    table += _separator(wordLengths)
    return table

def generateTable(data: list[list[str]]) -> str:
    wordLengths = []
    # Get length of longest word in each column
    for i in range(len(data[0])):
        wordLengths.append(_lengthOfLongestWordInColumn(i, data))

    table = "\n"+_header(wordLengths, data)
    table += _body(wordLengths, data)

    return table
