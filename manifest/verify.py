"""清单校验：把分组继承展开成生效条目，再与实际条目比对。

缺陷：子分组看不到父分组条目、不检测继承环、多余文件不报、大小不比较、
展开时对每个条目重扫全部分组。
"""


class Verifier:
    """校验台账。"""

    def __init__(self, groups):
        self.groups = groups
        self.work = 0

    def effective(self, name):
        """返回某个分组的生效条目。缺陷：只用本组条目、不查环、每个条目重扫全部分组。"""
        entries = {}
        group = self.groups.get(name)
        if group is None:
            return entries
        for entry in group["entries"]:
            self.work += len(self.groups)
            entries[entry["name"]] = entry
        return entries

    def compare(self, name, actual):
        """返回 missing / extra / size_mismatch。缺陷：多余与大小都不报。"""
        entries = self.effective(name)
        missing = [key for key in entries if key not in actual]
        return {"missing": sorted(missing), "extra": [], "size_mismatch": []}

    def errors(self):
        """返回解析与继承相关的错误。缺陷：恒为空。"""
        return []

    def work_count(self):
        return self.work
