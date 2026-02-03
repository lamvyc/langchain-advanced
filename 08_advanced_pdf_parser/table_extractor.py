"""
表格提取模块
支持从 PDF 中提取简单和复杂表格，并转换为结构化数据
"""

import pdfplumber
import camelot
import pandas as pd
from typing import List, Dict, Optional
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TableExtractor:
    """PDF 表格提取器"""
    
    def __init__(self):
        """初始化表格提取器"""
        self.extraction_methods = ['pdfplumber', 'camelot']
    
    def extract_with_pdfplumber(self, pdf_path: str, page_num: Optional[int] = None) -> List[pd.DataFrame]:
        """
        使用 pdfplumber 提取表格（适合简单表格）
        
        Args:
            pdf_path: PDF 文件路径
            page_num: 指定页码（None 表示所有页）
            
        Returns:
            提取的表格列表（DataFrame 格式）
        """
        tables = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                pages = [pdf.pages[page_num]] if page_num is not None else pdf.pages
                
                for page in pages:
                    # 提取当前页的所有表格
                    page_tables = page.extract_tables()
                    
                    for table in page_tables:
                        if table and len(table) > 0:
                            # 转换为 DataFrame
                            df = pd.DataFrame(table[1:], columns=table[0])
                            tables.append(df)
                            logger.info(f"✅ 从第 {page.page_number} 页提取表格，大小: {df.shape}")
        
        except Exception as e:
            logger.error(f"❌ pdfplumber 提取失败: {e}")
        
        return tables
    
    def extract_with_camelot(self, pdf_path: str, pages: str = 'all', flavor: str = 'lattice') -> List[pd.DataFrame]:
        """
        使用 camelot 提取表格（适合复杂表格）
        
        Args:
            pdf_path: PDF 文件路径
            pages: 页码范围（如 '1-5' 或 'all'）
            flavor: 提取模式
                   - 'lattice': 适合有明显边框的表格（默认）
                   - 'stream': 适合无边框的表格
            
        Returns:
            提取的表格列表（DataFrame 格式）
        """
        tables = []
        
        try:
            # 使用 camelot 提取表格
            camelot_tables = camelot.read_pdf(pdf_path, pages=pages, flavor=flavor)
            
            for i, table in enumerate(camelot_tables):
                df = table.df
                
                # 清理数据：去除空行和空列
                df = df.replace('', pd.NA).dropna(how='all').dropna(axis=1, how='all')
                
                if not df.empty:
                    tables.append(df)
                    logger.info(f"✅ camelot 提取表格 {i+1}，大小: {df.shape}，准确率: {table.accuracy:.2f}%")
        
        except Exception as e:
            logger.error(f"❌ camelot 提取失败: {e}")
        
        return tables
    
    def extract_all(self, pdf_path: str, prefer_method: str = 'auto') -> Dict[str, List[pd.DataFrame]]:
        """
        综合提取：尝试多种方法并返回最佳结果
        
        Args:
            pdf_path: PDF 文件路径
            prefer_method: 优先方法（'auto', 'pdfplumber', 'camelot'）
            
        Returns:
            字典：{'method': [tables]}
        """
        results = {}
        
        logger.info(f"📄 开始提取 PDF 表格: {pdf_path}")
        
        # 方法 1: pdfplumber（快速，适合简单表格）
        if prefer_method in ['auto', 'pdfplumber']:
            pdfplumber_tables = self.extract_with_pdfplumber(pdf_path)
            if pdfplumber_tables:
                results['pdfplumber'] = pdfplumber_tables
        
        # 方法 2: camelot-lattice（适合有边框的复杂表格）
        if prefer_method in ['auto', 'camelot']:
            try:
                camelot_lattice = self.extract_with_camelot(pdf_path, flavor='lattice')
                if camelot_lattice:
                    results['camelot_lattice'] = camelot_lattice
            except Exception as e:
                logger.warning(f"⚠️ camelot-lattice 失败，尝试 stream 模式: {e}")
        
        # 方法 3: camelot-stream（适合无边框的表格）
        if prefer_method in ['auto', 'camelot'] and 'camelot_lattice' not in results:
            try:
                camelot_stream = self.extract_with_camelot(pdf_path, flavor='stream')
                if camelot_stream:
                    results['camelot_stream'] = camelot_stream
            except Exception as e:
                logger.warning(f"⚠️ camelot-stream 失败: {e}")
        
        # 汇总结果
        total_tables = sum(len(tables) for tables in results.values())
        logger.info(f"✅ 提取完成，共找到 {total_tables} 个表格")
        
        return results
    
    def save_tables(self, tables: List[pd.DataFrame], output_dir: str, prefix: str = "table") -> List[str]:
        """
        保存提取的表格为 CSV 或 Excel 文件
        
        Args:
            tables: 表格列表
            output_dir: 输出目录
            prefix: 文件名前缀
            
        Returns:
            保存的文件路径列表
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        
        for i, df in enumerate(tables):
            # 保存为 CSV
            csv_path = output_path / f"{prefix}_{i+1}.csv"
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            saved_files.append(str(csv_path))
            
            logger.info(f"💾 保存表格 {i+1}: {csv_path}")
        
        return saved_files


def demo():
    """演示表格提取功能"""
    extractor = TableExtractor()
    
    # 示例：提取测试 PDF 中的表格
    test_pdf = "test_data/complex_table.pdf"
    
    if Path(test_pdf).exists():
        # 提取所有表格
        results = extractor.extract_all(test_pdf)
        
        # 打印结果
        for method, tables in results.items():
            print(f"\n📊 方法: {method}")
            for i, df in enumerate(tables):
                print(f"\n表格 {i+1}:")
                print(df.head())
        
        # 保存表格
        if results:
            all_tables = [table for tables in results.values() for table in tables]
            saved_files = extractor.save_tables(all_tables, "output/tables")
            print(f"\n✅ 已保存 {len(saved_files)} 个表格")
    else:
        print(f"⚠️ 测试文件不存在: {test_pdf}")
        print("请先准备测试数据或修改路径")


if __name__ == "__main__":
    demo()