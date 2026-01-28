import os
import mph
from pathlib import Path
import sys
import re

def translate_name(name):
    """
    将中文文件名翻译为符合 MATLAB 命名规范的英文名。
    规则：
    1. 只能包含字母、数字、下划线。
    2. 必须以字母开头。
    3. 长度不能超过 63 个字符 (尽量简洁)。
    """
    
    # 1. 基础映射词典
    translation_map = {
        # 顶级分类
        "开源模型": "OpenSource",
        "地震": "Seismic",
        "高密度": "HighDensity", 
        "雷达": "GPR", 
        
        # 属性描述
        "不同深度": "Var_Depth",
        "不同大小": "Var_Size",
        "不同隐患类型": "Var_HazardType",
        "不同水位": "Var_WaterLevel",
        "无隐患": "No_Hazard",
        "渗漏": "_Leakage",
        "复杂": "_Complex",
        "无限元": "_InfiniteElem",
        
        # 单位
        "3m": "_3m",
        "5m": "_5m",
    }
    
    result = name
    
    # 2. 处理括号内的范围，例如 (0-0) -> _Range_0_to_0_, (0.6-6) -> _Range_0pt6_to_6_
    def replace_range_content(match):
        content = match.group(1)
        # 处理小数点 0.6 -> 0pt6
        content = content.replace('.', 'pt')
        # 处理范围连接符 - -> _to_
        content = content.replace('-', '_to_')
        return f"_Range_{content}_"
    
    # 匹配中文或英文括号
    result = re.sub(r'[\(（](.*?)[\)）]', replace_range_content, result)
    
    # 3. 执行词典替换
    for cn, en in translation_map.items():
        result = result.replace(cn, en)
        
    # 4. 清理非法字符：将所有非字母、数字、下划线的字符替换为下划线
    # MATLAB 命名只允许 [a-zA-Z0-9_]
    result = re.sub(r'[^a-zA-Z0-9_]', '_', result)
    
    # 5. 处理重复的下划线
    result = re.sub(r'_+', '_', result)
    
    # 6. 去除首尾下划线
    result = result.strip('_')
    
    # 7. 强制以字母开头 (如果以数字开头，加前缀 Model_)
    if result and not result[0].isalpha():
        result = "Model_" + result
        
    return result

def process_comsol_files(source_dir, target_dir):
    """
    遍历源文件夹下的所有mph文件，清除解和网格后，
    另存为mph和m文件到目标文件夹（保持目录结构并翻译文件名）。
    """
    # 转换为绝对路径对象
    src_path = Path(source_dir).resolve()
    dst_path = Path(target_dir).resolve()

    if not src_path.exists():
        print(f"错误: 源文件夹 '{src_path}' 不存在")
        return

    # 启动 COMSOL 客户端 (需要已安装 COMSOL Multiphysics)
    print("正在启动 COMSOL 客户端...")
    try:
        client = mph.start()
    except Exception as e:
        print(f"启动 COMSOL 失败: {e}")
        print("请确保已安装 COMSOL Multiphysics 并且已安装 Python mph 库 (pip install mph)")
        return

    print(f"开始处理: {src_path} -> {dst_path}")

    # 遍历目录
    files_processed = 0
    for root, dirs, files in os.walk(src_path):
        for filename in files:
            if filename.lower().endswith(".mph"):
                file_path = Path(root) / filename
                
                # 计算相对路径
                rel_path = file_path.relative_to(src_path)
                
                # 翻译目录名和文件名
                translated_parts = [translate_name(part) for part in rel_path.parts]
                # 重新组合路径
                # 翻译目录部分 (每一层级都单独翻译)
                translated_parent_parts = [translate_name(part) for part in rel_path.parts[:-1]]
                
                # 单独处理文件名 (不含后缀)
                original_stem = rel_path.stem
                translated_stem = translate_name(original_stem)
                
                # 目标文件夹
                target_dir_path = dst_path.joinpath(*translated_parent_parts)
                target_dir_path.mkdir(parents=True, exist_ok=True)
                
                # 目标mph和m文件路径
                # 确保翻译后的文件名符合 .m 文件要求
                target_mph = target_dir_path / (translated_stem + ".mph")
                target_m = target_dir_path / (translated_stem + ".m")

                print(f"\n正在处理 [{files_processed + 1}]: {filename}")
                print(f"  源路径: {file_path}")
                print(f"  目标 (EN): {translated_stem}.mph / .m")
                
                try:
                    # 加载模型
                    model = client.load(file_path)
                    
                    # 获取底层的 Java 模型对象以便调用更多功能
                    jmodel = model.java

                    # 1. 清除所有解 (Solutions)
                    print("  清除解 (Solutions)...")
                    try:
                        # 1.1 先清除所有 Dataset (结果数据集)
                        # Dataset 往往引用了解，有时候即使解清除了，Dataset 还在引用（虽然是空的）
                        if hasattr(jmodel.result(), 'dataset'):
                            print("  清除 Datasets...")
                            for dset in jmodel.result().dataset().tags():
                                try:
                                    # 尝试清除数据集内容
                                    # 注意: 某些版本没有直接 clear 方法，这里主要依赖清除 Solution
                                    pass 
                                except:
                                    pass

                        # 1.2 清除 Solution
                        for tag in jmodel.sol().tags():
                            s_obj = jmodel.sol(tag)
                            # 优先使用 clearSolution (API 标准)
                            if hasattr(s_obj, 'clearSolution'):
                                s_obj.clearSolution()
                            
                            # 再次尝试 clear (某些旧版本或特殊对象)
                            if hasattr(s_obj, 'clear'):
                                try:
                                    s_obj.clear()
                                except:
                                    pass
                                    
                            # 1.3 深度清理: 检查 Solver Sequence 下的 Solution Feature (通常是 's1')
                            # 这里的逻辑比较复杂，通常 clearSolution 足够。
                            # 也就是所谓的 "Clear Solution" GUI 操作。
                                
                    except Exception as e:
                        print(f"  [警告] 清除解时遇到问题: {e}")

                    # 2. 清除所有网格 (Meshes)
                    print("  清除网格 (Meshes)...")
                    try:
                        for tag in jmodel.mesh().tags():
                            # 使用 clearMesh 方法清除网格数据
                            if hasattr(jmodel.mesh(tag), 'clearMesh'):
                                jmodel.mesh(tag).clearMesh()
                            else:
                                jmodel.mesh(tag).clear()
                    except Exception as e:
                        print(f"  [警告] 清除网格时遇到问题: {e}")

                    # 3. 重置历史记录 (Compact History) - 关键步骤：减小 M 文件体积
                    print("  重置历史记录...")
                    try:
                        jmodel.resetHist()
                    except Exception as e:
                        print(f"  [警告] 重置历史记录失败: {e}")

                    # 4. 另存为 MPH 文件
                    print(f"  保存 MPH: {target_mph.name}")
                    model.save(target_mph)

                    # 5. 另存为 M 文件 (MATLAB 代码)
                    print(f"  保存 M 文件 (MATLAB Code): {target_m.name}")
                    # 保存为 .m 后缀时，COMSOL 会自动将其保存为 MATLAB 格式的代码文件
                    model.save(target_m)
                    
                    files_processed += 1

                except Exception as e:
                    print(f"  [错误] 处理文件失败: {e}")
                
                finally:
                    # 卸载模型释放内存
                    if 'model' in locals():
                        try:
                            client.remove(model)
                        except:
                            pass

    print(f"\n全部完成! 共处理了 {files_processed} 个文件。")

if __name__ == "__main__":
    # 定义源文件夹和目标文件夹名称
    # 当前位于 e:\Model comsol 目录下
    CURRENT_DIR = Path(__file__).parent
    SOURCE_FOLDER = CURRENT_DIR / "开源模型"
    TARGET_FOLDER = CURRENT_DIR / "开源模型V2"

    process_comsol_files(SOURCE_FOLDER, TARGET_FOLDER)
