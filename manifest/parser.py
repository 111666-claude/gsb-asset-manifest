"""清单解析：@group 分段，条目行是 name size hash。"""


def parse(text):
    """解析清单文本，返回 (分组字典, 错误列表)。分组字典的值是 {name, parent, entries}。"""
    groups = {}
    errors = []
    seen = {}
    current = "default"
    groups[current] = {"name": current, "parent": "", "entries": []}
    seen[current] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("@"):
            header = line[1:].strip()
            if ":" in header:
                name, parent = header.split(":", 1)
                name, parent = name.strip(), parent.strip()
            else:
                name, parent = header, ""
            if not name:
                errors.append("非法行: %s" % line)
                continue
            current = name
            if name not in groups:
                groups[name] = {"name": name, "parent": parent, "entries": []}
                seen[name] = set()
            else:
                groups[name]["parent"] = parent
            continue
        parts = line.split()
        if len(parts) != 3:
            errors.append("非法行: %s" % line)
            continue
        name, size, digest = parts
        try:
            value = int(size)
        except ValueError:
            errors.append("size 解析失败: %s" % line)
            continue
        if name in seen[current]:
            errors.append("组内重名: %s" % name)
            continue
        seen[current].add(name)
        groups[current]["entries"].append({"name": name, "size": value, "hash": digest})
    return groups, errors
