import json
import os
from typing import Dict, Any, List, Tuple, Set

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

def get_all_paths(data: Dict[Any, Any], prefix: str = "") -> List[Tuple[str, Any]]:
    """递归获取JSON中所有的路径和值"""
    paths = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, (dict, list)):
                paths.extend(get_all_paths(value, current_path))
            else:
                paths.append((current_path, value))
    elif isinstance(data, list):
        for i, value in enumerate(data):
            current_path = f"{prefix}[{i}]"
            if isinstance(value, (dict, list)):
                paths.extend(get_all_paths(value, current_path))
            else:
                paths.append((current_path, value))
    
    return paths

def get_value_by_path(data: Dict[Any, Any], path: str) -> Any:
    """根据路径获取JSON中的值"""
    try:
        keys = path.split('.')
        current = data
        
        for key in keys:
            if '[' in key and ']' in key:
                # 处理数组索引
                key_name = key.split('[')[0]
                index = int(key.split('[')[1].split(']')[0])
                current = current[key_name][index]
            else:
                current = current[key]
        
        return current
    except (KeyError, IndexError, TypeError, ValueError):
        return None

def build_translation_dictionary(translated_items: Dict[str, Dict]) -> Dict[str, Set[str]]:
    """构建英文->中文翻译词典"""
    translation_dict = {}
    for path, info in translated_items.items():
        en_text = info["english"]
        zh_text = info["chinese"]
        
        if en_text not in translation_dict:
            translation_dict[en_text] = set()
        translation_dict[en_text].add(zh_text)
    
    return translation_dict

def analyze_translations(en_file: str, zh_file: str) -> Dict[str, Any]:
    """分析翻译状态"""
    print("正在加载文件...")
    en_data = load_json_file(en_file)
    zh_data = load_json_file(zh_file)
    
    if not en_data:
        print("英文文件加载失败")
        return {}
    
    if not zh_data:
        print("中文文件加载失败")
        return {}
    
    print("正在分析翻译状态...")
    en_paths = get_all_paths(en_data)
    
    translated = {}
    untranslated = {}
    
    total_count = len(en_paths)
    processed_count = 0
    
    for path, en_value in en_paths:
        processed_count += 1
        if processed_count % 100 == 0:
            print(f"处理进度: {processed_count}/{total_count}")
        
        zh_value = get_value_by_path(zh_data, path)
        
        if zh_value is not None and zh_value != en_value:
            # 已翻译（中文值存在且与英文不同）
            translated[path] = {
                "english": en_value,
                "chinese": zh_value
            }
        else:
            # 未翻译（中文值不存在或与英文相同）
            untranslated[path] = {
                "english": en_value,
                "status": "missing" if zh_value is None else "same_as_english"
            }
    
    # 构建翻译词典
    print("正在分析已翻译词汇...")
    translation_dict = build_translation_dictionary(translated)
    
    # 重新分析未翻译项目，标记那些已有翻译的
    potentially_translated = {}
    truly_untranslated = {}
    
    for path, info in untranslated.items():
        en_text = info["english"]
        if en_text in translation_dict:
            # 这个英文已经在其他地方翻译过了
            chinese_options = list(translation_dict[en_text])
            potentially_translated[path] = {
                "english": en_text,
                "status": info["status"],
                "existing_translations": chinese_options,
                "suggested_translation": chinese_options[0] if chinese_options else None
            }
        else:
            # 真的没有翻译过
            truly_untranslated[path] = info
    
    result = {
        "summary": {
            "total_items": total_count,
            "translated_count": len(translated),
            "untranslated_count": len(untranslated),
            "potentially_translated_count": len(potentially_translated),
            "truly_untranslated_count": len(truly_untranslated),
            "translation_rate": f"{len(translated) / total_count * 100:.2f}%",
            "potential_rate": f"{(len(translated) + len(potentially_translated)) / total_count * 100:.2f}%"
        },
        "translated": translated,
        "untranslated": untranslated,
        "potentially_translated": potentially_translated,
        "truly_untranslated": truly_untranslated,
        "translation_dictionary": {k: list(v) for k, v in translation_dict.items()}
    }
    
    return result

def save_untranslated_entries(untranslated: Dict[str, Any], output_file: str):
    """保存未翻译的条目到文件"""
    # 创建一个更简洁的格式，只包含英文原文
    simplified = {}
    for path, info in untranslated.items():
        simplified[path] = info["english"]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(simplified, f, ensure_ascii=False, indent=2)

def save_potentially_translated_entries(potentially_translated: Dict[str, Any], output_file: str):
    """保存可能已翻译的条目到文件"""
    simplified = {}
    for path, info in potentially_translated.items():
        simplified[path] = {
            "english": info["english"],
            "suggested_translation": info["suggested_translation"],
            "all_existing_translations": info["existing_translations"]
        }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(simplified, f, ensure_ascii=False, indent=2)

def main():
    """主函数"""
    print("=== Obsidian 翻译状态分析工具 ===")
    
    # 文件路径
    en_file = "en.json"
    zh_file = "zh.json"
    output_file = "untranslated_entries.json"
    report_file = "translation_report.json"
    potentially_file = "potentially_translated_entries.json"
    
    # 检查文件是否存在
    if not os.path.exists(en_file):
        print(f"错误: 找不到英文文件 {en_file}")
        return
    
    if not os.path.exists(zh_file):
        print(f"错误: 找不到中文文件 {zh_file}")
        return
    
    # 分析翻译状态
    result = analyze_translations(en_file, zh_file)
    
    if not result:
        print("分析失败")
        return
    
    # 输出统计信息
    summary = result["summary"]
    print("\n=== 翻译统计 ===")
    print(f"总配置项数: {summary['total_items']}")
    print(f"已翻译数量: {summary['translated_count']}")
    print(f"未翻译数量: {summary['untranslated_count']}")
    print(f"  - 可能已翻译过的: {summary['potentially_translated_count']}")
    print(f"  - 真的没翻译的: {summary['truly_untranslated_count']}")
    print(f"翻译完成率: {summary['translation_rate']}")
    print(f"潜在完成率: {summary['potential_rate']}")
    
    # 保存完整报告
    print(f"\n正在保存完整报告到: {report_file}")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 保存未翻译条目
    print(f"正在保存未翻译条目到: {output_file}")
    save_untranslated_entries(result["untranslated"], output_file)
    
    # 保存可能已翻译的条目
    print(f"正在保存可能已翻译的条目到: {potentially_file}")
    save_potentially_translated_entries(result["potentially_translated"], potentially_file)
    
    # 显示可能已翻译的例子
    print("\n=== 可能已翻译过的条目示例 ===")
    potentially_items = list(result["potentially_translated"].items())
    for i, (path, info) in enumerate(potentially_items[:10]):
        suggested = info["suggested_translation"]
        print(f"{i+1}. {path}")
        print(f"   英文: {info['english']}")
        print(f"   建议翻译: {suggested}")
        if len(info["existing_translations"]) > 1:
            other_translations = [t for t in info["existing_translations"] if t != suggested]
            print(f"   其他翻译: {', '.join(other_translations)}")
    
    if len(potentially_items) > 10:
        print(f"... 还有 {len(potentially_items) - 10} 个可能已翻译的条目")
    
    # 显示真的未翻译的例子
    print("\n=== 真的没翻译的条目示例 ===")
    truly_untranslated_items = list(result["truly_untranslated"].items())
    for i, (path, info) in enumerate(truly_untranslated_items[:10]):
        status = "缺失" if info["status"] == "missing" else "与英文相同"
        print(f"{i+1}. {path} -> {info['english']} ({status})")
    
    if len(truly_untranslated_items) > 10:
        print(f"... 还有 {len(truly_untranslated_items) - 10} 个真的没翻译条目")
    
    print(f"\n分析完成！")
    print(f"- 查看 {output_file} 获取所有未翻译条目")
    print(f"- 查看 {potentially_file} 获取可能已翻译的条目")
    print(f"- 查看 {report_file} 获取完整分析报告")
    print(f"\n📝 下一步操作:")
    print(f"1. 翻译完成后运行 pre.py 合并翻译")
    print(f"2. 运行 generate_pr_message.py 生成PR和Commit信息")

if __name__ == "__main__":
    main()
