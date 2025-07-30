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
    print("=== Obsidian 翻译状态分析与准备工具 ===")
    
    # 文件路径
    en_file = "input/en.json"
    zh_file = "input/zh.json"
    
    # 创建输出目录
    output_dir = "output_analyze"
    os.makedirs(output_dir, exist_ok=True)
    
    # 输出文件路径
    report_file = os.path.join(output_dir, "translation_report.json")
    untranslated_file = os.path.join(output_dir, "untranslated_entries.json")
    potentially_file = os.path.join(output_dir, "potentially_translated_entries.json")
    
    # 检查文件是否存在
    if not os.path.exists(en_file):
        print(f"❌ 错误: 找不到英文文件 {en_file}")
        return
    
    if not os.path.exists(zh_file):
        print(f"❌ 错误: 找不到中文文件 {zh_file}")
        return
    
    # 分析翻译状态
    result = analyze_translations(en_file, zh_file)
    
    if not result:
        print("分析失败")
        return
    
    # 输出统计信息
    summary = result["summary"]
    print("\n📊 翻译统计摘要:")
    print(f"  - 总条目: {summary['total_items']}")
    print(f"  - 已翻译: {summary['translated_count']} ({summary['translation_rate']})")
    print(f"  - 未翻译: {summary['untranslated_count']}")
    print(f"    - 纯未翻译: {summary['truly_untranslated_count']}")
    print(f"    - 可能已翻译: {summary['potentially_translated_count']}")
    
    # 保存完整报告
    print(f"\n💾 正在保存完整报告到: {report_file}")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 保存未翻译条目
    print(f"💾 正在保存【所有未翻译】条目到: {untranslated_file}")
    save_untranslated_entries(result["untranslated"], untranslated_file)
    
    # 保存可能已翻译的条目
    print(f"💾 正在保存【可能已翻译】的条目到: {potentially_file}")
    save_potentially_translated_entries(result["potentially_translated"], potentially_file)
    
    print(f"\n✅ 分析完成！")
    print(f"\n📝 下一步操作:")
    print(f"1. 在 '{output_dir}/' 目录下找到 untranslated_entries.json 和 potentially_translated_entries.json。")
    print(f"2. 对这些文件中的英文值进行翻译。")
    print(f"3. 将所有翻译好的键值对合并到一个文件中，并将其命名为 'manual_translations.json' 放入 'input/' 目录。")
    print(f"4. 运行 'python merge_translations.py' 来合并您的翻译。")

if __name__ == "__main__":
    main()
