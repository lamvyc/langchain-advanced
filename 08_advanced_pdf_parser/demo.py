"""
PDF 智能解析器 - 完整演示脚本
展示表格提取、OCR 识别、版面分析的完整功能
"""

import sys
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from table_extractor import TableExtractor
from image_ocr import ImageOCR
from layout_analyzer import LayoutAnalyzer
from advanced_loader import AdvancedPDFLoader, compare_with_basic_loader


def demo_table_extraction():
    """演示表格提取功能"""
    print("\n" + "="*70)
    print("📋 演示 1: 表格提取")
    print("="*70)
    
    extractor = TableExtractor()
    test_file = "test_data/complex_table.pdf"
    
    if not Path(test_file).exists():
        print(f"⚠️ 测试文件不存在: {test_file}")
        print("请准备包含表格的 PDF 文件")
        return
    
    # 提取表格
    results = extractor.extract_all(test_file)
    
    # 展示结果
    for method, tables in results.items():
        print(f"\n📊 方法: {method}")
        print(f"   提取表格数: {len(tables)}")
        
        for i, df in enumerate(tables[:2]):  # 只显示前 2 个表格
            print(f"\n   表格 {i+1} 预览:")
            print(f"   形状: {df.shape}")
            print(df.head(3).to_string(index=False))
    
    # 保存表格
    if results:
        all_tables = [table for tables in results.values() for table in tables]
        saved = extractor.save_tables(all_tables, "output/tables", prefix="demo")
        print(f"\n✅ 已保存 {len(saved)} 个表格到 output/tables/")


def demo_ocr():
    """演示 OCR 识别功能"""
    print("\n" + "="*70)
    print("🔍 演示 2: OCR 图片文字识别")
    print("="*70)
    
    ocr = ImageOCR(lang='ch')
    test_file = "test_data/scanned_doc.pdf"
    
    if not Path(test_file).exists():
        print(f"⚠️ 测试文件不存在: {test_file}")
        print("请准备扫描版或包含图片的 PDF 文件")
        return
    
    # 提取图片
    images = ocr.extract_images_from_pdf(test_file)
    print(f"\n📷 提取图片数: {len(images)}")
    
    if images:
        # 保存图片
        saved = ocr.save_images(images[:5], "output/images", prefix="demo")
        print(f"💾 已保存 {len(saved)} 张图片到 output/images/")
    
    # OCR 识别
    results = ocr.process_pdf(test_file, confidence_threshold=0.6)
    
    print(f"\n🔤 OCR 识别结果:")
    for page_num, texts in list(results.items())[:2]:  # 只显示前 2 页
        print(f"\n   第 {page_num} 页（前 3 行）:")
        for text in texts[:3]:
            print(f"   - {text}")
    
    # 导出结果
    if results:
        ocr.export_ocr_results(results, "output/demo_ocr_results.txt")
        print(f"\n✅ OCR 结果已导出到 output/demo_ocr_results.txt")


def demo_layout_analysis():
    """演示版面分析功能"""
    print("\n" + "="*70)
    print("📐 演示 3: 版面分析（多栏布局检测）")
    print("="*70)
    
    analyzer = LayoutAnalyzer(column_threshold=50.0)
    test_file = "test_data/multi_column.pdf"
    
    if not Path(test_file).exists():
        print(f"⚠️ 测试文件不存在: {test_file}")
        print("请准备多栏布局的 PDF 文件")
        return
    
    # 执行版面分析
    result = analyzer.analyze_layout(test_file)
    
    # 显示摘要
    summary = result['summary']
    print(f"\n📊 版面分析摘要:")
    print(f"   总文本块: {summary['total_blocks']}")
    print(f"   页数: {summary['pages']}")
    print(f"   最大列数: {summary['max_columns']}")
    print(f"   文本块类型:")
    for block_type, count in summary['block_types'].items():
        print(f"      - {block_type}: {count}")
    
    # 显示文本块示例
    print(f"\n📄 文本块示例（前 3 个）:")
    for i, block in enumerate(result['blocks'][:3]):
        print(f"\n   {i+1}. [{block.block_type.upper()}] 第{block.page}页 列{block.column}")
        print(f"      字体: {block.font_name} ({block.font_size:.1f}pt)")
        print(f"      {block.text[:80]}...")
    
    # 导出结果
    analyzer.export_to_text(result['blocks'], "output/demo_layout_analysis.txt")
    print(f"\n✅ 版面分析结果已导出到 output/demo_layout_analysis.txt")


def demo_advanced_loader():
    """演示高级加载器（整合所有功能）"""
    print("\n" + "="*70)
    print("🚀 演示 4: 高级加载器（整合功能）")
    print("="*70)
    
    # 查找可用的测试文件
    test_files = [
        "test_data/complex_table.pdf",
        "test_data/scanned_doc.pdf",
        "test_data/multi_column.pdf"
    ]
    
    available_files = [f for f in test_files if Path(f).exists()]
    
    if not available_files:
        print("⚠️ 没有找到测试文件，请准备以下任一文件:")
        for f in test_files:
            print(f"   - {f}")
        return
    
    test_file = available_files[0]
    print(f"\n📄 测试文件: {test_file}")
    
    # 创建高级加载器
    loader = AdvancedPDFLoader(
        enable_table_extraction=True,
        enable_ocr=True,
        enable_layout_analysis=True,
        ocr_lang='ch'
    )
    
    # 对比基础加载器
    try:
        print("\n" + "-"*70)
        compare_with_basic_loader(test_file)
        print("-"*70)
    except Exception as e:
        print(f"⚠️ 基础加载器对比失败: {e}")
    
    # 加载 PDF
    result = loader.load(test_file)
    
    # 显示结果摘要
    print(f"\n📊 解析结果摘要:")
    print(f"   文本长度: {len(result['text'])} 字符")
    print(f"   提取表格: {len(result['tables'])} 个")
    print(f"   OCR 页数: {len(result['ocr_results'])} 页")
    if result['layout']:
        print(f"   版面信息: {result['layout']['summary']}")
    
    # 显示文本预览
    print(f"\n📝 文本内容预览（前 300 字符）:")
    print(result['text'][:300] + "...")
    
    # 导出所有结果
    loader.export_results(result, "output/advanced_results")
    print(f"\n✅ 所有结果已导出到 output/advanced_results/")
    
    # 演示分块功能（用于 RAG）
    chunks = loader.load_and_split(test_file, chunk_size=500, chunk_overlap=100)
    print(f"\n📦 文本分块（用于 RAG）:")
    print(f"   块数量: {len(chunks)}")
    print(f"   块大小: 500 字符")
    print(f"   重叠: 100 字符")
    
    if chunks:
        print(f"\n   第 1 块预览:")
        print(f"   {chunks[0]['text'][:150]}...")


def create_test_data_info():
    """创建测试数据说明文件"""
    info_file = "test_data/README.md"
    
    content = """# 测试数据说明

本目录用于存放 PDF 智能解析器的测试文件。

## 需要准备的测试文件

### 1. complex_table.pdf
- **用途**: 测试表格提取功能
- **要求**: 包含复杂表格（合并单元格、多级表头、无边框表格等）
- **推荐来源**: 
  - 财务报表
  - 数据统计表
  - 学术论文中的表格

### 2. scanned_doc.pdf
- **用途**: 测试 OCR 识别功能
- **要求**: 扫描版 PDF 或包含图片文字的文档
- **推荐来源**:
  - 扫描的纸质文档
  - 包含图表和图片的演示文稿
  - 截图拼接的 PDF

### 3. multi_column.pdf
- **用途**: 测试版面分析功能
- **要求**: 多栏布局（如报纸、杂志、论文）
- **推荐来源**:
  - 学术论文（IEEE、ACM 格式）
  - 期刊文章
  - 报纸排版

## 如何准备测试数据

### 方法 1: 下载示例（推荐）
从以下资源下载示例 PDF：
- arXiv 论文（多栏布局）: https://arxiv.org/
- 公开数据集（表格）: Kaggle、UCI ML Repository
- 公开文档（OCR）: 互联网档案馆

### 方法 2: 自己创建
使用 Microsoft Word、Google Docs 或 LaTeX 创建测试文档，然后导出为 PDF。

### 方法 3: 使用现有文件
如果你有符合要求的 PDF 文件，直接复制到本目录并重命名即可。

## 注意事项

1. 确保测试文件不包含敏感信息
2. 文件大小建议 < 10MB
3. 文件名必须与上述要求一致
4. 如果只有部分测试文件，演示脚本会自动跳过缺失的测试

## 快速开始

```bash
# 1. 准备测试文件（复制到本目录）
cp /path/to/your/pdf/files/*.pdf test_data/

# 2. 重命名文件（可选）
mv your_file1.pdf complex_table.pdf
mv your_file2.pdf scanned_doc.pdf
mv your_file3.pdf multi_column.pdf

# 3. 运行演示脚本
cd ..
python demo.py
```

## 输出目录

解析结果将保存在 `output/` 目录下：
- `output/tables/` - 提取的表格（CSV 格式）
- `output/images/` - 提取的图片
- `output/demo_ocr_results.txt` - OCR 识别结果
- `output/demo_layout_analysis.txt` - 版面分析结果
- `output/advanced_results/` - 高级加载器的完整输出
"""
    
    # 创建测试数据目录
    Path("test_data").mkdir(exist_ok=True)
    
    # 保存说明文件
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已创建测试数据说明: {info_file}")


def main():
    """主函数：运行所有演示"""
    print("\n" + "="*70)
    print("🎯 PDF 智能解析器 - 完整演示")
    print("="*70)
    print("\n本演示将展示以下功能:")
    print("  1. 表格提取（简单 + 复杂表格）")
    print("  2. OCR 图片文字识别")
    print("  3. 版面分析（多栏布局检测）")
    print("  4. 高级加载器（整合所有功能）")
    
    # 创建输出目录
    Path("output").mkdir(exist_ok=True)
    
    # 创建测试数据说明
    create_test_data_info()
    
    # 检查测试数据
    test_files = [
        "test_data/complex_table.pdf",
        "test_data/scanned_doc.pdf",
        "test_data/multi_column.pdf"
    ]
    
    available = sum(1 for f in test_files if Path(f).exists())
    
    if available == 0:
        print("\n⚠️ 警告: 未找到任何测试文件")
        print("请查看 test_data/README.md 了解如何准备测试数据")
        print("\n演示将继续，但部分功能无法展示")
    else:
        print(f"\n✅ 找到 {available}/3 个测试文件")
    
    # 运行各项演示
    try:
        demo_table_extraction()
    except Exception as e:
        print(f"\n❌ 表格提取演示失败: {e}")
    
    try:
        demo_ocr()
    except Exception as e:
        print(f"\n❌ OCR 演示失败: {e}")
    
    try:
        demo_layout_analysis()
    except Exception as e:
        print(f"\n❌ 版面分析演示失败: {e}")
    
    try:
        demo_advanced_loader()
    except Exception as e:
        print(f"\n❌ 高级加载器演示失败: {e}")
    
    # 总结
    print("\n" + "="*70)
    print("🎉 演示完成！")
    print("="*70)
    print("\n📂 输出文件位置:")
    print("   - output/tables/          (提取的表格)")
    print("   - output/images/          (提取的图片)")
    print("   - output/*.txt            (文本结果)")
    print("   - output/advanced_results/ (完整解析结果)")
    print("\n📖 下一步:")
    print("   1. 查看输出文件，了解各模块的效果")
    print("   2. 准备更多测试数据，测试不同场景")
    print("   3. 集成到你的 RAG 系统中")
    print("   4. 根据需求调整参数（chunk_size、阈值等）")


if __name__ == "__main__":
    main()