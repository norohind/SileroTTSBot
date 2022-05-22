from typing import Iterable


class MISSING:
    pass


def format_table(data: Iterable[Iterable[str]], header: Iterable[str] = MISSING) -> str:
    if header != MISSING:
        data = (header, *data)

    result = '```\n'
    for row in data:
        row = [item.replace('`', '\\`') for item in row]
        result += '\t'.join(row) + '\n'

    result += '```'
    return result
