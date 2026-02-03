"""
版面分析模块
支持多栏布局检测、阅读顺序重排、文本块分类
"""

import fitz  # PyMuPDF
from typing import List, Dict, Tuple
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TextBlock:
    """文本块数据类"""
    text: str
    bbox: Tuple[float, float, float, float]  # (x0, y0, x1, y1)
    page: int
    block_type: str  # 'title', 'body', 'footer', 'header'
    column: int  # 所属列（0, 1, 2...）
    font_size: float
    font_name: str


class LayoutAnalyzer:
    """PDF 版面分析器"""
    
    def __init__(self, column_threshold: float = 50.0):
        """
        初始化版面分析器
        
        Args:
            column_threshold: 列分隔阈值（像素），用于判断是否为多栏布局
        """
        self.column_threshold = column_threshold
    
    def extract_text_blocks(self, pdf_path: str) -> List[TextBlock]:
        """
        提取 PDF 中的所有文本块及其属性
        
        Args:
            pdf_path: PDF 文件路径
            
        Returns:
            文本块列表
        """
        text_blocks = []
        
        try:
            pdf_document = fitz.open(pdf_path)
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                
                # 获取页面文本块（包含位置、字体等信息）
                blocks = page.get_text("dict")["blocks"]
                
                for block in blocks:
                    # 跳过图片块
                    if block.get("type") != 0:
                        continue
                    
                    # 提取文本行
                    text_lines = []
                    font_sizes = []
                    font_names = []
                    
                    for line in block.get("lines", []):
                        line_text = ""
                        for span in line.get("spans", []):
                            line_text += span.get("text", "")
                            font_sizes.append(span.get("size", 0))
                            font_names.append(span.get("font", ""))
                        
                        if line_text.strip():
                            text_lines.append(line_text)
                    
                    if text_lines:
                        # 计算平均字体大小
                        avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 12
                        most_common_font = max(set(font_names), key=font_names.count) if font_names else ""
                        
                        text_block = TextBlock(
                            text="\n".join(text_lines),
                            bbox=tuple(block["bbox"]),
                            page=page_num + 1,
                            block_type="body",  # 初始类型，稍后分类
                            column=0,  # 初始列号，稍后分配
                            font_size=avg_font_size,
                            font_name=most_common_font
                        )
                        text_blocks.append(text_block)
            
            pdf_document.close()
            logger.info(f"✅ 提取 {len(text_blocks)} 个文本块")
        
        except Exception as e:
            logger.error(f"❌ 文本块提取失败: {e}")
        
        return text_blocks
    
    def classify_blocks(self, blocks: List[TextBlock]) -> List[TextBlock]:
        """
        对文本块进行分类（标题、正文、页眉、页脚）
        
        Args:
            blocks: 文本块列表
            
        Returns:
            分类后的文本块列表
        """
        if not blocks:
            return blocks
        
        # 计算平均字体大小
        avg_font_size = sum(b.font_size for b in blocks) / len(blocks)
        
        for block in blocks:
            x0, y0, x1, y1 = block.bbox
            
            # 根据字体大小判断是否为标题
            if block.font_size > avg_font_size * 1.3:
                block.block_type = "title"
            
            # 根据位置判断页眉和页脚
            # 假设页眉在页面上方 10%，页脚在页面下方 10%
            elif y0 < 60:  # 页眉区域（像素）
                block.block_type = "header"
            elif y1 > 780:  # 页脚区域（假设 A4 页面高度约 842）
                block.block_type = "footer"
            else:
                block.block_type = "body"
        
        logger.info(f"✅ 文本块分类完成")
        return blocks
    
    def detect_columns(self, blocks: List[TextBlock], page_num: int) -> List[TextBlock]:
        """
        检测多栏布局并分配列号
        
        Args:
            blocks: 特定页面的文本块列表
            page_num: 页码
            
        Returns:
            分配列号后的文本块列表
        """
        # 过滤当前页面的正文块
        page_blocks = [b for b in blocks if b.page == page_num and b.block_type == "body"]
        
        if not page_blocks:
            return blocks
        
        # 按 x0 坐标排序（从左到右）
        page_blocks.sort(key=lambda b: b.bbox[0])
        
        # 检测列分隔
        columns = []
        current_column = [page_blocks[0]]
        
        for i in range(1, len(page_blocks)):
            prev_block = page_blocks[i-1]
            curr_block = page_blocks[i]
            
            # 计算水平距离
            gap = curr_block.bbox[0] - prev_block.bbox[2]
            
            # 如果间隙超过阈值，认为是新列
            if gap > self.column_threshold:
                columns.append(current_column)
                current_column = [curr_block]
            else:
                current_column.append(curr_block)
        
        columns.append(current_column)
        
        # 分配列号
        for col_idx, column_blocks in enumerate(columns):
            for block in column_blocks:
                block.column = col_idx
        
        num_columns = len(columns)
        logger.info(f"📊 第 {page_num} 页检测到 {num_columns} 列布局")
        
        return blocks
    
    def reorder_by_reading_order(self, blocks: List[TextBlock]) -> List[TextBlock]:
        """
        按阅读顺序重排文本块（从左到右，从上到下）
        
        Args:
            blocks: 文本块列表
            
        Returns:
            重排后的文本块列表
        """
        # 按页码分组
        pages = {}
        for block in blocks:
            if block.page not in pages:
                pages[block.page] = []
            pages[block.page].append(block)
        
        reordered_blocks = []
        
        for page_num in sorted(pages.keys()):
            page_blocks = pages[page_num]
            
            # 先处理页眉
            headers = [b for b in page_blocks if b.block_type == "header"]
            headers.sort(key=lambda b: (b.bbox[1], b.bbox[0]))  # 从上到下，从左到右
            
            # 处理正文（按列和垂直位置排序）
            body_blocks = [b for b in page_blocks if b.block_type in ["title", "body"]]
            body_blocks.sort(key=lambda b: (b.column, b.bbox[1], b.bbox[0]))
            
            # 处理页脚
            footers = [b for b in page_blocks if b.block_type == "footer"]
            footers.sort(key=lambda b: (b.bbox[1], b.bbox[0]))
            
            # 合并
            reordered_blocks.extend(headers)
            reordered_blocks.extend(body_blocks)
            reordered_blocks.extend(footers)
        
        logger.info(f"✅ 文本块已按阅读顺序重排")
        return reordered_blocks
    
    def analyze_layout(self, pdf_path: str) -> Dict:
        """
        综合版面分析：提取、分类、检测多栏、重排序
        
        Args:
            pdf_path: PDF 文件路径
            
        Returns:
            分析结果字典
        """
        logger.info(f"📄 开始版面分析: {pdf_path}")
        
        # 1. 提取文本块
        blocks = self.extract_text_blocks(pdf_path)
        
        if not blocks:
            logger.warning("⚠️ 未提取到文本块")
            return {"blocks": [], "summary": {}}
        
        # 2. 分类文本块
        blocks = self.classify_blocks(blocks)
        
        # 3. 检测多栏布局（按页处理）
        pages = set(b.page for b in blocks)
        for page_num in pages:
            blocks = self.detect_columns(blocks, page_num)
        
        # 4. 按阅读顺序重排
        blocks = self.reorder_by_reading_order(blocks)
        
        # 5. 生成摘要统计
        summary = {
            "total_blocks": len(blocks),
            "pages": len(pages),
            "block_types": {
                "title": len([b for b in blocks if b.block_type == "title"]),
                "body": len([b for b in blocks if b.block_type == "body"]),
                "header": len([b for b in blocks if b.block_type == "header"]),
                "footer": len([b for b in blocks if b.block_type == "footer"])
            },
            "max_columns": max([b.column for b in blocks]) + 1 if blocks else 0
        }
        
        logger.info(f"✅ 版面分析完成: {summary}")
        
        return {
            "blocks": blocks,
            "summary": summary
        }
    
    def export_to_text(self, blocks: List[TextBlock], output_path: str):
        """
        导出分析结果为文本文件（保持阅读顺序）
        
        Args:
            blocks: 文本块列表
            output_path: 输出文件路径
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                current_page = None
                
                for block in blocks:
                    # 新页面标记
                    if block.page != current_page:
                        current_page = block.page
                        f.write(f"\n{'='*60}\n")
                        f.write(f"第 {current_page} 页\n")
                        f.write(f"{'='*60}\n\n")
                    
                    # 写入文本块（带类型标记）
                    type_tag = f"[{block.block_type.upper()}]"
                    f.write(f"{type_tag} {block.text}\n\n")
            
            logger.info(f"💾 版面分析结果已保存: {output_path}")
        
        except Exception as e:
            logger.error(f"❌ 保存结果失败: {e}")


def demo():
    """演示版面分析功能"""
    analyzer = LayoutAnalyzer(column_threshold=50.0)
    
    # 示例：分析多栏布局 PDF
    test_pdf = "test_data/multi_column.pdf"
    
    if Path(test_pdf).exists():
        # 执行版面分析
        result = analyzer.analyze_layout(test_pdf)
        
        # 打印摘要
        print("\n📊 版面分析摘要:")
        print(f"  总文本块: {result['summary']['total_blocks']}")
        print(f"  页数: {result['summary']['pages']}")
        print(f"  最多列数: {result['summary']['max_columns']}")
        print(f"  文本块类型分布: {result['summary']['block_types']}")
        
        # 打印前几个文本块
        print("\n📄 文本块预览（前5个）:")
        for i, block in enumerate(result['blocks'][:5]):
            print(f"\n{i+1}. [{block.block_type}] 第{block.page}页 列{block.column}")
            print(f"   {block.text[:100]}...")
        
        # 导出结果
        analyzer.export_to_text(result['blocks'], "output/layout_analysis.txt")
        print("\n✅ 结果已导出")
    else:
        print(f"⚠️ 测试文件不存在: {test_pdf}")
        print("请先准备测试数据或修改路径")


if __name__ == "__main__":
    from pathlib import Path
    demo()