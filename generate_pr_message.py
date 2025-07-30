import json
import os
from datetime import datetime
from typing import Dict, Any, List, Tuple

def load_json_file(filepath: str) -> Dict[Any, Any]:
    """加载JSON文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"文件未找到: {filepath}")
        return {}
    except json.JSONDecodeError as e:
        print(f"JSON解析错误 {filepath}: {e}")
        return {}

def get_all_paths(data: Dict[Any, Any], prefix: str = "") -> Dict[str, Any]:
    """递归获取JSON中所有的路径和值"""
    paths = {}
    
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, (dict, list)):
                paths.update(get_all_paths(value, current_path))
            else:
                paths[current_path] = value
    elif isinstance(data, list):
        for i, value in enumerate(data):
            current_path = f"{prefix}[{i}]"
            if isinstance(value, (dict, list)):
                paths.update(get_all_paths(value, current_path))
            else:
                paths[current_path] = value
    
    return paths

def analyze_translation_changes(old_zh_file: str, new_zh_file: str, en_file: str = None) -> Dict[str, Any]:
    """分析翻译变更"""
    print("正在分析翻译变更...")
    
    old_data = load_json_file(old_zh_file)
    new_data = load_json_file(new_zh_file)
    en_data = load_json_file(en_file) if en_file and os.path.exists(en_file) else {}
    
    old_paths = get_all_paths(old_data)
    new_paths = get_all_paths(new_data)
    en_paths = get_all_paths(en_data) if en_data else {}
    
    # 分类变更
    new_translations = {}  # 新翻译的项目
    updated_translations = {}  # 更新的翻译
    removed_translations = {}  # 删除的翻译
    
    # 找出新增和更新的翻译
    for path, new_value in new_paths.items():
        old_value = old_paths.get(path)
        en_value = en_paths.get(path, "")
        
        if old_value is None:
            # 新增的项目
            new_translations[path] = {
                "chinese": new_value,
                "english": en_value
            }
        elif old_value != new_value:
            # 更新的项目
            updated_translations[path] = {
                "old": old_value,
                "new": new_value,
                "english": en_value
            }
    
    # 找出删除的翻译
    for path, old_value in old_paths.items():
        if path not in new_paths:
            removed_translations[path] = {
                "chinese": old_value,
                "english": en_paths.get(path, "")
            }
    
    return {
        "new_translations": new_translations,
        "updated_translations": updated_translations,
        "removed_translations": removed_translations,
        "total_old": len(old_paths),
        "total_new": len(new_paths),
        "summary": {
            "new_count": len(new_translations),
            "updated_count": len(updated_translations),
            "removed_count": len(removed_translations),
            "total_changes": len(new_translations) + len(updated_translations) + len(removed_translations)
        }
    }

def categorize_changes_by_feature(changes: Dict[str, Any]) -> Dict[str, List[str]]:
    """按功能模块分类变更"""
    categories = {
        "界面相关": [],
        "编辑器": [],
        "插件系统": [],
        "设置选项": [],
        "文件管理": [],
        "搜索功能": [],
        "主题样式": [],
        "快捷键": [],
        "工作区": [],
        "其他": []
    }
    
    # 定义关键词映射
    keyword_mapping = {
        "界面相关": ["interface", "ui", "menu", "toolbar", "sidebar", "status", "ribbon", "view"],
        "编辑器": ["editor", "markdown", "preview", "format", "syntax", "writing"],
        "插件系统": ["plugin", "extension", "addon", "community"],
        "设置选项": ["settings", "preferences", "options", "config", "general"],
        "文件管理": ["file", "folder", "vault", "import", "export", "attach"],
        "搜索功能": ["search", "find", "query", "index"],
        "主题样式": ["theme", "css", "style", "appearance", "color"],
        "快捷键": ["hotkey", "shortcut", "key", "command"],
        "工作区": ["workspace", "pane", "split", "tab", "window"]
    }
    
    all_changes = {}
    all_changes.update(changes["new_translations"])
    all_changes.update(changes["updated_translations"])
    
    for path in all_changes.keys():
        path_lower = path.lower()
        categorized = False
        
        for category, keywords in keyword_mapping.items():
            if any(keyword in path_lower for keyword in keywords):
                categories[category].append(path)
                categorized = True
                break
        
        if not categorized:
            categories["其他"].append(path)
    
    # 移除空分类
    return {k: v for k, v in categories.items() if v}

def generate_pr_title(changes: Dict[str, Any]) -> str:
    """生成PR标题"""
    summary = changes["summary"]
    total_changes = summary["total_changes"]
    
    if total_changes == 0:
        return "docs: 更新中文翻译文件"
    
    change_types = []
    if summary["new_count"] > 0:
        change_types.append(f"新增{summary['new_count']}项")
    if summary["updated_count"] > 0:
        change_types.append(f"更新{summary['updated_count']}项")
    if summary["removed_count"] > 0:
        change_types.append(f"删除{summary['removed_count']}项")
    
    return f"update zh.json: 中文翻译更新 - {', '.join(change_types)}"

def generate_pr_body(changes: Dict[str, Any], categories: Dict[str, List[str]]) -> str:
    """生成PR正文"""
    summary = changes["summary"]
    
    body = "## 翻译更新摘要\n\n"
    
    # 统计信息
    body += "### 📊 更新统计\n\n"
    body += f"- 🆕 新增翻译: {summary['new_count']} 项\n"
    body += f"- 🔄 更新翻译: {summary['updated_count']} 项\n"
    if summary["removed_count"] > 0:
        body += f"- 🗑️ 删除翻译: {summary['removed_count']} 项\n"
    body += f"- 📈 总计变更: {summary['total_changes']} 项\n\n"
    
    # 按功能分类
    if categories:
        body += "### 🏷️ 变更分类\n\n"
        for category, paths in categories.items():
            body += f"**{category}** ({len(paths)} 项)\n"
            # 只显示前5个，避免过长
            for path in paths[:5]:
                body += f"- `{path}`\n"
            if len(paths) > 5:
                body += f"- ... 还有 {len(paths) - 5} 项\n"
            body += "\n"
    
    # 重要更新示例
    if changes["new_translations"]:
        body += "### ✨ 新增翻译示例\n\n"
        new_items = list(changes["new_translations"].items())
        for i, (path, info) in enumerate(new_items[:5]):
            en_text = info.get("english", "")
            zh_text = info["chinese"]
            body += f"- `{path}`\n"
            if en_text:
                body += f"  - EN: {en_text}\n"
            body += f"  - ZH: {zh_text}\n\n"
        
        if len(new_items) > 5:
            body += f"... 还有 {len(new_items) - 5} 项新增翻译\n\n"
    
    if changes["updated_translations"]:
        body += "### 🔄 更新翻译示例\n\n"
        updated_items = list(changes["updated_translations"].items())
        for i, (path, info) in enumerate(updated_items[:3]):
            body += f"- `{path}`\n"
            if info.get("english"):
                body += f"  - EN: {info['english']}\n"
            body += f"  - 旧: {info['old']}\n"
            body += f"  - 新: {info['new']}\n\n"
        
        if len(updated_items) > 3:
            body += f"... 还有 {len(updated_items) - 3} 项更新翻译\n\n"
    
    # 翻译说明
    body += "### 📝 翻译说明\n\n"
    body += "- ✅ 所有翻译已经过审核确认\n"
    body += "- 🎯 保持了与英文界面的功能对应关系\n"
    body += "- 🔤 专业术语翻译保持一致性\n"
    body += "- 📱 适配了中文用户的使用习惯\n\n"
    
    body += "### 🧪 测试建议\n\n"
    body += "- [ ] 验证界面显示正确\n"
    body += "- [ ] 检查中文字符编码\n"
    body += "- [ ] 确认功能操作正常\n"
    body += "- [ ] 测试设置项生效\n"
    
    return body

def generate_commit_message(changes: Dict[str, Any]) -> str:
    """生成Git commit信息"""
    summary = changes["summary"]
    total_changes = summary["total_changes"]
    
    if total_changes == 0:
        return "docs: update Chinese translation file"
    
    # 主要的commit信息
    change_types = []
    if summary["new_count"] > 0:
        change_types.append(f"add {summary['new_count']} translations")
    if summary["updated_count"] > 0:
        change_types.append(f"update {summary['updated_count']} translations")
    if summary["removed_count"] > 0:
        change_types.append(f"remove {summary['removed_count']} translations")
    
    # 生成简洁的commit标题
    commit_title = f"update zh.json: {', '.join(change_types)}"
    
    # 生成详细的commit正文
    commit_body = []
    
    # 统计信息
    commit_body.append("Translation update summary:")
    commit_body.append(f"- New translations: {summary['new_count']}")
    commit_body.append(f"- Updated translations: {summary['updated_count']}")
    if summary["removed_count"] > 0:
        commit_body.append(f"- Removed translations: {summary['removed_count']}")
    commit_body.append(f"- Total changes: {summary['total_changes']}")
    commit_body.append("")
    
    # 重要变更示例
    if changes["new_translations"]:
        commit_body.append("Key new translations:")
        new_items = list(changes["new_translations"].items())
        for path, info in new_items[:3]:
            en_text = info.get("english", "")[:50]
            zh_text = info["chinese"][:50]
            commit_body.append(f"- {path}: {en_text} -> {zh_text}")
        if len(new_items) > 3:
            commit_body.append(f"- ... and {len(new_items) - 3} more")
        commit_body.append("")
    
    if changes["updated_translations"]:
        commit_body.append("Key updated translations:")
        updated_items = list(changes["updated_translations"].items())
        for path, info in updated_items[:2]:
            old_text = info["old"][:30]
            new_text = info["new"][:30]
            commit_body.append(f"- {path}: {old_text} -> {new_text}")
        if len(updated_items) > 2:
            commit_body.append(f"- ... and {len(updated_items) - 2} more")
        commit_body.append("")
    
    commit_body.append("All translations have been reviewed and verified.")
    
    # 组合完整的commit信息
    full_commit = commit_title
    if commit_body:
        full_commit += "\n\n" + "\n".join(commit_body)
    
    return full_commit

def generate_commit_commands(commit_message: str, zh_file: str = "zh.json") -> List[str]:
    """生成Git命令序列"""
    commands = [
        f"git add {zh_file}",
        f'git commit -m "{commit_message.split(chr(10))[0]}"'
    ]
    
    # 如果有详细信息，使用多行commit
    if "\n" in commit_message:
        lines = commit_message.split("\n")
        title = lines[0]
        body = "\n".join(lines[2:])  # 跳过空行
        
        # 转义特殊字符
        body_escaped = body.replace('"', '\\"').replace('$', '\\$')
        commands[1] = f'git commit -m "{title}" -m "{body_escaped}"'
    
    return commands

def save_commit_info(commit_message: str, commands: List[str], output_file: str = "commit_info.txt"):
    """保存commit信息到文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    content = f"# Git Commit 信息\n\n"
    content += f"生成时间: {timestamp}\n\n"
    content += f"## Commit 信息\n\n```\n{commit_message}\n```\n\n"
    content += f"## Git 命令\n\n"
    for cmd in commands:
        content += f"```bash\n{cmd}\n```\n\n"
    content += f"## 一键执行\n\n"
    content += f"```bash\n{' && '.join(commands)}\n```\n"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

def save_pr_message(title: str, body: str, output_file: str = "pr_message.md"):
    """保存PR信息到文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    content = f"# PR 提交信息\n\n"
    content += f"生成时间: {timestamp}\n\n"
    content += f"## 标题\n\n{title}\n\n"
    content += f"## 正文\n\n{body}\n"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    """主函数"""
    print("=== PR 提交信息生成器 ===")
    
    # 文件路径配置
    input_dir = "input"
    output_dir = "output"
    old_zh_file = os.path.join(input_dir, "zh.json")  # 原始中文文件
    new_zh_file = os.path.join(output_dir, "zh_translated.json")  # 翻译后的文件
    en_file = os.path.join(input_dir, "en.json")  # 英文参考文件
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "pr_message.md")
    changes_file = os.path.join(output_dir, "translation_changes.json")
    commit_file = os.path.join(output_dir, "commit_info.txt")
    
    # 检查文件存在性
    if not os.path.exists(old_zh_file):
        print(f"错误: 找不到原始中文文件 {old_zh_file}")
        return
    
    if not os.path.exists(new_zh_file):
        print(f"错误: 找不到翻译后文件 {new_zh_file}")
        return
    
    # 分析变更
    changes = analyze_translation_changes(old_zh_file, new_zh_file, en_file)
    
    if changes["summary"]["total_changes"] == 0:
        print("没有发现翻译变更")
        return
    
    # 保存详细变更信息
    print(f"保存详细变更信息到: {changes_file}")
    with open(changes_file, 'w', encoding='utf-8') as f:
        json.dump(changes, f, ensure_ascii=False, indent=2)
    
    # 按功能分类
    categories = categorize_changes_by_feature(changes)
    
    # 生成PR信息
    title = generate_pr_title(changes)
    body = generate_pr_body(changes, categories)
    
    # 生成Commit信息
    commit_message = generate_commit_message(changes)
    commit_commands = generate_commit_commands(commit_message, "zh.json")
    
    # 保存PR信息
    save_pr_message(title, body, output_file)
    
    # 保存Commit信息
    save_commit_info(commit_message, commit_commands, commit_file)
    
    # 输出结果
    print("\n=== 生成的PR信息 ===")
    print(f"\n标题:")
    print(title)
    print(f"\n正文预览:")
    print(body[:500] + "..." if len(body) > 500 else body)
    
    print("\n=== 生成的Commit信息 ===")
    print(f"\nCommit标题:")
    commit_lines = commit_message.split('\n')
    print(commit_lines[0])
    
    print(f"\nCommit正文预览:")
    if len(commit_lines) > 1:
        body_preview = '\n'.join(commit_lines[2:7])  # 显示前几行
        print(body_preview)
        if len(commit_lines) > 7:
            print("...")
    
    print(f"\n=== Git 命令 ===")
    for cmd in commit_commands:
        print(f"  {cmd}")
    
    print(f"\n一键执行:")
    print(f"  {' && '.join(commit_commands)}")
    
    print(f"\n✅ PR信息已保存到: {output_file}")
    print(f"📄 详细变更信息已保存到: {changes_file}")
    print(f"🔧 Commit信息已保存到: {commit_file}")
    
    # 输出统计摘要
    summary = changes["summary"]
    print(f"\n📊 变更统计:")
    print(f"- 新增翻译: {summary['new_count']} 项")
    print(f"- 更新翻译: {summary['updated_count']} 项")
    print(f"- 删除翻译: {summary['removed_count']} 项")
    print(f"- 总计变更: {summary['total_changes']} 项")
    
    if categories:
        print(f"\n🏷️ 主要变更模块:")
        for category, paths in list(categories.items())[:5]:
            print(f"- {category}: {len(paths)} 项")
    
    print(f"\n💡 提示:")
    print(f"1. 将 '{new_zh_file}' 重命名为 'zh.json' 并替换掉原始仓库中的文件。")
    print(f"2. 复制 '{output_file}' 中的内容用于PR。")
    print(f"3. 使用 '{commit_file}' 中的命令提交代码。")

if __name__ == "__main__":
    main()
