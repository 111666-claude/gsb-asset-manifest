"""清单校验：把分组继承展开成生效条目，再与实际条目比对。

口径见 README：生效条目 = 父分组生效条目 + 本组条目（同名由本组覆盖）；
父分组不存在或继承链成环各记一条错误；missing / extra / size_mismatch 三类都报，
各自按名字升序；展开一个分组是 O(该分组条目数)。
"""

class _LayeredMap:
    """本组条目覆盖父组同名条目的只读层叠视图，构造 O(本组条目数)，查找走循环。"""

    __slots__ = ("own", "parent")

    def __init__(self, own, parent):
        self.own = own
        self.parent = parent

    def _maps(self):
        node = self
        while node is not None:
            yield node.own
            node = node.parent

    def __getitem__(self, key):
        for mapping in self._maps():
            if key in mapping:
                return mapping[key]
        raise KeyError(key)

    def __contains__(self, key):
        return any(key in mapping for mapping in self._maps())

    def __iter__(self):
        seen = set()
        for mapping in self._maps():
            for key in mapping:
                if key not in seen:
                    seen.add(key)
                    yield key

    def __len__(self):
        return sum(1 for _ in self)


class Verifier:
    """校验台账。"""

    def __init__(self, groups):
        self.groups = groups
        self.work = 0
        self._broken = None
        self._errors = None
        self._cache = {}

    def effective(self, name):
        """返回某个分组的生效条目（本组覆盖父组同名条目）。

        继承链上有环或缺失父分组时，只返回本组条目。
        """
        if name in self._cache:
            return self._cache[name]
        group = self.groups.get(name)
        if group is None:
            return {}
        if name in self._broken_groups():
            result = self._own_entries(group)
            self._cache[name] = result
            return result
        chain = []
        node = name
        while node in self.groups and node not in self._cache:
            chain.append(node)
            node = self.groups[node]["parent"]
        result = self._cache.get(node)
        for group_name in reversed(chain):
            own = self._own_entries(self.groups[group_name])
            result = _LayeredMap(own, result)
            self._cache[group_name] = result
        return self._cache[name]

    def _own_entries(self, group):
        own = {}
        for entry in group["entries"]:
            self.work += 1
            own[entry["name"]] = entry
        return own

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
            self._analyze()
        return list(self._errors)

    def work_count(self):
        return self.work

    def _broken_groups(self):
        """返回继承链上有环或缺失父分组的分组集合（含下游受影响的分组）。"""
        if self._broken is None:
            self._analyze()
        return self._broken

    def _analyze(self):
        missing_parent = set()
        errors = []
        for name in sorted(self.groups):
            parent = self.groups[name]["parent"]
            if parent and parent not in self.groups:
                missing_parent.add(name)
                errors.append("父分组不存在: %s -> %s" % (name, parent))

        in_cycle = set()
        state = {}
        for start in sorted(self.groups):
            if state.get(start):
                continue
            stack = []
            node = start
            while node and node in self.groups and not state.get(node):
                state[node] = "visiting"
                stack.append(node)
                node = self.groups[node]["parent"]
            if node and state.get(node) == "visiting":
                cycle = stack[stack.index(node):]
                in_cycle.update(cycle)
                errors.append("继承链成环: %s" % " -> ".join(cycle + [node]))
            for done in stack:
                state[done] = "done"

        broken = set(missing_parent) | in_cycle
        changed = True
        while changed:
            changed = False
            for name, group in self.groups.items():
                if name not in broken and group["parent"] in broken:
                    broken.add(name)
                    changed = True

        self._broken = broken
        self._errors = sorted(errors)
