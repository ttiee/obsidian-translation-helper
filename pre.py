import json
import copy

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

# 读取原始文件
with open("zh.json", "r", encoding="utf-8") as f:
    original_data = json.load(f)

# 提取未翻译条目
untranslated_entries = find_untranslated(original_data)

# 保存原始数据结构（用于后续合并）
with open("original_structure.json", "w", encoding="utf-8") as f:
    json.dump(original_data, f, ensure_ascii=False, indent=2)

# 输出待翻译文件
with open("untranslated_entries.json", "w", encoding="utf-8") as f:
    json.dump(untranslated_entries, f, ensure_ascii=False, indent=2)

print(f"✅ 提取完成，找到 {len(untranslated_entries)} 个待翻译条目")
print("📁 已保存文件:")
print("  - untranslated_entries.json (待翻译)")
print("  - original_structure.json (原始结构)")
print("\n📝 翻译步骤:")
print("1. 翻译 untranslated_entries.json 中的内容")
print("2. 将翻译结果保存为 translated_entries.json")
print("3. 运行合并脚本生成最终文件")
print("4. 运行 generate_pr_message.py 生成PR提交信息")

# 如果存在翻译文件，自动合并
try:
    with open("translated_entries.json", "r", encoding="utf-8") as f:
        translated_entries = json.load(f)
    
    # 合并翻译结果
    final_data = merge_translations(original_data, translated_entries)
    
    # 保存最终结果
    with open("zh_translated.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent="\t")
    
    print("\n🎉 发现翻译文件，已自动合并为 zh_translated.json")
    print("\n💡 提示: 运行 'python generate_pr_message.py' 生成PR提交信息")
    
except FileNotFoundError:
    print("\n💡 翻译完成后，请将结果保存为 translated_entries.json，然后重新运行此脚本进行合并")
