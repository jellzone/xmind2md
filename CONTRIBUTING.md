# 贡献指南 / Contributing

欢迎用中文或英文提交 Issue、文档改进和 Pull Request。

> Contributions are licensed under the [MIT License](LICENSE). We use the
> [Developer Certificate of Origin (DCO)](https://developercertificate.org/),
> not a CLA. Sign off each commit with `git commit -s`.
> Please follow our [Code of Conduct](CODE_OF_CONDUCT.md) and report
> vulnerabilities through [SECURITY.md](SECURITY.md).

## 开始之前

- 查阅 [README](README.md) 的功能、已知限制和路线图，并搜索已有 Issue / PR。
- Bug 报告请使用 [Bug 模板](https://github.com/jellzone/xmind2md/issues/new?template=bug.yml)，附复现命令、预期输出和实际结果。
- 新功能、输出格式变更或新增依赖，请先开 Issue 说明使用场景与兼容性影响。
- 文档修正和小范围修复可以直接提交 PR。
- 不要上传凭据、真实客户资料或未经授权的思维导图。请用合成数据或已脱敏的最小样例。

## 本地开发

需要 Python 3.8+ 和 Git。项目仅使用 Python 标准库，没有第三方依赖安装步骤。

先在 GitHub 上 Fork 本仓库，再克隆自己的 Fork：

```bash
git clone https://github.com/YOUR-USERNAME/xmind2md.git
cd xmind2md
git remote add upstream https://github.com/jellzone/xmind2md.git
git switch -c docs/your-change
python3 --version
python3 xmind2md.py --help
```

`YOUR-USERNAME` 替换为你的 GitHub 用户名；功能和修复分支可用 `feat/...`、`fix/...`。

仓库目前的主要文件：

- `xmind2md.py`：JSON / XML 解析、Markdown 格式化、公共函数和 CLI。
- `README.md`：安装、使用方法、CLI 选项与限制。
- `.github/`：Issue 表单和 PR 模板。

## 修改约定

- 每个 PR 聚焦一个问题；保持标准库实现、现有代码风格和清晰的函数边界。
- 保持 `convert_xmind_to_markdown(...)` 的默认参数、返回值和 CLI 选项兼容。
- 涉及转换行为时，同步说明对 XMind 2020/Zen 的 `content.json` 与 XMind 8 的 `content.xml` 的影响。
- 更改输出格式、默认行为或支持范围时，更新 README 中的示例与限制。
- 新增依赖时，在 PR 中解释必要性、许可证和维护成本。
- 测试样例应最小化并使用合成数据；新增样例可放入 `tests/fixtures/`，并明确授权以本项目 MIT 许可证分发。

## 验证

提交前先执行现有脚本的基础检查：

```bash
python3 -m py_compile xmind2md.py
python3 xmind2md.py --help
```

仓库目前没有自动化测试套件或 CI。以上命令只检查语法和 CLI 入口，
不能证明转换结果正确。文档修改请检查代码块、相对链接和示例命令。

如果改动转换逻辑，请同时提供最小回归用例和预期 Markdown，覆盖：

- JSON 与 XML 两种包格式；多 Sheet、根主题、子主题与嵌套层级。
- 中文、空格路径和 Markdown 特殊字符。
- 备注、标签、标记、超链接，以及 `--no-notes` / `--no-labels` / `--no-markers`。
- `--max-depth 0` 和较深层级；CLI 文件输出与函数返回值的一致性。
- 不存在的输入文件、损坏 ZIP，以及缺少 `content.json` / `content.xml` 的输入。

优先使用标准库 `unittest`，将新增测试放入 `tests/`。新增后可运行：

```bash
python3 -m unittest discover -s tests -v
```

在 PR 中写明实际 Python 版本、操作系统、执行命令及结果；未验证的格式或平台请明确标出。

## 提交签署（DCO）

每个提交都需包含 `Signed-off-by` 行，表示你确认
[Developer Certificate of Origin 1.1](https://developercertificate.org/)：
你有权按本项目的 MIT 许可证提交这些内容。无需签署 CLA。

```bash
git add <changed-files>
git commit -s -m "docs: improve usage instructions"
```

`-s` 会使用你的 Git 姓名与邮箱添加签署行；这与 GPG 提交签名不同。
提交前检查身份配置。遗漏最后一次提交的签署时，可在自己的贡献分支上使用
`git commit --amend --no-edit -s`。若已推送，按协作者约定更新分支，避免覆盖他人改动。

提交信息建议使用 `docs:`、`fix:`、`feat:`、`test:` 等前缀。

## 提交 Pull Request

向 `jellzone/xmind2md` 的 `main` 分支发起 PR，并按模板填写：

1. 问题、改动后的行为和关联 Issue（如有）。
2. 实际验证步骤、结果和未覆盖的情况。
3. 涉及格式兼容性时，附合成输入与预期 Markdown。
4. 确认文档同步、无敏感数据、每个提交均已签署。

维护者审核后可能请求调整；请在原 PR 分支继续提交。
安全问题按 [SECURITY.md](SECURITY.md) 报告。
