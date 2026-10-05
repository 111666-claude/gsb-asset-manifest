"""清单解析：@group 分段，条目行是 name size hash。

缺陷：非法行静默跳过、组内重名不报、size 解析失败当 0、@group 的父分组写法不解析。
"""


def parse(text):
    """解析清单文本，返回 (分组字典, 错误列表)。分组字典的值是 {name, parent, entries}。"""
    groups = {}
    errors = []
    current = "default"
    groups[current] = {"name": current, "parent": "", "entries": []}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("@"):
            current = line[1:].strip().split(":")[0].strip()
            groups[current] = {"name": current, "parent": "", "entries": []}
            continue
        parts = line.split()
        if len(parts) != 3:
            continue
        name, size, digest = parts
        try:
            value = int(size)
        except ValueError:
            value = 0
        groups[current]["entries"].append({"name": name, "size": value, "hash": digest})
    return groups, errors
