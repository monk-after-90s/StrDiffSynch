# StrDiff
One of two strings can change into the other when absorbing the difference among them. 
```python
import json
from StrDiffSynch import StrDiff

data1 = json.dumps({"name": "davis", "other": {"age": 18}})
data2 = json.dumps({"name": "davis", "age": 18})
diff = StrDiff(data1, data2)
assert data1 + diff == data2
assert diff + data1 == data2
```
# SynchBox
This class is used for synchronizing big string but not big enough to have to be stored in a database, 
among two endpoints.
```python
import asyncio

from StrDiffSynch import SynchBox

# LOCAL
# Define a SynchBox instance to contain the string
synch_box = SynchBox('This is big data.')
# update the containing string
synch_box.local_str = 'This is another big data.'
# If a request with the remote string hash value comes to ask to synchronize the string at the remote endpoint, local endpoint handles the request.
# REMOTE
synch_box2 = SynchBox('')
remote_str_hash = synch_box2.local_str_hash
# request though the web
# LOCAL
remote_synch_data = synch_box.handle_remote_synch_command(remote_str_hash)
# response through the web
# REMOTE
# Because no synchronization has happened, remote_synch_data would be the raw big string, 'This is another big data.' as demonstration.
synch_box2.handle_local_synch_command(remote_synch_data)
assert 'This is another big data.' == remote_synch_data == synch_box2.local_str

# Now repeat
# REMOTE
remote_str_hash = synch_box2.local_str_hash
# request though the web
# LOCAL
remote_synch_data = synch_box.handle_remote_synch_command(remote_str_hash)
# response through the web
# REMOTE
# Well now that initial synchronization has happened, SynchBox will try to find the difference information between these two copy , which is usually much smaller than the raw string.
assert type(remote_synch_data) != str and any(['h' == i[0] for i in remote_synch_data])
synch_box2.handle_local_synch_command(remote_synch_data)  # At this step,there is nothing to change in fact.
assert synch_box2.local_str == synch_box.local_str

# Now repeat
# LOCAL
# make some change
synch_box.local_str += 'u28dy2'
# REMOTE
remote_str_hash = synch_box2.local_str_hash
# request though the web
# LOCAL
remote_synch_data = synch_box.handle_remote_synch_command(remote_str_hash)
# response through the web
# REMOTE
assert type(remote_synch_data) != str and any(['h' == i[0] for i in remote_synch_data])
old_str = synch_box2.local_str
synch_box2.handle_local_synch_command(remote_synch_data)  # At this step,changes happen.
assert synch_box2.local_str == synch_box.local_str != old_str

# Now repeat
# Vice versa, REMOTE could synchronizes LOCAL.
# REMOTE
# make some change
synch_box2.local_str = synch_box2.local_str[0:3] + synch_box2.local_str[-3:]
# LOCAL
str_hash = synch_box.local_str_hash
# request though the web
# REMOTE
synch_data = synch_box2.handle_remote_synch_command(str_hash)
# response through the web
# LOCAL
assert type(synch_data) != str and any(['h' == i[0] for i in synch_data])
old_str = synch_box.local_str
synch_box.handle_local_synch_command(synch_data)  # At this step,changes happen.
assert synch_box2.local_str == synch_box.local_str != old_str

# A bad situation
# REMOTE
remote_str_hash = synch_box2.local_str_hash
# request though the web
# LOCAL
remote_synch_data = synch_box.handle_remote_synch_command(remote_str_hash)
# response through the web
# REMOTE
assert type(remote_synch_data) != str and any(['h' == i[0] for i in remote_synch_data])
# Before the difference information synchronization data comes, the string with the hash value remote_str_hash changes for some reason.
synch_box2.local_str = 'Hello world'
# The coming information can't be handled.
try:
    synch_box2.handle_local_synch_command(remote_synch_data)
except AssertionError:
    print('Fail to handle_local_synch_command')


# If you want to automatically handle this bad situation, you can pass the keyword parameter strdiff_add_error_handler to handle_local_synch_command, to be called to fetch the raw string.
# For example,
# def fetch_raw_string():
#     return requests.get('http://www.baidu.com/raw-string')
# We will demonstrate easily.
def fetch_raw_string():
    return synch_box.local_str


synch_box2.handle_local_synch_command(remote_synch_data, fetch_raw_string)  # At this step,changes happen
assert synch_box2.local_str == synch_box.local_str


# If you are using this module in a coroutine function, to request you can pass a coroutine function as the error handler,
# for example:
# async def fetch_raw_string():
#     async with aiohttp.ClientSession().get('http://www.baidu.com/raw-string') as r:
#         return await r.text()
# We will demonstrate easily.
async def fetch_raw_string():
    return synch_box.local_str


async def main():
    handle_local_synch_command_res = synch_box2.handle_local_synch_command(remote_synch_data, fetch_raw_string)
    # try to await the result only when necessary.
    if type(handle_local_synch_command_res) == asyncio.Task:
        await handle_local_synch_command_res
    assert synch_box2.local_str == synch_box.local_str


asyncio.get_event_loop().run_until_complete(main())

```
