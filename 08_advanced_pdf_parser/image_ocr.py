"""
图片 OCR 模块
支持从 PDF 中提取图片并使用 OCR 识别文字
"""

import fitz  # PyMuPDF
from paddleocr import PaddleOCR
from PIL import Image
import io
import logging
from typing import List, Dict, Tuple
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageOCR:
    """PDF 图片 OCR 识别器"""
    
    def __init__(self, use_angle_cls=True, lang='ch'):
        """
        初始化 OCR 识别器
        
        Args:
            use_angle_cls: 是否使用角度分类（自动纠正图片方向）
            lang: 语言模型（'ch': 中文, 'en': 英文）
        """
        try:
            self.ocr = PaddleOCR(use_angle_cls=use_angle_cls, lang=lang, show_log=False)
            logger.info("✅ PaddleOCR 初始化成功")
        except Exception as e:
            logger.error(f"❌ PaddleOCR 初始化失败: {e}")
            self.ocr = None
    
    def extract_images_from_pdf(self, pdf_path: str, min_width: int = 100, min_height: int = 100) -> List[Dict]:
        """
        从 PDF 中提取所有图片
        
        Args:
            pdf_path: PDF 文件路径
            min_width: 最小图片宽度（过滤小图标）
            min_height: 最小图片高度
            
        Returns:
            图片信息列表：[{'page': page_num, 'image': PIL.Image, 'bbox': (x0, y0, x1, y1)}]
        """
        images = []
        
        try:
            pdf_document = fitz.open(pdf_path)
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        # 获取图片对象
                        xref = img[0]
                        base_image = pdf_document.extract_image(xref)
                        image_bytes = base_image["image"]
                        
                        # 转换为 PIL Image
                        pil_image = Image.open(io.BytesIO(image_bytes))
                        
                        # 过滤小图片
                        if pil_image.width < min_width or pil_image.height < min_height:
                            continue
                        
                        # 获取图片在页面中的位置
                        img_rects = page.get_image_rects(xref)
                        bbox = img_rects[0] if img_rects else None
                        
                        images.append({
                            'page': page_num + 1,
                            'index': img_index + 1,
                            'image': pil_image,
                            'bbox': bbox,
                            'size': (pil_image.width, pil_image.height)
                        })
                        
                        logger.info(f"📷 第 {page_num + 1} 页提取图片 {img_index + 1}，尺寸: {pil_image.size}")
                    
                    except Exception as e:
                        logger.warning(f"⚠️ 提取图片失败: {e}")
                        continue
            
            pdf_document.close()
            logger.info(f"✅ 共提取 {len(images)} 张图片")
        
        except Exception as e:
            logger.error(f"❌ PDF 图片提取失败: {e}")
        
        return images
    
    def recognize_text(self, image: Image.Image) -> List[Tuple[str, float]]:
        """
        对单张图片进行 OCR 识别
        
        Args:
            image: PIL Image 对象
            
        Returns:
            识别结果列表：[(文本内容, 置信度)]
        """
        if self.ocr is None:
            logger.error("❌ OCR 未初始化")
            return []
        
        try:
            # 转换为 numpy array
            import numpy as np
            img_array = np.array(image)
            
            # 执行 OCR
            result = self.ocr.ocr(img_array, cls=True)
            
            # 解析结果
            text_results = []
            if result and result[0]:
                for line in result[0]:
                    text = line[1][0]  # 识别的文本
                    confidence = line[1][1]  # 置信度
                    text_results.append((text, confidence))
            
            return text_results
        
        except Exception as e:
            logger.error(f"❌ OCR 识别失败: {e}")
            return []
    
    def process_pdf(self, pdf_path: str, confidence_threshold: float = 0.5) -> Dict[int, List[str]]:
        """
        处理整个 PDF：提取图片并进行 OCR
        
        Args:
            pdf_path: PDF 文件路径
            confidence_threshold: 置信度阈值（低于此值的结果将被过滤）
            
        Returns:
            字典：{page_num: [recognized_texts]}
        """
        logger.info(f"📄 开始处理 PDF: {pdf_path}")
        
        # 提取所有图片
        images = self.extract_images_from_pdf(pdf_path)
        
        if not images:
            logger.warning("⚠️ 未找到图片")
            return {}
        
        # 对每张图片进行 OCR
        results = {}
        
        for img_info in images:
            page_num = img_info['page']
            image = img_info['image']
            
            logger.info(f"🔍 识别第 {page_num} 页图片 {img_info['index']}...")
            
            # 执行 OCR
            text_results = self.recognize_text(image)
            
            # 过滤低置信度结果
            filtered_texts = [
                text for text, conf in text_results 
                if conf >= confidence_threshold
            ]
            
            if filtered_texts:
                if page_num not in results:
                    results[page_num] = []
                results[page_num].extend(filtered_texts)
                
                logger.info(f"✅ 识别出 {len(filtered_texts)} 行文本（置信度 ≥ {confidence_threshold}）")
        
        return results
    
    def save_images(self, images: List[Dict], output_dir: str, prefix: str = "image") -> List[str]:
        """
        保存提取的图片
        
        Args:
            images: 图片信息列表
            output_dir: 输出目录
            prefix: 文件名前缀
            
        Returns:
            保存的文件路径列表
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        
        for img_info in images:
            page_num = img_info['page']
            img_index = img_info['index']
            image = img_info['image']
            
            # 保存图片
            img_path = output_path / f"{prefix}_page{page_num}_img{img_index}.png"
            image.save(img_path)
            saved_files.append(str(img_path))
            
            logger.info(f"💾 保存图片: {img_path}")
        
        return saved_files
    
    def export_ocr_results(self, results: Dict[int, List[str]], output_path: str):
        """
        导出 OCR 识别结果到文本文件
        
        Args:
            results: OCR 结果字典
            output_path: 输出文件路径
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for page_num in sorted(results.keys()):
                    f.write(f"\n{'='*50}\n")
                    f.write(f"第 {page_num} 页识别结果\n")
                    f.write(f"{'='*50}\n\n")
                    
                    for text in results[page_num]:
                        f.write(f"{text}\n")
            
            logger.info(f"💾 OCR 结果已保存: {output_path}")
        
        except Exception as e:
            logger.error(f"❌ 保存 OCR 结果失败: {e}")


def demo():
    """演示 OCR 功能"""
    ocr = ImageOCR(lang='ch')
    
    # 示例：处理扫描版 PDF
    test_pdf = "test_data/scanned_doc.pdf"
    
    if Path(test_pdf).exists():
        # 提取图片并识别
        results = ocr.process_pdf(test_pdf, confidence_threshold=0.6)
        
        # 打印结果
        print("\n📊 OCR 识别结果:")
        for page_num, texts in results.items():
            print(f"\n第 {page_num} 页:")
            for text in texts[:5]:  # 只显示前 5 行
                print(f"  - {text}")
        
        # 导出结果
        ocr.export_ocr_results(results, "output/ocr_results.txt")
        
        # 提取并保存图片
        images = ocr.extract_images_from_pdf(test_pdf)
        if images:
            saved = ocr.save_images(images, "output/images")
            print(f"\n✅ 已保存 {len(saved)} 张图片")
    else:
        print(f"⚠️ 测试文件不存在: {test_pdf}")
        print("请先准备测试数据或修改路径")


if __name__ == "__main__":
    demo()