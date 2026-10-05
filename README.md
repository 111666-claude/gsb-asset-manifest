# asset-manifest

资源清单校验：解析自写清单协议（支持分组继承），展开成生效条目后与实际资源比对，只用 Python 标准库。

```
python3 -m manifest.cli --sample inherit
python3 -m manifest.cli --sample cycle
python3 -m manifest.cli --sample extra
python3 -m manifest.cli --sample size
python3 -m manifest.cli --sample badline
python3 -m manifest.cli --sample dup
python3 -m manifest.cli --sample work
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **协议**：`@group 名字` 或 `@group 名字 : 父分组` 开分组；条目行是 `name size hash`；
  空行与 `#` 注释忽略；其它形式的行、解析不出的 size、组内重名都要记进 `errors`（重名保留先出现的）。
- **继承覆盖层**：分组的生效条目等于父分组生效条目加上本组条目，同名条目由本组覆盖；
  父分组不存在记一条错误，继承链成环也记一条错误。
- **校验**：`missing` 是生效清单有而实际没有、`extra` 是实际有而生效清单没有、
  `size_mismatch` 是两边都有但大小不同；三类都要报，各自按名字升序。
- **不变量**：`errors` 与三类结果都不受分组书写顺序影响；同一份输入重复校验结果相同。
- **代价**：展开一个分组是 O(该分组条目数)，不许对每个条目重扫全部分组；
  `work_count()` 不随分组数乘条目数增长。

## 输出契约（不改格式）

```
missing=..
errors=..
extra=..
size=..
work=..
```

## 目录

```
manifest/parser.py   清单协议解析
manifest/verify.py   继承展开与比对
manifest/cli.py      命令行入口
tests/test_manifest.py unittest 用例
```
