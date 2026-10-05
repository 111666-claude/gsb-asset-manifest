# asset-manifest

资源清单校验：解析自写清单协议，再与实际资源条目比对，只用 Python 标准库。

```
python3 -m manifest.cli --sample badline
python3 -m manifest.cli --sample dup
python3 -m manifest.cli --sample extra
python3 -m manifest.cli --sample size
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **协议**：`@group 名字` 开一个新分组；条目行是 `name size hash`；空行与 `#` 注释忽略；
  其它形式的行都是错误，记进 `errors`。
- **重名**：同一个分组内名字重复算一条错误，保留先出现的那条。
- **校验**：比对清单与实际条目，`missing`（清单有、实际没有）、`extra`（实际有、清单没有）、
  `size_mismatch`（名字在两边但大小不同）三类都要报，结果各自按名字升序。
- **不变量**：`errors` 与三类结果都不受分组顺序影响；同一份输入重复校验结果相同。
- **代价**：校验是 O(清单条目数 加 实际条目数)，不许对每个条目重扫整份清单。

## 输出契约（不改格式）

```
errors=..
extra=..
size=..
```

## 目录

```
manifest/parser.py   清单协议解析
manifest/verify.py   与实际条目比对
manifest/cli.py      命令行入口
tests/test_manifest.py unittest 用例
```
