"""
高级 PDF 加载器
整合表格提取、OCR 识别、版面分析，提供统一的加载接口
"""

from typing import List, Dict, Optional
from pathlib import Path
import logging

from table_extractor import TableExtractor
from image_ocr import ImageOCR
from layout_analyzer import LayoutAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedPDFLoader:
    """高级 PDF 加载器"""
    
    def __init__(self, 
                 enable_table_extraction: bool = True,
                 enable_ocr: bool = True,
                 enable_layout_analysis: bool = True,
                 ocr_lang: str = 'ch'):
        """
        初始化高级加载器
        
        Args:
            enable_table_extraction: 是否启用表格提取
            enable_ocr: 是否启用 OCR
            enable_layout_analysis: 是否启用版面分析
            ocr_lang: OCR 语言（'ch': 中文, 'en': 英文）
        """
        self.enable_table_extraction = enable_table_extraction
        self.enable_ocr = enable_ocr
        self.enable_layout_analysis = enable_layout_analysis
        
        # 初始化各模块
        if enable_table_extraction:
            self.table_extractor = TableExtractor()
            logger.info("✅ 表格提取模块已加载")
        
        if enable_ocr:
            self.ocr = ImageOCR(lang=ocr_lang)
            logger.info("✅ OCR 模块已加载")
        
        if enable_layout_analysis:
            self.layout_analyzer = LayoutAnalyzer()
            logger.info("✅ 版面分析模块已加载")
    
    def load(self, pdf_path: str) -> Dict:
        """
        加载并解析 PDF 文档
        
        Args:
            pdf_path: PDF 文件路径
            
        Returns:
            解析结果字典，包含以下字段：
            - text: 文本内容（按阅读顺序）
            - tables: 提取的表格列表
            - ocr_results: OCR 识别结果
            - layout: 版面分析结果
            - metadata: 元数据
        """
        logger.info(f"🚀 开始加载 PDF: {pdf_path}")
        
        if not Path(pdf_path).exists():
            logger.error(f"❌ 文件不存在: {pdf_path}")
            return {}
        
        result = {
            "text": "",
            "tables": [],
            "ocr_results": {},
            "layout": {},
            "metadata": {
                "file_path": pdf_path,
                "file_name": Path(pdf_path).name
            }
        }
        
        # 1. 版面分析（获取结构化文本）
        if self.enable_layout_analysis:
            logger.info("📊 执行版面分析...")
            layout_result = self.layout_analyzer.analyze_layout(pdf_path)
            result["layout"] = layout_result
            
            # 提取按阅读顺序排列的文本
            blocks = layout_result.get("blocks", [])
            text_parts = []
            for block in blocks:
                if block.block_type in ["title", "body"]:
                    text_parts.append(block.text)
            
            result["text"] = "\n\n".join(text_parts)
            logger.info(f"✅ 提取文本 {len(result['text'])} 字符")
        
        # 2. 表格提取
        if self.enable_table_extraction:
            logger.info("📋 执行表格提取...")
            table_results = self.table_extractor.extract_all(pdf_path)
            
            # 合并所有方法提取的表格
            all_tables = []
            for method, tables in table_results.items():
                all_tables.extend(tables)
            
            result["tables"] = all_tables
            logger.info(f"✅ 提取 {len(all_tables)} 个表格")
        
        # 3. OCR 识别（针对扫描版或图片）
        if self.enable_ocr:
            logger.info("🔍 执行 OCR 识别...")
            ocr_results = self.ocr.process_pdf(pdf_path, confidence_threshold=0.6)
            result["ocr_results"] = ocr_results
            
            # 如果文本为空，尝试使用 OCR 结果
            if not result["text"].strip() and ocr_results:
                ocr_text_parts = []
                for page_num in sorted(ocr_results.keys()):
                    ocr_text_parts.extend(ocr_results[page_num])
                result["text"] = "\n".join(ocr_text_parts)
                logger.info(f"✅ 使用 OCR 文本 {len(result['text'])} 字符")
        
        logger.info(f"🎉 PDF 加载完成")
        return result
    
    def load_and_split(self, 
                      pdf_path: str, 
                      chunk_size: int = 1000, 
                      chunk_overlap: int = 200) -> List[Dict]:
        """
        加载 PDF 并分块（适用于 RAG 系统）
        
        Args:
            pdf_path: PDF 文件路径
            chunk_size: 块大小（字符数）
            chunk_overlap: 块重叠大小
            
        Returns:
            文本块列表，每个块包含 text 和 metadata
        """
        # 加载 PDF
        result = self.load(pdf_path)
        
        if not result.get("text"):
            logger.warning("⚠️ 未提取到文本内容")
            return []
        
        # 简单分块（按字符数）
        text = result["text"]
        chunks = []
        
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "source": result["metadata"]["file_name"],
                    "chunk_id": len(chunks),
                    "start_char": start,
                    "end_char": end
                }
            })
            
            start = end - chunk_overlap
        
        logger.info(f"✅ 分块完成，共 {len(chunks)} 个块")
        return chunks
    
    def batch_load(self, pdf_paths: List[str]) -> List[Dict]:
        """
        批量加载多个 PDF 文件
        
        Args:
            pdf_paths: PDF 文件路径列表
            
        Returns:
            解析结果列表
        """
        results = []
        
        for i, pdf_path in enumerate(pdf_paths):
            logger.info(f"📂 处理文件 {i+1}/{len(pdf_paths)}: {pdf_path}")
            try:
                result = self.load(pdf_path)
                results.append(result)
            except Exception as e:
                logger.error(f"❌ 处理失败: {e}")
                continue
        
        logger.info(f"✅ 批量处理完成，成功 {len(results)}/{len(pdf_paths)} 个文件")
        return results
    
    def export_results(self, result: Dict, output_dir: str):
        """
        导出解析结果到文件
        
        Args:
            result: 解析结果
            output_dir: 输出目录
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        file_name = result["metadata"]["file_name"].replace(".pdf", "")
        
        # 1. 导出文本
        text_file = output_path / f"{file_name}_text.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(result["text"])
        logger.info(f"💾 文本已保存: {text_file}")
        
        # 2. 导出表格
        if result["tables"]:
            self.table_extractor.save_tables(
                result["tables"], 
                str(output_path / "tables"),
                prefix=file_name
            )
        
        # 3. 导出 OCR 结果
        if result["ocr_results"]:
            ocr_file = output_path / f"{file_name}_ocr.txt"
            self.ocr.export_ocr_results(result["ocr_results"], str(ocr_file))
        
        # 4. 导出版面分析结果
        if result["layout"] and result["layout"].get("blocks"):
            layout_file = output_path / f"{file_name}_layout.txt"
            self.layout_analyzer.export_to_text(result["layout"]["blocks"], str(layout_file))
        
        logger.info(f"✅ 所有结果已导出到: {output_dir}")


def compare_with_basic_loader(pdf_path: str):
    """
    对比基础加载器和高级加载器的效果
    
    Args:
        pdf_path: PDF 文件路径
    """
    from langchain_community.document_loaders import PyPDFLoader
    
    print("\n" + "="*60)
    print("📊 基础加载器 vs 高级加载器对比")
    print("="*60)
    
    # 基础加载器
    print("\n1️⃣ 基础加载器（PyPDFLoader）:")
    try:
        basic_loader = PyPDFLoader(pdf_path)
        basic_docs = basic_loader.load()
        basic_text = "\n".join([doc.page_content for doc in basic_docs])
        print(f"   提取文本: {len(basic_text)} 字符")
        print(f"   文档数: {len(basic_docs)}")
        print(f"   表格提取: ❌ 不支持")
        print(f"   OCR: ❌ 不支持")
        print(f"   版面分析: ❌ 不支持")
    except Exception as e:
        print(f"   ❌ 加载失败: {e}")
    
    # 高级加载器
    print("\n2️⃣ 高级加载器（AdvancedPDFLoader）:")
    try:
        advanced_loader = AdvancedPDFLoader()
        result = advanced_loader.load(pdf_path)
        print(f"   提取文本: {len(result['text'])} 字符")
        print(f"   表格提取: ✅ 提取 {len(result['tables'])} 个表格")
        print(f"   OCR: ✅ 识别 {len(result['ocr_results'])} 页图片")
        print(f"   版面分析: ✅ 检测 {result['layout']['summary'].get('max_columns', 0)} 列布局")
        
        print(f"\n📈 提升效果:")
        if basic_text:
            improvement = (len(result['text']) - len(basic_text)) / len(basic_text) * 100
            print(f"   文本提取量提升: {improvement:.1f}%")
        print(f"   额外功能: 表格结构化、图片文字识别、版面理解")
    except Exception as e:
        print(f"   ❌ 加载失败: {e}")


def demo():
    """演示高级加载器功能"""
    # 创建加载器实例
    loader = AdvancedPDFLoader(
        enable_table_extraction=True,
        enable_ocr=True,
        enable_layout_analysis=True,
        ocr_lang='ch'
    )
    
    # 测试文件
    test_files = [
        "test_data/complex_table.pdf",
        "test_data/scanned_doc.pdf",
        "test_data/multi_column.pdf"
    ]
    
    # 检查并处理存在的文件
    existing_files = [f for f in test_files if Path(f).exists()]
    
    if not existing_files:
        print("⚠️ 测试文件不存在，请准备以下文件:")
        for f in test_files:
            print(f"   - {f}")
        return
    
    print(f"✅ 找到 {len(existing_files)} 个测试文件")
    
    # 处理第一个文件
    test_file = existing_files[0]
    print(f"\n🎯 处理: {test_file}")
    
    # 对比基础加载器
    try:
        compare_with_basic_loader(test_file)
    except:
        pass
    
    # 加载并导出结果
    result = loader.load(test_file)
    loader.export_results(result, "output/advanced_results")
    
    # 分块处理（RAG 用）
    chunks = loader.load_and_split(test_file, chunk_size=500, chunk_overlap=100)
    print(f"\n✅ 分块完成: {len(chunks)} 个文本块")
    print(f"   块大小: 500 字符")
    print(f"   重叠: 100 字符")


if __name__ == "__main__":
    demo()