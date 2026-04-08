import pandas as pd
import os
from pathlib import Path

# ==========================================
# 步骤1：找到所有Excel文件
# ==========================================

def find_all_excel_files(folder_path='.'):
    """找到文件夹中的所有Excel文件"""
    excel_files = []
    
    for file in os.listdir(folder_path):
        if file.endswith('.xlsx') or file.endswith('.xls'):
            full_path = os.path.join(folder_path, file)
            excel_files.append((file, full_path))
    
    return sorted(excel_files)

# ==========================================
# 步骤2：检查每个文件的内容
# ==========================================

def explore_excel_file(file_path, file_name):
    """
    读取Excel文件并显示其结构
    """
    print(f"\n{'='*70}")
    print(f"📄 文件: {file_name}")
    print(f"{'='*70}")
    
    try:
        # 读取所有sheet名
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names
        
        print(f"📊 Sheet数量: {len(sheet_names)}")
        print(f"   Sheet名称: {sheet_names}")
        
        # 对每个sheet显示信息
        for sheet in sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet)
            print(f"\n  Sheet: '{sheet}'")
            print(f"    行数: {len(df)}")
            print(f"    列数: {len(df.columns)}")
            print(f"    列名: {list(df.columns)}")
            print(f"    数据类型:\n{df.dtypes}")
            print(f"\n    前3行预览:")
            print(df.head(3).to_string())
            
    except Exception as e:
        print(f"❌ 错误: {str(e)}")

# ==========================================
# 步骤3：主程序
# ==========================================

def main():
    print("\n" + "="*70)
    print("🔍 数据文件探索工具")
    print("="*70)
    
    # 找到所有文件
    excel_files = find_all_excel_files()
    
    print(f"\n✓ 找到 {len(excel_files)} 个Excel文件：\n")
    for i, (file_name, _) in enumerate(excel_files, 1):
        print(f"  {i}. {file_name}")
    
    # 逐个探索文件
    for file_name, file_path in excel_files:
        explore_excel_file(file_path, file_name)
    
    print(f"\n\n{'='*70}")
    print("✅ 探索完成！")
    print("="*70)
    print("\n下一步：")
    print("1. 查看上面的输出")
    print("2. 告诉我：")
    print("   - 哪个文件是'主数据文件'（包含所有频道）")
    print("   - 哪个文件包含时间序列数据")
    print("   - 哪个文件包含评论数据")
    print("   - 缺失什么数据")

if __name__ == '__main__':
    main()