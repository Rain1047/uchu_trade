#!/usr/bin/env python3
"""
交易规则提取主控制脚本
整合PDF处理、规则提取、AI增强和策略生成的完整流程
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import argparse

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / "tools"))

# 导入自定义模块
from tools.pdf_processor import PDFProcessor
from tools.rule_extractor import RuleExtractor
from tools.ai_rule_enhancer import AIRuleEnhancer
from tools.strategy_generator import StrategyGenerator

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_rules_extraction.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TradingRulesExtractor:
    """交易规则提取主控制器"""
    
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            self.base_dir = Path(__file__).parent
        
        # 设置目录路径
        self.raw_books_dir = self.base_dir / "raw_books"
        self.extracted_text_dir = self.base_dir / "extracted_text"
        self.processed_rules_dir = self.base_dir / "processed_rules"
        self.final_strategies_dir = self.base_dir / "final_strategies"
        
        # 确保所有目录存在
        for dir_path in [self.raw_books_dir, self.extracted_text_dir, 
                        self.processed_rules_dir, self.final_strategies_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # 初始化处理器
        self.pdf_processor = PDFProcessor(
            str(self.raw_books_dir), 
            str(self.extracted_text_dir)
        )
        self.rule_extractor = RuleExtractor(
            str(self.extracted_text_dir), 
            str(self.processed_rules_dir)
        )
        self.ai_enhancer = AIRuleEnhancer(
            str(self.extracted_text_dir), 
            str(self.processed_rules_dir)
        )
        self.strategy_generator = StrategyGenerator(
            str(self.processed_rules_dir), 
            str(self.final_strategies_dir)
        )
        
        # 处理统计
        self.stats = {
            'pdf_files': 0,
            'text_files': 0,
            'extracted_rules': 0,
            'generated_strategies': 0,
            'errors': []
        }
    
    def check_dependencies(self) -> bool:
        """检查依赖库是否安装"""
        required_packages = [
            'PyPDF2', 'pdfplumber', 'pymupdf', 'pandas', 'numpy'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                if package == 'pymupdf':
                    import fitz
                elif package == 'PyPDF2':
                    import PyPDF2
                else:
                    __import__(package.lower())
                logger.info(f"✓ {package} 已安装")
            except ImportError:
                missing_packages.append(package)
                logger.warning(f"✗ {package} 未安装")
        
        if missing_packages:
            logger.error(f"缺少以下依赖包: {missing_packages}")
            logger.info("请运行以下命令安装:")
            for package in missing_packages:
                logger.info(f"  pip install {package}")
            return False
        
        return True
    
    def step1_extract_pdf_text(self) -> bool:
        """步骤1: 从PDF提取文本"""
        logger.info("=" * 50)
        logger.info("步骤 1: PDF文本提取")
        logger.info("=" * 50)
        
        try:
            pdf_files = list(self.raw_books_dir.glob('*.pdf'))
            if not pdf_files:
                logger.warning(f"在 {self.raw_books_dir} 中未找到PDF文件")
                logger.info("请将PDF文件放入 raw_books/ 目录，文件命名格式: 书名_作者_类型.pdf")
                return False
            
            logger.info(f"找到 {len(pdf_files)} 个PDF文件")
            self.stats['pdf_files'] = len(pdf_files)
            
            # 处理所有PDF
            results = self.pdf_processor.process_all_pdfs()
            
            logger.info(f"PDF处理完成: {results['success_count']}/{results['total_files']} 成功")
            if results['failed']:
                logger.warning(f"失败的文件: {results['failed']}")
                self.stats['errors'].extend(results['failed'])
            
            self.stats['text_files'] = results['success_count']
            return results['success_count'] > 0
            
        except Exception as e:
            logger.error(f"PDF文本提取失败: {e}")
            self.stats['errors'].append(f"PDF提取错误: {e}")
            return False
    
    def step2_extract_rules(self, use_ai: bool = False) -> bool:
        """步骤2: 提取交易规则"""
        logger.info("=" * 50)
        logger.info(f"步骤 2: 交易规则提取 ({'AI增强' if use_ai else '基础模式'})")
        logger.info("=" * 50)
        
        try:
            text_files = list(self.extracted_text_dir.glob('*.txt'))
            if not text_files:
                logger.warning("没有找到文本文件，请先运行PDF提取")
                return False
            
            logger.info(f"找到 {len(text_files)} 个文本文件")
            
            if use_ai:
                # 使用AI增强提取
                total_rules = 0
                for text_file in text_files:
                    logger.info(f"AI分析文件: {text_file.name}")
                    results = self.ai_enhancer.process_text_file(text_file.name)
                    if results:
                        file_rules = (len(results.get('entry_rules', [])) + 
                                    len(results.get('exit_rules', [])) + 
                                    len(results.get('filter_rules', [])))
                        total_rules += file_rules
                        logger.info(f"  提取规则: {file_rules} 条")
            else:
                # 使用基础提取
                results = self.rule_extractor.process_all_text_files()
                total_rules = results['total_rules']
            
            logger.info(f"规则提取完成: 总计 {total_rules} 条规则")
            self.stats['extracted_rules'] = total_rules
            return total_rules > 0
            
        except Exception as e:
            logger.error(f"规则提取失败: {e}")
            self.stats['errors'].append(f"规则提取错误: {e}")
            return False
    
    def step3_generate_strategies(self) -> bool:
        """步骤3: 生成交易策略"""
        logger.info("=" * 50)
        logger.info("步骤 3: 策略代码生成")
        logger.info("=" * 50)
        
        try:
            rule_files = list(self.processed_rules_dir.glob('*_rules.json'))
            rule_files.extend(list(self.processed_rules_dir.glob('*_ai_analysis.json')))
            
            if not rule_files:
                logger.warning("没有找到规则文件，请先运行规则提取")
                return False
            
            logger.info(f"找到 {len(rule_files)} 个规则文件")
            
            # 生成策略
            results = self.strategy_generator.process_all_rules()
            
            logger.info(f"策略生成完成: {results['success_count']}/{results['total_files']} 成功")
            if results['failed_files']:
                logger.warning(f"失败的文件: {results['failed_files']}")
                self.stats['errors'].extend(results['failed_files'])
            
            self.stats['generated_strategies'] = results['success_count']
            
            # 显示生成的策略
            if results['generated_strategies']:
                logger.info("生成的策略:")
                for strategy in results['generated_strategies']:
                    logger.info(f"  - {strategy}")
            
            return results['success_count'] > 0
            
        except Exception as e:
            logger.error(f"策略生成失败: {e}")
            self.stats['errors'].append(f"策略生成错误: {e}")
            return False
    
    def generate_conversation_prompts(self, sample_text: str = None) -> Dict[str, str]:
        """生成对话式分析提示"""
        if not sample_text:
            # 尝试从现有文本文件中获取示例
            text_files = list(self.extracted_text_dir.glob('*.txt'))
            if text_files:
                with open(text_files[0], 'r', encoding='utf-8') as f:
                    sample_text = f.read()[:2000]  # 取前2000字符
            else:
                sample_text = "请先提供文本内容"
        
        return self.ai_enhancer.generate_conversation_prompts(sample_text)
    
    def run_full_pipeline(self, use_ai: bool = False) -> Dict[str, Any]:
        """运行完整的处理流程"""
        logger.info("开始交易规则提取完整流程")
        logger.info(f"工作目录: {self.base_dir}")
        
        # 检查依赖
        if not self.check_dependencies():
            return {'success': False, 'error': 'Missing dependencies'}
        
        # 步骤1: PDF文本提取
        if not self.step1_extract_pdf_text():
            return {'success': False, 'error': 'PDF extraction failed', 'stats': self.stats}
        
        # 步骤2: 规则提取
        if not self.step2_extract_rules(use_ai=use_ai):
            return {'success': False, 'error': 'Rule extraction failed', 'stats': self.stats}
        
        # 步骤3: 策略生成
        if not self.step3_generate_strategies():
            return {'success': False, 'error': 'Strategy generation failed', 'stats': self.stats}
        
        # 生成最终报告
        self.generate_final_report()
        
        logger.info("=" * 50)
        logger.info("处理流程完成!")
        logger.info("=" * 50)
        
        return {'success': True, 'stats': self.stats}
    
    def generate_final_report(self):
        """生成最终处理报告"""
        report = {
            'processing_summary': {
                'pdf_files_processed': self.stats['pdf_files'],
                'text_files_created': self.stats['text_files'],
                'rules_extracted': self.stats['extracted_rules'],
                'strategies_generated': self.stats['generated_strategies'],
                'errors_count': len(self.stats['errors'])
            },
            'file_structure': {
                'raw_books': list(str(f) for f in self.raw_books_dir.glob('*.pdf')),
                'extracted_text': list(str(f) for f in self.extracted_text_dir.glob('*.txt')),
                'processed_rules': list(str(f) for f in self.processed_rules_dir.glob('*.json')),
                'final_strategies': list(str(f) for f in self.final_strategies_dir.glob('*.py'))
            },
            'errors': self.stats['errors'],
            'next_steps': [
                "1. 检查生成的策略代码",
                "2. 在回测系统中测试策略",
                "3. 根据回测结果优化参数",
                "4. 部署到实盘交易系统"
            ]
        }
        
        report_path = self.base_dir / "extraction_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"处理报告已保存到: {report_path}")
        
        # 打印摘要
        logger.info(f"处理摘要:")
        logger.info(f"  PDF文件: {self.stats['pdf_files']}")
        logger.info(f"  文本文件: {self.stats['text_files']}")
        logger.info(f"  提取规则: {self.stats['extracted_rules']}")
        logger.info(f"  生成策略: {self.stats['generated_strategies']}")
        if self.stats['errors']:
            logger.info(f"  错误数量: {len(self.stats['errors'])}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='交易规则提取系统')
    parser.add_argument('--mode', choices=['full', 'pdf', 'rules', 'strategies', 'prompt'], 
                       default='full', help='运行模式')
    parser.add_argument('--ai', action='store_true', help='使用AI增强模式')
    parser.add_argument('--base-dir', type=str, help='基础工作目录')
    
    args = parser.parse_args()
    
    # 创建提取器
    extractor = TradingRulesExtractor(args.base_dir)
    
    if args.mode == 'prompt':
        # 生成对话提示
        prompts = extractor.generate_conversation_prompts()
        print("\n=== 对话式分析提示 ===")
        for stage, prompt in prompts.items():
            print(f"\n{stage.upper()}:")
            print(prompt)
            print("-" * 50)
    
    elif args.mode == 'pdf':
        # 只运行PDF提取
        extractor.step1_extract_pdf_text()
    
    elif args.mode == 'rules':
        # 只运行规则提取
        extractor.step2_extract_rules(use_ai=args.ai)
    
    elif args.mode == 'strategies':
        # 只运行策略生成
        extractor.step3_generate_strategies()
    
    elif args.mode == 'full':
        # 运行完整流程
        result = extractor.run_full_pipeline(use_ai=args.ai)
        if result['success']:
            print("\n✓ 处理流程成功完成!")
        else:
            print(f"\n✗ 处理失败: {result['error']}")

if __name__ == "__main__":
    main() 