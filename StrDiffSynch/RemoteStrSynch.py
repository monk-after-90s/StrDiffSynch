import hashlib
from functools import lru_cache

from StrDiffSynch import StrDiff


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

    def handle_remote_synch_request(self, remote_msg: dict):
        '''

        :param remote_msg:like {'remote_hash':'hfewhfyr89yrq398rhufy932q8ryf9'}
        :return: Increment tuple or full data string.
        '''
        # 增量同步
        if remote_msg['remote_hash'] == self._remote_str.hash:
            diff = StrDiff(str(self._remote_str), str(self._local_str))
            return diff.metadata
        else:  # 完整同步
            return str(self._local_str)


if __name__ == '__main__':
    sh = StrHash('')
    print()
