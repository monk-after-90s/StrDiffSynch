from unittest import TestCase
from string import printable
from random import sample

from StrDiffSynch import StrDiff


class StrDiffSyncTest(TestCase):
    def setUp(self) -> None:
        self.initial_str = ''.join([sample(printable, 1)[0] for _ in range(1000)])
        print(self.initial_str)

    def test_repeatly_change_a_string_then_synch_its_copy(self):
        a = self.initial_str
        b = a
        for _ in range(1000):
            # 随机更改a中的300字符
            a = list(a)
            for random_index in sample(range(1000), 300):
                a[random_index] = sample(printable, 1)[0]
            a = ''.join(a)

            # 计算差异
            diff = StrDiff(b, a)
            # 同步
            self.assertEqual(a, b + diff)

    def test_create_strdiff_from_metadata(self):
        metadata = (
            ('d', 38, 39, None),
            ('i', 19, 29, 'ewr'),  # insert
            ('r', 19, 29, 'rewr'),  # replace
            ('h', '7dd2bf72f19411ad72e04708f6055fd3b7dd9ab45943b2e71a3d34ac5a4cc2bf',
             '43ca572d0bbad16c017baf1700c8ed12dcfdcfe936bc014b3bcdb522ab5e1a37')
        )
        StrDiff.create_str_diff_from_metadata(metadata)

        with self.assertRaises(ValueError) as cm:
            StrDiff.create_str_diff_from_metadata((
                ('d', 38, 39, None),
                ('i', 19, 29, 'ewr'),  # insert
                ('j', 19, 29, 'rewr'),  # replace
                ('h', '7dd2bf72f19411ad72e04708f6055fd3b7dd9ab45943b2e71a3d34ac5a4cc2bf',
                 '43ca572d0bbad16c017baf1700c8ed12dcfdcfe936bc014b3bcdb522ab5e1a37')
            ))
        self.assertEqual(str(cm.exception), 'Illegal metadata.')

        with self.assertRaises(ValueError) as cm:
            StrDiff.create_str_diff_from_metadata((
                ('d', 38, 39, None),
                ('i', 19, 29, 'ewr'),  # insert
                ('r', 19, 29, 'rewr'),  # replace
                ('o', '7dd2bf72f19411ad72e04708f6055fd3b7dd9ab45943b2e71a3d34ac5a4cc2bf',
                 '43ca572d0bbad16c017baf1700c8ed12dcfdcfe936bc014b3bcdb522ab5e1a37')
            ))
        self.assertEqual(str(cm.exception), 'Illegal metadata.')

        with self.assertRaises(ValueError) as cm:
            StrDiff.create_str_diff_from_metadata((
                ('d', 38, 39, None),
                ('i', 19, 29, 'ewr'),  # insert
                ('r', 19, 29, 'rewr'),  # replace
                ('h', 123,
                 '43ca572d0bbad16c017baf1700c8ed12dcfdcfe936bc014b3bcdb522ab5e1a37')
            ))
        self.assertEqual(str(cm.exception), 'Illegal metadata.')
