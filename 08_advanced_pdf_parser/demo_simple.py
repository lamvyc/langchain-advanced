#!/usr/bin/env python3
"""
PDF智能解析器 - 简化演示脚本
专注于表格提取和文本解析核心功能，不依赖OCR
"""

import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from table_extractor import TableExtractor
import fitz  # PyMuPDF

def create_demo_pdf():
    """创建一个演示PDF文件"""
    doc = fitz.open()
    page = doc.new_page()
    
    # 添加标题
    page.insert_text((72, 720), "PDF智能解析器演示文档", fontsize=16)
    page.insert_text((72, 690), "=" * 50)
    
    # 添加文本内容
    page.insert_text((72, 660), "这是一个包含表格和文本的测试文档")
    page.insert_text((72, 640), "演示了表格提取和文本解析功能")
    
    # 创建表格数据
    page.insert_text((72, 600), "项目信息表")
    table_y = 580
    headers = ["项目名称", "负责人", "状态", "进度"]
    rows = [
        ["PDF解析器", "张三", "完成", "100%"],
        ["混合检索", "李四", "进行中", "30%"],
        ["权限管理", "王五", "计划中", "0%"],
    ]
    
    # 绘制表头
    for i, header in enumerate(headers):
        page.insert_text((72 + i*120, table_y), header)
    
    # 绘制表格内容
    for row_idx, row in enumerate(rows):
        y = table_y - (row_idx + 1) * 20
        for col_idx, cell in enumerate(row):
            page.insert_text((72 + col_idx*120, y), cell)
    
    # 保存文件
    output_path = Path(__file__).parent / "demo_document.pdf"
    doc.save(str(output_path))
    doc.close()
    
    return output_path

def demo_table_extraction(pdf_path):
    """演示表格提取功能"""
    print("\n" + "="*60)
    print("📊 演示1: 表格提取功能")
    print("="*60)
    
    extractor = TableExtractor()
    
    # 提取所有表格
    results = extractor.extract_all(str(pdf_path))
    
    print(f"\n提取结果汇总:")
    print(f"  使用方法: {list(results.keys())}")
    total_tables = sum(len(tables) for tables in results.values())
    print(f"  提取表格总数: {total_tables}")
    
    # 显示详细信息
    for method, tables in results.items():
        print(f"\n  方法 [{method}]:")
        for i, table in enumerate(tables, 1):
            print(f"    表格 {i}: {table.shape[0]} 行 × {table.shape[1]} 列")
            if not table.empty:
                print(f"    前3行预览:")
                print(table.head(3).to_string(index=False))

def demo_text_extraction(pdf_path):
    """演示文本提取功能"""
    print("\n" + "="*60)
    print("📝 演示2: 文本提取功能")
    print("="*60)
    
    doc = fitz.open(str(pdf_path))
    
    print(f"\n文档信息:")
    print(f"  总页数: {len(doc)}")
    print(f"  文件大小: {pdf_path.stat().st_size / 1024:.2f} KB")
    
    # 提取文本
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        print(f"\n第 {page_num + 1} 页内容:")
        print("-" * 40)
        print(text.strip())
    
    doc.close()

def demo_smart_chunking(pdf_path):
    """演示智能分块功能"""
    print("\n" + "="*60)
    print("🧩 演示3: 智能分块功能")
    print("="*60)
    
    doc = fitz.open(str(pdf_path))
    
    chunks = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        # 按段落分块
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        for line in lines:
            if len(line) > 10:  # 过滤太短的行
                chunks.append({
                    'page': page_num + 1,
                    'content': line,
                    'length': len(line),
                    'type': 'text'
                })
    
    doc.close()
    
    print(f"\n分块结果:")
    print(f"  总块数: {len(chunks)}")
    print(f"  平均长度: {sum(c['length'] for c in chunks) / len(chunks):.1f} 字符")
    
    print(f"\n前5个文本块:")
    for i, chunk in enumerate(chunks[:5], 1):
        print(f"  {i}. [页{chunk['page']}] {chunk['content'][:50]}...")

def demo_comparison():
    """演示与基础方法的对比"""
    print("\n" + "="*60)
    print("⚖️  演示4: 功能对比")
    print("="*60)
    
    print("\n基础PDF解析 vs 智能解析器:")
    print()
    print("  功能对比表:")
    print("  ┌────────────────┬──────────┬──────────┐")
    print("  │ 功能           │ 基础方法 │ 智能解析 │")
    print("  ├────────────────┼──────────┼──────────┤")
    print("  │ 文本提取       │    ✓     │    ✓     │")
    print("  │ 表格提取       │    ✗     │    ✓     │")
    print("  │ 多方法融合     │    ✗     │    ✓     │")
    print("  │ 智能分块       │    ✗     │    ✓     │")
    print("  │ 版面分析       │    ✗     │    ✓     │")
    print("  │ 结构化输出     │    ✗     │    ✓     │")
    print("  └────────────────┴──────────┴──────────┘")
    
    print("\n  优势:")
    print("    ✓ 多种提取方法自动选择最佳结果")
    print("    ✓ 支持复杂表格结构")
    print("    ✓ 统一的数据格式输出")
    print("    ✓ 完善的错误处理")

def main():
    """主函数"""
    print("\n" + "🚀 " + "="*58)
    print("  PDF智能解析器 - 核心功能演示")
    print("  (简化版本 - 不依赖OCR)")
    print("="*60)
    
    # 创建演示PDF
    print("\n📄 正在创建演示文档...")
    pdf_path = create_demo_pdf()
    print(f"✓ 演示文档已创建: {pdf_path.name}")
    
    try:
        # 演示1: 表格提取
        demo_table_extraction(pdf_path)
        
        # 演示2: 文本提取
        demo_text_extraction(pdf_path)
        
        # 演示3: 智能分块
        demo_smart_chunking(pdf_path)
        
        # 演示4: 功能对比
        demo_comparison()
        
        print("\n" + "="*60)
        print("✅ 演示完成！")
        print("="*60)
        
        print("\n💡 提示:")
        print("  - 演示文档保存在: demo_document.pdf")
        print("  - 完整功能请参考: README.md")
        print("  - OCR功能需要解决依赖问题后使用")
        
    except Exception as e:
        print(f"\n❌ 演示过程出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理（可选）
        # pdf_path.unlink()
        pass

if __name__ == "__main__":
    main()
