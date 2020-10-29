import difflib


class StrDiff:
    @classmethod
    def create_str_diff_from_metadata(cls, metadata: tuple):
        '''
        Create a StrDiff instance from a meta data.

        :param metadata:Like:
        [
        ('d', 38, 39, None),
        ('d', 19, 29, None),
        ('h', '7dd2bf72f19411ad72e04708f6055fd3b7dd9ab45943b2e71a3d34ac5a4cc2bf', '43ca572d0bbad16c017baf1700c8ed12dcfdcfe936bc014b3bcdb522ab5e1a37')
        ]
        :return:
        '''
        new = StrDiff('', '')
        new.metadata = metadata
        return new

    def __init__(self, from_str: str, to_str: str):
        matcher = []
        for tag, i1, i2, j1, j2 in reversed(difflib.SequenceMatcher(None, from_str, to_str).get_opcodes()):
            if tag == 'delete':
                # del from_str[i1:i2]
                matcher.append(('d', i1, i2, None))
            elif tag == 'equal':
                pass
            elif tag == 'insert':
                # from_str[i1:i2] = to_str[j1:j2]
                matcher.append(('i', i1, i2, to_str[j1:j2]))
            elif tag == 'replace':
                # from_str[i1:i2] = to_str[j1:j2]
                matcher.append(('r', i1, i2, to_str[j1:j2]))
        self.metadata = tuple(matcher)

    def __add__(self, from_str: str):
        assert type(from_str) == str
        from_str = list(from_str)
        for tag, i1, i2, diff_str in self.metadata:
            if tag == 'd':
                del from_str[i1:i2]
            elif tag == 'i':
                from_str[i1:i2] = diff_str

            elif tag == 'r':
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
