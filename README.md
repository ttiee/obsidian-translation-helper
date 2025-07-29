# Obsidian 翻译辅助工具

本项目包含一系列 Python 脚本，旨在简化为 [Obsidian](https://obsidian.md/) 进行中文翻译的流程。这些工具可以帮助您：

-   分析当前翻译进度。
-   识别未翻译和可能已翻译的文本。
-   利用现有翻译成果，自动填充建议。
-   合并翻译内容。
-   自动生成规范的 Pull Request 和 Git Commit 信息。

目标仓库：[obsidianmd/obsidian-translations](https://github.com/obsidianmd/obsidian-translations)

## ✨ 功能特性

-   **全面的翻译状态分析**：精确统计已翻译、未翻译、与原文相同的条目。
-   **智能翻译建议**：利用已有的翻译内容，为新出现的相同英文文本提供翻译建议，提高效率和一致性。
-   **清晰的产出物**：生成多个 JSON 文件，分别包含纯未翻译、可能已翻译和完整的分析报告。
-   **自动化合并**：将翻译好的内容安全地合并回 `zh.json` 文件结构中。
-   **一键生成提交信息**：根据翻译变更，自动生成符合社区规范的 PR 标题、正文和 Git Commit 信息。

## 🚀 快速开始

### 1. 准备工作

1.  **克隆仓库**：将此工具仓库克隆到本地。
2.  **安装依赖**：本项目无第三方依赖，使用标准 Python 即可。
3.  **准备翻译文件**：
    -   从 [obsidian-translations](https://github.com/obsidianmd/obsidian-translations) 仓库获取最新的 `en.json` 和 `zh.json` 文件。
    -   将这两个文件放置于脚本所在的根目录。

### 2. 分析翻译状态

运行分析脚本，了解当前的翻译情况。

```bash
python translate.py
```

该脚本会：
1.  比较 `en.json` 和 `zh.json`。
2.  在控制台输出详细的统计摘要。
3.  生成以下文件：
    -   `translation_report.json`：完整的分析报告。
    -   `untranslated_entries.json`：**真正未翻译**的条目，格式为 `{"路径": "英文原文"}`。
    -   `potentially_translated_entries.json`：**可能已翻译**的条目，包含翻译建议。

### 3. 进行翻译

1.  **创建翻译文件**：复制 `untranslated_entries.json` 并重命名为 `translated_entries.json`。
2.  **翻译内容**：打开 `translated_entries.json`，将文件中的英文值（value）替换为中文翻译。

    **示例**：
    *   翻译前 (`untranslated_entries.json`):
        ```json
        {
          "command.go-to-next-tab.name": "Go to next tab"
        }
        ```
    *   翻译后 (`translated_entries.json`):
        ```json
        {
          "command.go-to-next-tab.name": "切换到下一个标签页"
        }
        ```
3.  **(可选) 参考建议**：打开 `potentially_translated_entries.json` 查看并利用其中的翻译建议，手动将它们添加到 `translated_entries.json` 中。

### 4. 合并翻译

当 `translated_entries.json` 文件准备好后，运行合并脚本。

```bash
python pre.py
```

此脚本会：
1.  读取 `zh.json` (原始中文文件) 和 `translated_entries.json` (你的翻译)。
2.  将你的翻译合并到原始数据中。
3.  生成最终的翻译文件 `zh_translated.json`。

### 5. 生成 PR 和 Commit 信息

最后，使用 `zh_translated.json` 和原始的 `zh.json` 来生成提交信息。

```bash
python generate_pr_message.py
```

该脚本会：
1.  比较 `zh.json` 和 `zh_translated.json` 之间的差异。
2.  生成以下文件：
    -   `pr_message.md`：包含格式化好的 PR 标题和正文，可直接复制到 GitHub。
    -   `commit_info.txt`：包含完整的 Git Commit 信息和可直接执行的 Git 命令。
    -   `translation_changes.json`：本次变更的详细 JSON 报告。

### 6. 提交翻译

1.  **替换文件**：将生成的 `zh_translated.json` 重命名为 `zh.json`，替换掉你本地 `obsidian-translations` 仓库中的旧文件。
2.  **提交代码**：使用 `commit_info.txt` 中生成的命令来提交你的更改。
3.  **创建 PR**：在 GitHub 上创建 Pull Request，并将 `pr_message.md` 的内容粘贴进去。

## 脚本详解

### `translate.py`

**核心功能**：分析和报告。
-   **输入**：`en.json`, `zh.json`
-   **输出**：
    -   `translation_report.json`
    -   `untranslated_entries.json`
    -   `potentially_translated_entries.json`
-   **用途**：翻译工作的第一步，用于评估工作量和获取待翻译列表。

### `pre.py`

**核心功能**：合并翻译。
-   **输入**：`zh.json`, `translated_entries.json`
-   **输出**：`zh_translated.json`
-   **用途**：将分散的翻译条目整合回完整的 JSON 文件结构中。

### `generate_pr_message.py`

**核心功能**：生成 PR 和 Commit 信息。
-   **输入**：`zh.json` (旧), `zh_translated.json` (新), `en.json` (可选参考)
-   **输出**：
    -   `pr_message.md`
    -   `commit_info.txt`
    -   `translation_changes.json`
-   **用途**：自动化创建高质量、规范的提交信息，节省时间并符合社区贡献标准。

## 贡献

欢迎通过 Issue 或 Pull Request 提出改进建议，让这个工具变得更好用！
