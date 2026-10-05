"""清单校验：比对清单与实际条目，报告缺失、多余与大小不符。

缺陷：同组重名只留最后一条、实际多出来的文件不报、完全不比较大小。
"""


def compare(groups, actual):
    """返回 missing / extra / size_mismatch 三类结果（各自按名字升序）。"""
    missing = []
    for entries in groups.values():
        seen = {}
        for entry in entries:
            seen[entry["name"]] = entry
        for name in seen:
            if name not in actual:
                missing.append(name)
    return {"missing": sorted(missing), "extra": [], "size_mismatch": []}
