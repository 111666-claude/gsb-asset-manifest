"""清单校验：把分组继承展开成生效条目，再与实际条目比对。"""


class Verifier:
    """校验台账。"""

    def __init__(self, groups):
        self.groups = groups
        self.work = 0
        self._cache = {}
        self._errors = None

    def effective(self, name):
        """返回某个分组的生效条目：父分组生效条目加本组条目，同名由本组覆盖。"""
        entries, _ = self._expand(name, set())
        return dict(entries)

    def _expand(self, name, visiting):
        """展开分组，返回 (条目字典, 是否可缓存)。每个分组只展开一次，代价 O(本组条目数)。"""
        if name in self._cache:
            return self._cache[name], True
        group = self.groups.get(name)
        if group is None:
            return {}, True
        if name in visiting:
            return {}, False
        visiting.add(name)
        entries = {}
        cacheable = True
        parent = group["parent"]
        if parent:
            parent_entries, cacheable = self._expand(parent, visiting)
            entries = dict(parent_entries)
        self.work += len(group["entries"])
        for entry in group["entries"]:
            entries[entry["name"]] = entry
        visiting.discard(name)
        if cacheable:
            self._cache[name] = entries
        return entries, cacheable

    def compare(self, name, actual):
        """返回 missing / extra / size_mismatch，各自按名字升序。"""
        entries = self.effective(name)
        missing = sorted(key for key in entries if key not in actual)
        extra = sorted(key for key in actual if key not in entries)
        size_mismatch = sorted(
            key for key in entries if key in actual and entries[key]["size"] != actual[key]
        )
        return {"missing": missing, "extra": extra, "size_mismatch": size_mismatch}

    def errors(self):
        """返回继承相关的错误：父分组不存在、继承链成环，各记一条。"""
        if self._errors is None:
            self._errors = self._compute_errors()
        return list(self._errors)

    def _compute_errors(self):
        errors = []
        for name in sorted(self.groups):
            parent = self.groups[name]["parent"]
            if parent and parent not in self.groups:
                errors.append("分组 %s 的父分组 %s 不存在" % (name, parent))
        done = set()
        for start in sorted(self.groups):
            if start in done:
                continue
            path = []
            node = start
            while node in self.groups and node not in done and node not in path:
                path.append(node)
                node = self.groups[node]["parent"]
            if node in path:
                cycle = path[path.index(node):]
                errors.append("继承链成环: %s" % " -> ".join(cycle + [node]))
            done.update(path)
        return errors

    def work_count(self):
        return self.work
