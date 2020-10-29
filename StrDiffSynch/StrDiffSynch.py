import difflib


class StrDiff:
    def __init__(self, from_str: str, to_str: str):
        from_str = list(from_str)
        to_str = list(to_str)
        matcher = []
        for tag, i1, i2, j1, j2 in reversed(difflib.SequenceMatcher(None, from_str, to_str).get_opcodes()):
            if tag == 'delete':
                # del from_str[i1:i2]
                matcher.append((tag, i1, i2, None))
            elif tag == 'equal':
                pass
            elif tag == 'insert':
                # from_str[i1:i2] = to_str[j1:j2]
                matcher.append((tag, i1, i2, to_str[j1:j2]))
            elif tag == 'replace':
                # from_str[i1:i2] = to_str[j1:j2]
                matcher.append((tag, i1, i2, to_str[j1:j2]))
        self._matcher = matcher

    def __add__(self, from_str: str):
        assert type(from_str) == str
        from_str = list(from_str)
        for tag, i1, i2, diff_str in self._matcher:
            if tag == 'delete':
                del from_str[i1:i2]
            elif tag == 'equal':
                pass
            elif tag == 'insert':
                from_str[i1:i2] = diff_str

            elif tag == 'replace':
                from_str[i1:i2] = diff_str
        to_str = ''.join(from_str)
        return to_str

    def __radd__(self, other: str):
        return self.__add__(other)


if __name__ == '__main__':
    import json

    data1 = {"name": "davis", "other": {"age": 18}}
    data2 = {"name": "davis", "age": 18}
    diff = StrDiff(json.dumps(data1), json.dumps(data2))
    print(json.loads(json.dumps(data1) + diff) == data2)
