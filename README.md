# xmind2md · XMind → Markdown 转换器

将 `.xmind` 思维导图一键转换为结构清晰的 Markdown 大纲。  
同时支持 **XMind 2020/Zen（content.json）** 与 **XMind 8（content.xml）** 打包格式，零第三方依赖，Python 标准库即可跑。

> 典型场景：知识库归档、协作文档初始化、从脑图快速生成 README/会议记录/计划草案。

---

## 功能特性

- ✅ 双格式兼容：XMind 2020/Zen（JSON）与 XMind 8（XML）
- ✅ 结构化导出：Sheet → `#`，Root → `##`，其余层级 → 缩进无序列表
- ✅ 内容映射：  
  - **超链接** → Markdown 链接  
  - **备注**（Notes）→ 引用块 `>`  
  - **标签**（Labels）→ 行内代码 `` `label` ``  
  - **标记**（Markers）→ `<priority-1>` 等后缀  
- ✅ 可选项：限制导出深度、关闭备注/标签/标记
- ✅ 纯标准库：不依赖任何外部包，便于 CI/CD 与离线使用

---

## 安装

方式一（直接使用脚本）：
```bash
git clone https://github.com/<your-org-or-name>/xmind2md.git
cd xmind2md
python xmind2md.py -h
````

方式二（作为模块导入，便于二次开发）：

```python
from xmind2md import convert_xmind_to_markdown

md_text = convert_xmind_to_markdown(
    "input.xmind",
    output_path="output.md",
    notes=True,
    labels=True,
    markers=True,
    max_depth=None
)
```

> 运行要求：Python 3.8+（仅用到 `zipfile/json/xml.etree` 等标准库）

---

## 快速开始

```bash
# 最常用：把 input.xmind 转成 output.md
python xmind2md.py input.xmind -o output.md

# 仅导出前 3 层，不包含备注与标记
python xmind2md.py input.xmind -o output.md --max-depth 3 --no-notes --no-markers
```

成功后，终端会打印预览的前 40 行，同时在目标位置生成 `.md`。

---

## CLI 选项

```text
usage: xmind2md.py input.xmind -o output.md [--max-depth N] [--no-notes] [--no-labels] [--no-markers]

--max-depth N   限制导出层级（0=仅导出一层子主题）
--no-notes      不导出备注（Notes）
--no-labels     不导出标签（Labels）
--no-markers    不导出标记（Markers）
```

---

## 输出格式规范（映射规则）

* **Sheet 标题** → `# <sheet title>`
* **根主题（Root）** → `## <root topic>`
* **子主题层级** → 使用缩进与 `-` 生成无序列表
* **备注（Notes）** → 列表项下方使用 `>` 多行引用
* **标签（Labels）** → 以 `` `label` `` 形式追加在行末
* **标记（Markers）** → 以 `<marker-id>` 形式追加在行末
* **超链接（Hyperlink）** → 转为 `[title](url)`，自动转义 `)` 等符号

示例（节选）：

```markdown
# 示例Sheet
## 根主题
- 子主题A `标签A` <priority-1>
  > 这是备注的第一行
  > 第二行
  - 孙主题A1
- [子主题B](https://example.com)
```

---

## 兼容性说明

* **XMind 2020/Zen**：读取包内 `content.json`
* **XMind 8**：读取包内 `content.xml`
* 自动识别两种格式，无需额外参数

---

## 已知限制

* 图片/附件不导出（如需导出，建议在 Markdown 中保留路径或后续扩展）
* 关系（Relationships）、边界（Boundaries）、汇总（Summaries）目前以主题层级信息为主，不渲染图形结构
* 极个别历史版本的 XMind 包结构不标准时，可能需要先在 XMind 中打开另存为后再转换

---

## 常见问题（Troubleshooting）

1. **报错 “This .xmind file doesn't contain content.json or content.xml”**

   * 原因：包内缺少核心内容文件（损坏或非常老旧的导出格式）。
   * 处理：用 XMind 打开该文件，另存为新 `.xmind` 后再试。

2. **中文路径/空格路径**

   * 处理：在命令行中使用引号包裹路径，例如
     `python xmind2md.py "D:\文档\我的文件.xmind" -o "D:\输出\我的文件.md"`

3. **内容过深或太冗长**

   * 处理：使用 `--max-depth` 限制层级，或搭配 `--no-notes` 简化输出。

4. **Markdown 渲染错位**

   * 处理：原文中若含特殊符号，脚本已做轻度转义；仍异常时建议检查个别节点文本是否包含不闭合的 Markdown 语法。

---

## 路线图

* [ ] 可选导出为不同风格（全标题层级、混排、有序列表等）
* [ ] 图片与附件的提取与引用占位
* [ ] Relationships/Boundaries/Summaries 基础渲染
* [ ] 多语言环境测试矩阵完善（Windows/Linux/macOS）

---

## 参与贡献

欢迎 PR / Issue：

* 代码风格尽量保持无第三方依赖、结构清晰
* 新增能力务必附带最小可复现样例
* 大型功能请先开 Issue 讨论方向

---

## 许可证

本项目使用 **MIT License**，详见 [LICENSE](./LICENSE)。

````

---

## 🧾 LICENSE (MIT)

```text
MIT License

Copyright (c) 2025 <Your Name>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
````

> 把 `<Your Name>` 换成你的名字或公司名。

---

## 🌫️ .gitignore（建议）

```gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
build/
dist/
*.egg-info/

# macOS / Windows
.DS_Store
Thumbs.db

# Editors
.vscode/
.idea/

# Test artifacts
*.xmind
*.md
!README.md
```
