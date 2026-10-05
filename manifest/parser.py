"""清单解析：@group 分段，条目行是 name size hash。

协议见 README：非法行、无法解析的 size、组内重名都记入 errors（重名保留先出现的）。
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
            header = parse_group_header(line, groups, errors)
            if header is not None:
                current = header
            continue
        parts = line.split()
        if len(parts) != 3:
            errors.append("非法行: %s" % line)
            continue
        name, size, digest = parts
        if any(entry["name"] == name for entry in groups[current]["entries"]):
            errors.append("组内重名: %s/%s" % (current, name))
            continue
        try:
            value = int(size)
        except ValueError:
            errors.append("无法解析 size: %s" % line)
            continue
        groups[current]["entries"].append({"name": name, "size": value, "hash": digest})
    return groups, sorted(errors)


def parse_group_header(line, groups, errors):
    """解析 `@group 名字` 或 `@group 名字 : 父分组`，非法时记错误并返回 None。"""
    body = line[1:].strip()
    if ":" in body:
        name, _, parent = body.partition(":")
        name = name.strip()
        parent = parent.strip()
        if not name or not parent or ":" in parent:
            errors.append("非法行: %s" % line)
            return None
    else:
        name = body.strip()
        parent = ""
        if not name:
            errors.append("非法行: %s" % line)
            return None
    if name not in groups:
        groups[name] = {"name": name, "parent": parent, "entries": []}
    return name
