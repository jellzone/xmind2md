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
