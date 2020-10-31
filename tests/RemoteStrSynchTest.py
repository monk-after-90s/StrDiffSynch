from copy import deepcopy
from random import sample, randrange
from string import printable
from unittest import TestCase

from StrDiffSynch import SynchBox, StrDiff
import asyncio


class RemoteStrSynchTest(TestCase):
    '''
    全部测试，不要单个测试。不能保证一定通过测试，多测试几次，大部分都能测试通过。
    '''
    box2_history = []

    @classmethod
    def setUpClass(cls) -> None:
        cls.synch_box1 = SynchBox(''.join([sample(printable, 1)[0] for _ in range(1000)]))
        cls.synch_box2 = SynchBox('')

    def test_1_handle_remote_synch_request_and_handle_local_synch_request_intial_synch(self):
        remote_synch_data = self.synch_box1.handle_remote_synch_request(self.synch_box2.local_str_hash)
        self.assertEqual(str, type(remote_synch_data))
        with self.assertRaisesRegex(ValueError, 'Illegal metadata.'):
            StrDiff.create_str_diff_from_metadata(remote_synch_data)

        self.synch_box2.handle_local_synch_request(remote_synch_data)
        self.assertEqual(self.synch_box1.local_str, self.synch_box2.local_str)
        self.box2_history.append(deepcopy(self.synch_box2._local_str))

    def test_2_increment_asynch(self):
        # 随机更改300字符
        a = list(self.synch_box1.local_str)
        for random_index in sample(range(1000), 300):
            a[random_index] = sample(printable, 1)[0]
        self.synch_box1.local_str = ''.join(a)
        remote_synch_data = self.synch_box1.handle_remote_synch_request(self.synch_box2.local_str_hash)
        self.assertEqual(tuple, type(remote_synch_data))
        StrDiff.create_str_diff_from_metadata(remote_synch_data)
        self.synch_box2.handle_local_synch_request(remote_synch_data)
        self.assertEqual(self.synch_box1.local_str, self.synch_box2.local_str)
        self.box2_history.append(deepcopy(self.synch_box2._local_str))

    def test_3_remote_hash_str_history(self):
        # 从历史获取增量，无法跟现在的数据合并
        remote_synch_data = self.synch_box1.handle_remote_synch_request(self.box2_history[0].hash)
        self.assertEqual(tuple, type(remote_synch_data))
        StrDiff.create_str_diff_from_metadata(remote_synch_data)
        with self.assertRaisesRegex(AssertionError, 'Wrong string.'):
            self.synch_box2.handle_local_synch_request(remote_synch_data)

        # 从现在的数据获取增量，可以跟现在的数据合并
        remote_synch_data = self.synch_box1.handle_remote_synch_request(self.box2_history[-1].hash)
        self.assertEqual(tuple, type(remote_synch_data))
        StrDiff.create_str_diff_from_metadata(remote_synch_data)
        self.synch_box2.handle_local_synch_request(remote_synch_data)
        self.assertEqual(self.synch_box1.local_str, self.synch_box2.local_str)

    def test_4_accurate_increment(self):
        # 不变更新
        remote_synch_data = self.synch_box1.handle_remote_synch_request(self.synch_box2.local_str_hash)
        self.assertEqual(tuple, type(remote_synch_data))
        self.assertEqual(len(remote_synch_data), 1)
        self.assertEqual(remote_synch_data[0][0], 'h')

        # 随机删除一个字符
        a = list(self.synch_box1.local_str)
        rand_index = randrange(len(a))
        a.pop(rand_index)
        self.synch_box1.local_str = ''.join(a)
        remote_synch_data = self.synch_box1.handle_remote_synch_request(self.synch_box2.local_str_hash)
        self.assertEqual(tuple, type(remote_synch_data))
        self.assertEqual(len(remote_synch_data), 2)
        self.assertEqual(remote_synch_data[0][0], 'd')
        self.assertEqual(remote_synch_data[0][1], rand_index)
        self.assertEqual(remote_synch_data[0][2], rand_index + 1)
        StrDiff.create_str_diff_from_metadata(remote_synch_data)
        self.synch_box2.handle_local_synch_request(remote_synch_data)
        self.assertEqual(self.synch_box1.local_str, self.synch_box2.local_str)
        # 随机在一个位置插入几个字符
        a = list(self.synch_box1.local_str)
        rand_index = randrange(len(a))
        a.insert(rand_index, 'dfjhoeu283')
        self.synch_box1.local_str = ''.join(a)
        remote_synch_data = self.synch_box1.handle_remote_synch_request(self.synch_box2.local_str_hash)
        self.assertEqual(tuple, type(remote_synch_data))
        self.assertEqual(remote_synch_data[0][0], 'i')
        self.assertEqual(remote_synch_data[0][1], rand_index)
        self.assertEqual(remote_synch_data[0][2], rand_index)
        self.assertEqual(remote_synch_data[0][3], 'dfjhoeu283')
        StrDiff.create_str_diff_from_metadata(remote_synch_data)
        self.synch_box2.handle_local_synch_request(remote_synch_data)
        self.assertEqual(self.synch_box1.local_str, self.synch_box2.local_str)

        # 随机在一个位置更换几个字符
        a = list(self.synch_box1.local_str)
        rand_index = randrange(len(a))
        end_index = rand_index + 5
        end_index = end_index if end_index < len(a) else len(a) - 1
        a[rand_index:end_index] = ['测试']
        self.synch_box1.local_str = ''.join(a)
        remote_synch_data = self.synch_box1.handle_remote_synch_request(self.synch_box2.local_str_hash)
        self.assertEqual(tuple, type(remote_synch_data))
        self.assertEqual(remote_synch_data[0][0], 'r')
        self.assertEqual(remote_synch_data[0][1], rand_index)
        self.assertEqual(remote_synch_data[0][2], end_index)
        self.assertEqual(remote_synch_data[0][3], '测试')
        StrDiff.create_str_diff_from_metadata(remote_synch_data)
        self.synch_box2.handle_local_synch_request(remote_synch_data)
        self.assertEqual(self.synch_box1.local_str, self.synch_box2.local_str)

    def test_5_strdiff_add_error_handler(self):
        async def test_5_strdiff_add_error_handler():
            # 故意使用老的哈希值请求差异值
            remote_synch_data = self.synch_box1.handle_remote_synch_request(self.box2_history[0].hash)
            self.assertEqual(tuple, type(remote_synch_data))
            StrDiff.create_str_diff_from_metadata(remote_synch_data)
            with self.assertRaisesRegex(AssertionError, 'Wrong string.'):
                self.synch_box2.handle_local_synch_request(remote_synch_data)

            # 传入强制获取完整数据的方法
            def strdiff_add_error_handler():
                return self.synch_box1.local_str

            self.synch_box2.handle_local_synch_request(remote_synch_data, strdiff_add_error_handler)
            self.assertEqual(self.synch_box1.local_str, self.synch_box2.local_str)

            # 传入异步函数重做一遍

            # 故意使用老的哈希值请求差异值
            remote_synch_data = self.synch_box1.handle_remote_synch_request(self.box2_history[0].hash)
            self.assertEqual(tuple, type(remote_synch_data))
            StrDiff.create_str_diff_from_metadata(remote_synch_data)
            with self.assertRaisesRegex(AssertionError, 'Wrong string.'):
                self.synch_box2.handle_local_synch_request(remote_synch_data)

            # 传入强制获取完整数据的方法
            async def strdiff_add_error_handler():
                return self.synch_box1.local_str

            await self.synch_box2.handle_local_synch_request(remote_synch_data, strdiff_add_error_handler)
            self.assertEqual(self.synch_box1.local_str, self.synch_box2.local_str)

        asyncio.get_event_loop().run_until_complete(test_5_strdiff_add_error_handler())
