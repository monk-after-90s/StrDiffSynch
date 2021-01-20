# StrDiffSynch

This module calculates the difference from one string to another. If the origin string absorbs the difference, it
becomes the other string.

Thus, two endpoints could synchronize the strings by passing the difference.

---

### [Install](#Install) · [Usage](#Usage) ·

---

## Install

[StrDiffSynch in **PyPI**](https://pypi.org/project/StrDiffSynch/)

```shell
pip install StrDiffSynch
```

## Usage

### StrDiff

One of two strings can change into the other when absorbing the difference from it to the other.

```python
import json
from StrDiffSynch import StrDiff

data1 = json.dumps({"name": "davis", "other": {"age": 18}})
data2 = json.dumps({"name": "davis", "age": 18})
diff = StrDiff(data1, data2)
assert data1 + diff == data2
assert diff + data1 == data2
```

### SynchBox

This class is used for synchronizing big string but not big enough to have to be stored in a database, among two
endpoints. We will demonstrate with codes. You can type them in python console.

```python
import asyncio

from StrDiffSynch import SynchBox
```

At endpoint A, set the SynchBox to contain the string.

```python
synch_boxA = SynchBox('This is big data.')
```

Update the containing string.

```python
synch_boxA.local_str = 'This is another big data.'
```

At endpoint B, set the SynchBox to contain a empty string.

```python
synch_boxB = SynchBox('')
```

Get the string hash at endpoint B.

```python
B_str_hash = synch_boxB.local_str_hash
```

Now endpoint A is commanded to synchronize endpoint B. Endpoint A needs to know the string hash at endpoint B, to
calculate the difference data.

```python
B_synch_data = synch_boxA.handle_remote_synch_command(B_str_hash)
```

Because no synchronization has happened, 'B_synch_data' would be the raw big string, 'This is another big data.' as
demonstration.

Endpoint B gets 'B_synch_data' to synchronize itself.

```python
synch_boxB.handle_local_synch_command(B_synch_data)
assert 'This is another big data.' == B_synch_data == synch_boxB.local_str
```

Now repeat to synchronize to see what will happen after the initial synchronization.

Well now that initial synchronization has happened, SynchBox will try to find the difference information between these
two copy , which is usually much smaller than the raw string.

```python
B_str_hash = synch_boxB.local_str_hash
B_synch_data = synch_boxA.handle_remote_synch_command(B_str_hash)
assert type(B_synch_data) != str and any(['h' == i[0] for i in B_synch_data])
```

At this step,there is nothing to change in fact.

```python
old_B_local_str = synch_boxB.local_str
synch_boxB.handle_local_synch_command(B_synch_data)
assert synch_boxB.local_str == synch_boxA.local_str == old_B_local_str
```

Now repeat once more. Let's make some change at endpoint A.

```python
synch_boxA.local_str += 'u28dy2'
B_str_hash = synch_boxB.local_str_hash
B_synch_data = synch_boxA.handle_remote_synch_command(B_str_hash)
assert type(B_synch_data) != str and any(['h' == i[0] for i in B_synch_data])
old_str = synch_boxB.local_str
```

Apply the change.

```python
synch_boxB.handle_local_synch_command(B_synch_data)
assert synch_boxB.local_str == synch_boxA.local_str != old_str
```

Vice versa, endpoint B could synchronizes endpoint A. Let's make some change at endpoint B.

```python
synch_boxB.local_str = synch_boxB.local_str[0:3] + synch_boxB.local_str[-3:]
str_hash = synch_boxA.local_str_hash
synch_data = synch_boxB.handle_remote_synch_command(str_hash)
assert type(synch_data) != str and any(['h' == i[0] for i in synch_data])
old_str = synch_boxA.local_str
synch_boxA.handle_local_synch_command(synch_data)
assert synch_boxB.local_str == synch_boxA.local_str != old_str
```

Well, everything is OK so far. However there is a possibility that the synchronization data can not be applied.

```python
B_str_hash = synch_boxB.local_str_hash
B_synch_data = synch_boxA.handle_remote_synch_command(B_str_hash)
assert type(B_synch_data) != str and any(['h' == i[0] for i in B_synch_data])
```

Before the synchronization data comes, the string with the hash value B_str_hash changes for some reason.

```python
synch_boxB.local_str = 'Hello world'
```

The coming data can't be handled.

```python
try:
    synch_boxB.handle_local_synch_command(B_synch_data)
except AssertionError:
    print('Fail to handle_local_synch_command')
```

If you want to automatically handle this bad situation, you can pass the keyword parameter "strdiff_add_error_handler"
to
"handle_local_synch_command", to be called to fetch the raw string. For example,

```python
def fetch_raw_string():
    return requests.get('http://www.baidu.com/raw-string')
```

We will demonstrate an easy example.

```python
def fetch_raw_string():
    return synch_boxA.local_str


synch_boxB.handle_local_synch_command(B_synch_data, fetch_raw_string)
assert synch_boxB.local_str == synch_boxA.local_str
```

If you are using this module in a coroutine function, you can pass a coroutine function as the error handler to request.
For example:

```python
async def fetch_raw_string():
    async with aiohttp.ClientSession().get('http://www.baidu.com/raw-string') as r:
        return await r.text()
```

We will demonstrate an easy example:

```python
async def fetch_raw_string():
    return synch_boxA.local_str


async def main():
    handle_local_synch_command_res = synch_boxB.handle_local_synch_command(B_synch_data, fetch_raw_string)
    # try to await the result only when necessary.
    if type(handle_local_synch_command_res) == asyncio.Task:
        await handle_local_synch_command_res
    assert synch_boxB.local_str == synch_boxA.local_str


asyncio.get_event_loop().run_until_complete(main())

```
