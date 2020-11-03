import asyncio
import hashlib
from functools import lru_cache

from StrDiffSynch import StrDiff

from StrDiffSynch.LRUCache import LRUCache
import platform


@lru_cache(maxsize=128, typed=False)
def get_hash(s: str):
    return hashlib.sha256(s.encode()).hexdigest()


class StrHash:
    def __init__(self, s: str):
        self.string = s

    def __str__(self):
        return self.string

    @property
    def string(self):
        return self._string

    @string.setter
    def string(self, s: str):
        self._string = s
        self.hash = get_hash(s)

    def __bool__(self):
        return bool(self._string)


class SynchBox:
    def __init__(self, s: str):
        self._local_str = StrHash(s)
        self._remote_str_history = LRUCache(20)
        self._remote_str_history.put(self._local_str.hash, str(self._local_str))

    def handle_remote_synch_command(self, remote_hash: str):
        '''

        :param remote_hash:
        :return: Increment tuple or full data string.
        '''
        try:
            local_remote_str = self._remote_str_history.get(remote_hash)
            # 找到本级缓存的远程数据，增量同步
            if local_remote_str is not None:
                diff = StrDiff(local_remote_str, str(self._local_str))
                return diff.metadata
            else:  # 完整同步
                return str(self._local_str)
        finally:
            self._remote_str_history.put(self._local_str.hash, str(self._local_str))

    def handle_local_synch_command(self, remote_msg, strdiff_add_error_handler=None):
        '''
        :param remote_msg: full remote string or StrDiff metadata--a sequence.
        :param strdiff_add_error_handler: function to be called when the remote StrDiff instance can't be added to self._local_str.string, to force to fetch the full data.Otherwise, an AssertionError would be raised.
        :return: None means the synchronization completed. Otherwise a asyncio.Task instance means that synchronization completes only if the task is awaited.
        '''
        try:
            diff = StrDiff.create_str_diff_from_metadata(remote_msg)
        except ValueError:  # 非差异对象，而是完整配置
            self._local_str.string = str(remote_msg)
        else:  # 差异对象
            try:
                self._local_str.string += diff
            except AssertionError:  # 无法合成
                if strdiff_add_error_handler is not None:
                    strdiff_add_error_handler_res = strdiff_add_error_handler()
                    if asyncio.iscoroutine(strdiff_add_error_handler_res):
                        async def await_remote_full_data_then_handle_local_synch_command():
                            remote_full_data = await strdiff_add_error_handler_res
                            self.handle_local_synch_command(remote_full_data)

                        if platform.python_version() >= '3.7.0':
                            return asyncio.create_task(await_remote_full_data_then_handle_local_synch_command())
                        else:
                            return asyncio.ensure_future(await_remote_full_data_then_handle_local_synch_command())
                    else:
                        self.handle_local_synch_command(strdiff_add_error_handler_res)
                else:
                    raise

        finally:
            self._remote_str_history.put(self._local_str.hash, str(self._local_str))

    @property
    def local_str(self):
        return str(self._local_str)

    @local_str.setter
    def local_str(self, s: str):
        self._local_str.string = s

    @property
    def local_str_hash(self):
        return self._local_str.hash


if __name__ == '__main__':
    sh = StrHash('')
    print()
