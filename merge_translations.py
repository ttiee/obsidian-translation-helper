import json
import copy
import os

def find_untranslated(obj, path=""):
    untranslated = {}

    if isinstance(obj, dict):
        for key, value in obj.items():
            new_path = f"{path}.{key}" if path else key
            if isinstance(value, (dict, list)):
                result = find_untranslated(value, new_path)
                if result:
                    untranslated.update(result)
            elif isinstance(value, str):
                # 判断是否为未翻译的英文（纯 ASCII 且不含中文）
                key_simple = key.lower().replace("-", "").replace("_", "")
                val_simple = value.lower().replace(" ", "").replace("-", "").replace("_", "")
                is_ascii = val_simple.isascii()
                has_chinese = any("\u4e00" <= c <= "\u9fff" for c in value)
                if not has_chinese and (val_simple == key_simple or is_ascii):
                    untranslated[new_path] = value
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_path = f"{path}[{i}]"
            if isinstance(item, (dict, list)):
                result = find_untranslated(item, new_path)
                if result:
                    untranslated.update(result)
            elif isinstance(item, str):
                has_chinese = any("\u4e00" <= c <= "\u9fff" for c in item)
                if not has_chinese and item.isascii():
                    untranslated[new_path] = item
    return untranslated

def set_nested_value(obj, path, value):
    """根据路径设置嵌套对象的值"""
    keys = []
    temp_path = path
    
    # 解析路径，处理数组索引
    while temp_path:
        if '[' in temp_path:
            key_part = temp_path[:temp_path.index('[')]
            if key_part:
                keys.append(key_part)
            
            bracket_start = temp_path.index('[')
            bracket_end = temp_path.index(']')
            index = int(temp_path[bracket_start+1:bracket_end])
            keys.append(index)
            
            temp_path = temp_path[bracket_end+1:]
            if temp_path.startswith('.'):
                temp_path = temp_path[1:]
        elif '.' in temp_path:
            next_dot = temp_path.index('.')
            keys.append(temp_path[:next_dot])
            temp_path = temp_path[next_dot+1:]
        else:
            keys.append(temp_path)
            break
    
    # 设置值
    current = obj
    for i, key in enumerate(keys[:-1]):
        if isinstance(key, int):
            current = current[key]
        else:
            current = current[key]
    
    final_key = keys[-1]
    if isinstance(final_key, int):
        current[final_key] = value
    else:
        current[final_key] = value

def merge_translations(original_data, translations):
    """将翻译结果合并回原始数据"""
    result = copy.deepcopy(original_data)
    
    for path, translated_value in translations.items():
        set_nested_value(result, path, translated_value)
    
    return result


def main():
    """主函数：将手动翻译的文件合并到中文语言文件中。"""
    print("=== 开始合并翻译文件 ===")

    # 定义文件路径
    input_dir = "input"
    output_dir = "output"
    original_zh_file = os.path.join(input_dir, "zh.json")
    manual_translations_file = os.path.join(input_dir, "manual_translations.json")
    merged_file = os.path.join(output_dir, "zh_translated.json")

    # 确保输入输出目录存在
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # 检查所需文件是否存在
    if not os.path.exists(original_zh_file):
        print(f"❌ 错误: 找不到原始中文文件 {original_zh_file}")
        return

    if not os.path.exists(manual_translations_file):
        print(f"❌ 错误: 找不到手动翻译文件 {manual_translations_file}")
        print(f"💡 提示: 请先运行 'python analyze_translations.py' 生成待翻译文件，")
        print(f"   完成后将其复制并重命名为 {manual_translations_file} 并放入 '{input_dir}/' 目录。")
        return

    # 读取原始中文数据
    print(f"📖 正在读取原始文件: {original_zh_file}")
    with open(original_zh_file, "r", encoding="utf-8") as f:
        original_data = json.load(f)

    # 读取手动翻译的数据
    print(f"📖 正在读取翻译文件: {manual_translations_file}")
    with open(manual_translations_file, "r", encoding="utf-8") as f:
        translated_entries = json.load(f)

    # 合并翻译
    print("🔄 正在合并翻译...")
    final_data = merge_translations(original_data, translated_entries)

    # 保存最终结果
    print(f"💾 正在保存合并后的文件到: {merged_file}")
    with open(merged_file, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent="\t")

    print(f"\n🎉 合并完成！最终文件已保存为 {merged_file}")
    print("\n💡 下一步: 运行 'python generate_pr_message.py' 生成PR和Commit信息。")


if __name__ == "__main__":
    main()
