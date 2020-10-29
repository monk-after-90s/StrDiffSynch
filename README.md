# StrDiffSynch
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
