import asyncio
import hashlib
from functools import lru_cache

from StrDiffSynch import StrDiff
from copy import deepcopy


class StrHash:
    def __init__(self, s: str, endpoint_method, endpoint_url):
        self.string = s
        self.endpoint = (endpoint_method, endpoint_url)

    def __str__(self):
        return self.string

    @property
    def string(self):
        return self._string

    @string.setter
    def string(self, s: str):
        self._string = s
        self.hash = self._get_hash(s)

    @lru_cache(maxsize=128, typed=False)
    def _get_hash(self, s: str):
        return hashlib.sha256(s.encode()).hexdigest()

    def __bool__(self):
        return bool(self._string)

    @property
    def endpoint(self):
        return self._endpoint

    @endpoint.setter
    def endpoint(self, method='GET', url=''):
        self._endpoint = (method, url)


class SynchBox:
    def __init__(self, remote_endpoint_method, remote_endpoint_url):
        self._local_str = StrHash('', '', '')
        self._remote_str = StrHash('', remote_endpoint_method, remote_endpoint_url)
        self._remote_full_data_function = None
        self._remote_increment_method = None

    def get_remote_full_data_method(self, func):
        self._remote_full_data_function = func

    def get_remote_increment_method(self, func):
        self._remote_increment_method = func

    def force_update_local(self):
        pass

    def _get_remote_data(self, full=False):
        pass

    def handle_remote_synch_request(self, remote_hash: str):
        '''

        :param remote_hash:
        :return: Increment tuple or full data string.
        '''
        try:
            # 增量同步
            if remote_hash == self._remote_str.hash:
                diff = StrDiff(str(self._remote_str), str(self._local_str))
                return diff.metadata
            else:  # 完整同步
                return str(self._local_str)
        finally:
            self._remote_str = deepcopy(self._local_str)

    def handle_local_synch_request(self, remote_msg, strdiff_add_error_handler=None):
        '''
        :param remote_msg: full remote string or StrDiff metadata--a sequence.
        :param strdiff_add_error_handler: function to be called when the remote StrDiff instance can't be added to self._local_str.string, to force to fetch the full data.
        :return: None表示同步完成，若是asyncio.Task实例，则需要等待完成才同步完成
        '''
        try:
            diff = StrDiff.create_str_diff_from_metadata(remote_msg)
        except ValueError:  # 非差异对象，而是完整配置
            self._local_str.string = str(remote_msg)
        else:  # 差异对象
            try:
                self._local_str.string += diff
            except AssertionError:  # 无法合成
                strdiff_add_error_handler_res = strdiff_add_error_handler()
                if asyncio.iscoroutine(strdiff_add_error_handler_res):
                    async def await_remote_full_data_then_handle_local_synch_request():
                        remote_full_data = await strdiff_add_error_handler_res
                        self.handle_local_synch_request(remote_full_data)

                    return asyncio.create_task(await_remote_full_data_then_handle_local_synch_request())
                else:
                    self.handle_local_synch_request(strdiff_add_error_handler_res)

        finally:
            self._remote_str = deepcopy(self._local_str)

    @property
    def local_str(self):
        return self._local_str

    @local_str.setter
    def local_str(self, s: str):
        self._local_str.string = s


if __name__ == '__main__':
    sh = StrHash('')
    print()
