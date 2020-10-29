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
