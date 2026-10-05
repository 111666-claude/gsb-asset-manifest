"""清单解析：@group 分段，条目行是 name size hash。

缺陷：非法行静默跳过、组内重名不报错、size 解析失败当 0。
"""


def parse(text):
    """解析清单文本，返回 (分组字典, 错误列表)。缺陷：非法行与重名都不报错。"""
    groups = {}
    errors = []
    current = "default"
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("@"):
            current = line[1:].strip()
            groups.setdefault(current, [])
            continue
        parts = line.split()
        if len(parts) != 3:
            continue
        name, size, digest = parts
        try:
            value = int(size)
        except ValueError:
            value = 0
        groups.setdefault(current, []).append({"name": name, "size": value, "hash": digest})
    return groups, errors
