# Obsidian Translation Helper (Obsidian 翻译辅助工具)

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
    -   在项目根目录创建 `input` 文件夹。
    -   从 [obsidian-translations](https://github.com/obsidianmd/obsidian-translations) 仓库获取最新的 `en.json` 和 `zh.json` 文件。
    -   将这两个文件放置于 `input` 目录中。

### 2. 分析翻译状态

运行 `analyze_translations.py` 脚本，全面了解当前的翻译情况。这是推荐的开始方式。

```bash
python analyze_translations.py
```

该脚本会：
1.  比较 `input/en.json` 和 `input/zh.json`。
2.  在控制台输出详细的统计摘要。
3.  在 `output_analyze` 目录下生成以下文件：
    -   `translation_report.json`：完整的分析报告。
    -   `untranslated_entries.json`：所有未翻译（或与英文原文相同）的条目，格式为 `{"路径": "英文原文"}`。**这是您需要翻译的主要文件**。
    -   `potentially_translated_entries.json`：**可能已翻译**的条目，包含翻译建议，可作为翻译时的参考。

### 3. 进行翻译

1.  **创建翻译文件**：将 `output_analyze/untranslated_entries.json` 文件复制到 `input` 目录，并重命名为 `manual_translations.json`。这是您的工作文件。
2.  **翻译内容**：打开 `input/manual_translations.json`，将文件中的英文值（value）替换为中文翻译。
    -   **示例**：
        *   翻译前 (`untranslated_entries.json`):
            ```json
            {
              "command.go-to-next-tab.name": "Go to next tab"
            }
            ```
        *   翻译后 (`manual_translations.json`):
            ```json
            {
              "command.go-to-next-tab.name": "切换到下一个标签页"
            }
            ```
3.  **(可选) 参考建议**：打开 `output_analyze/potentially_translated_entries.json` 查看并利用其中的翻译建议。如果建议合适，可以将其复制到您的 `input/manual_translations.json` 文件中，以确保翻译的一致性。
4.  **保存工作**：完成翻译后，请确保已保存 `input/manual_translations.json` 文件。

### 4. 合并翻译

当 `input/manual_translations.json` 文件准备好后，运行合并脚本 `merge_translations.py`。

```bash
python merge_translations.py
```

此脚本会：
1.  读取 `input/zh.json` (原始中文文件) 和 `input/manual_translations.json` (你的翻译)。
2.  将你的翻译合并到原始数据中。
3.  在 `output` 目录下生成最终的翻译文件 `zh_translated.json`。

### 5. 生成 PR 和 Commit 信息

最后，使用 `output/zh_translated.json` 和原始的 `input/zh.json` 来生成提交信息。

```bash
python generate_pr_message.py
```

该脚本会：
1.  比较 `input/zh.json` 和 `output/zh_translated.json` 之间的差异。
2.  在 `output` 目录下生成以下文件：
    -   `pr_message.md`：包含格式化好的 PR 标题和正文，可直接复制到 GitHub。
    -   `commit_info.txt`：包含完整的 Git Commit 信息和可直接执行的 Git 命令。
    -   `translation_changes.json`：本次变更的详细 JSON 报告。

### 6. 提交翻译

1.  **替换文件**：将生成的 `output/zh_translated.json` 重命名为 `zh.json`，替换掉你本地 `obsidian-translations` 仓库中的旧文件。
2.  **提交代码**：使用 `output/commit_info.txt` 中生成的命令来提交你的更改。
3.  **创建 PR**：在 GitHub 上创建 Pull Request，并将 `output/pr_message.md` 的内容粘贴进去。

## 脚本详解

### `analyze_translations.py`

**核心功能**：分析和报告。
-   **输入**：`input/en.json`, `input/zh.json`
-   **输出** (`output_analyze/` 目录):
    -   `translation_report.json`
    -   `untranslated_entries.json`
    -   `potentially_translated_entries.json`
-   **用途**：翻译工作的第一步，用于评估工作量、获取待翻译列表和翻译建议。

### `merge_translations.py`

**核心功能**：合并翻译。
-   **输入**：`input/zh.json`, `input/manual_translations.json`
-   **输出** (`output/` 目录): `zh_translated.json`
-   **用途**：将 `manual_translations.json` 中的翻译内容安全地合并回完整的 JSON 文件结构中，生成最终的 `zh_translated.json`。

### `generate_pr_message.py`

**核心功能**：生成 PR 和 Commit 信息。
-   **输入**：`input/zh.json` (旧), `output/zh_translated.json` (新), `input/en.json` (可选参考)
-   **输出** (`output/` 目录):
    -   `pr_message.md`
    -   `commit_info.txt`
    -   `translation_changes.json`
-   **用途**：自动化创建高质量、规范的提交信息，节省时间并符合社区贡献标准。

## 贡献

欢迎通过 Issue 或 Pull Request 提出改进建议，让这个工具变得更好用！
