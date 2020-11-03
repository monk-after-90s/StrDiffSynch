import difflib
import hashlib
from functools import lru_cache


@lru_cache(maxsize=128, typed=False)
def get_opcodes(from_str: str, to_str: str):
    return difflib.SequenceMatcher(None, from_str, to_str).get_opcodes()[::-1]


class StrDiff:
    @classmethod
    def create_str_diff_from_metadata(cls, metadata: tuple):
        '''
        Create a StrDiff instance from a meta data.

        :param metadata:Like:
        (
        ('d', 38, 39, None),
        ('i', 19, 29, 'ewr'),#insert
        ('r', 19, 29, 'rewr'),#replace
        ('h', '7dd2bf72f19411ad72e04708f6055fd3b7dd9ab45943b2e71a3d34ac5a4cc2bf', '43ca572d0bbad16c017baf1700c8ed12dcfdcfe936bc014b3bcdb522ab5e1a37')#hash values of the initial string and target string
        )
        :return:
        '''
        try:
            new = StrDiff('', '')
            if all([op_item[0] in 'dirh' for op_item in metadata]) and \
                    any([op_item[0] == 'h' and type(op_item[1]) == str and type(op_item[2]) == str
                         for op_item in metadata]):
                new.metadata = metadata
                return new
            else:
                raise ValueError('Illegal metadata.')
        except:
            raise ValueError('Illegal metadata.')

    def __init__(self, from_str: str, to_str: str):
        from_str_hash = hashlib.sha256(from_str.encode()).hexdigest()
        to_str_hash = hashlib.sha256(to_str.encode()).hexdigest()
        matcher = []
        for tag, i1, i2, j1, j2 in get_opcodes(from_str, to_str):
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
        matcher.append(('h', from_str_hash, to_str_hash, None))
        self.metadata = tuple(matcher)

    def __add__(self, from_str: str):
        assert type(from_str) == str
        try:
            assert self.metadata[-1][1] == hashlib.sha256(from_str.encode()).hexdigest()
        except AssertionError:
            raise AssertionError('Wrong string adds StrDiff.')
        from_str = list(from_str)
        for tag, i1, i2, diff_str in self.metadata:
            if tag == 'd':
                del from_str[i1:i2]
            elif tag == 'i':
                from_str[i1:i2] = diff_str

            elif tag == 'r':
                from_str[i1:i2] = diff_str
        to_str = ''.join(from_str)
        try:
            assert self.metadata[-1][2] == hashlib.sha256(to_str.encode()).hexdigest()
        except AssertionError:
            raise AssertionError('Wrong string adds StrDiff.')

        return to_str

    def __radd__(self, other: str):
        return self.__add__(other)


if __name__ == '__main__':
    import json

    data1 = json.dumps({"name": "davis", "other": {"age": 18}})
    data2 = json.dumps({"name": "davis", "age": 18})
    diff = StrDiff(data1, data2)
    print(data1 + diff == data2)
