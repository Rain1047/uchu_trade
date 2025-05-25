#!/usr/bin/env python3
"""
PDF处理工具
用于从交易书籍PDF中提取文本内容
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """PDF文档处理器"""
    
    def __init__(self, raw_books_dir: str, extracted_text_dir: str):
        self.raw_books_dir = Path(raw_books_dir)
        self.extracted_text_dir = Path(extracted_text_dir)
        self.extracted_text_dir.mkdir(exist_ok=True)
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Optional[str]:
        """
        从PDF文件提取文本
        支持多种PDF处理库作为备选方案
        """
        text_content = ""
        
        # 方案1：尝试使用PyPDF2
        try:
            import PyPDF2
            text_content = self._extract_with_pypdf2(pdf_path)
            if text_content.strip():
                logger.info(f"使用PyPDF2成功提取: {pdf_path.name}")
                return text_content
        except ImportError:
            logger.warning("PyPDF2未安装")
        except Exception as e:
            logger.warning(f"PyPDF2提取失败: {e}")
        
        # 方案2：尝试使用pdfplumber
        try:
            import pdfplumber
            text_content = self._extract_with_pdfplumber(pdf_path)
            if text_content.strip():
                logger.info(f"使用pdfplumber成功提取: {pdf_path.name}")
                return text_content
        except ImportError:
            logger.warning("pdfplumber未安装")
        except Exception as e:
            logger.warning(f"pdfplumber提取失败: {e}")
        
        # 方案3：尝试使用pymupdf
        try:
            import fitz  # pymupdf
            text_content = self._extract_with_pymupdf(pdf_path)
            if text_content.strip():
                logger.info(f"使用pymupdf成功提取: {pdf_path.name}")
                return text_content
        except ImportError:
            logger.warning("pymupdf未安装")
        except Exception as e:
            logger.warning(f"pymupdf提取失败: {e}")
        
        logger.error(f"所有PDF提取方法都失败了: {pdf_path.name}")
        return None
    
    def _extract_with_pypdf2(self, pdf_path: Path) -> str:
        """使用PyPDF2提取文本"""
        import PyPDF2
        
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _extract_with_pdfplumber(self, pdf_path: Path) -> str:
        """使用pdfplumber提取文本"""
        import pdfplumber
        
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    
    def _extract_with_pymupdf(self, pdf_path: Path) -> str:
        """使用pymupdf提取文本"""
        import fitz
        
        text = ""
        doc = fitz.open(pdf_path)
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text() + "\n"
        doc.close()
        return text
    
    def process_pdf(self, pdf_filename: str) -> Optional[Dict[str, Any]]:
        """
        处理单个PDF文件
        返回处理结果信息
        """
        pdf_path = self.raw_books_dir / pdf_filename
        
        if not pdf_path.exists():
            logger.error(f"PDF文件不存在: {pdf_path}")
            return None
        
        # 解析文件名获取元信息
        name_parts = pdf_path.stem.split('_')
        if len(name_parts) >= 3:
            book_name = name_parts[0]
            author = name_parts[1]
            trading_type = name_parts[2]
        else:
            book_name = pdf_path.stem
            author = "未知"
            trading_type = "未分类"
        
        logger.info(f"开始处理PDF: {pdf_filename}")
        
        # 提取文本
        text_content = self.extract_text_from_pdf(pdf_path)
        if not text_content:
            return None
        
        # 保存提取的文本
        text_filename = f"{pdf_path.stem}.txt"
        text_path = self.extracted_text_dir / text_filename
        
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        result = {
            'pdf_file': pdf_filename,
            'text_file': text_filename,
            'book_name': book_name,
            'author': author,
            'trading_type': trading_type,
            'text_length': len(text_content),
            'success': True
        }
        
        logger.info(f"成功处理PDF: {pdf_filename}, 文本长度: {len(text_content)}")
        return result
    
    def process_all_pdfs(self) -> Dict[str, Any]:
        """处理所有PDF文件"""
        results = {
            'processed': [],
            'failed': [],
            'total_files': 0,
            'success_count': 0
        }
        
        pdf_files = list(self.raw_books_dir.glob('*.pdf'))
        results['total_files'] = len(pdf_files)
        
        for pdf_path in pdf_files:
            result = self.process_pdf(pdf_path.name)
            if result:
                results['processed'].append(result)
                results['success_count'] += 1
            else:
                results['failed'].append(pdf_path.name)
        
        logger.info(f"PDF处理完成: {results['success_count']}/{results['total_files']} 成功")
        return results

def install_pdf_dependencies():
    """安装PDF处理依赖"""
    dependencies = [
        'PyPDF2',
        'pdfplumber', 
        'pymupdf'
    ]
    
    for dep in dependencies:
        try:
            __import__(dep.lower().replace('pdf2', 'PyPDF2'))
            logger.info(f"{dep} 已安装")
        except ImportError:
            logger.info(f"正在安装 {dep}...")
            os.system(f"pip install {dep}")

if __name__ == "__main__":
    # 设置路径
    current_dir = Path(__file__).parent
    raw_books_dir = current_dir.parent / "raw_books"
    extracted_text_dir = current_dir.parent / "extracted_text"
    
    # 检查并安装依赖
    print("检查PDF处理依赖...")
    install_pdf_dependencies()
    
    # 创建处理器并运行
    processor = PDFProcessor(str(raw_books_dir), str(extracted_text_dir))
    results = processor.process_all_pdfs()
    
    print(f"\n处理结果:")
    print(f"总文件数: {results['total_files']}")
    print(f"成功处理: {results['success_count']}")
    print(f"失败文件: {len(results['failed'])}")
    
    if results['failed']:
        print(f"失败的文件: {results['failed']}") 