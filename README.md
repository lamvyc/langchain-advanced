# 🚀 LangChain 进阶项目集

这是一个系统化的 LangChain 进阶学习项目集合，涵盖 RAG、Agent、生产工程化等核心主题。

## 📋 项目概览

本项目包含 12 个循序渐进的实战项目，分为 3 个阶段：

### 阶段一：RAG 深化 (1-4)
1. ✅ **PDF 智能解析器** - 高级文档处理（表格、OCR、版面分析）
2. ⏸️ **混合检索系统** - BM25 + 向量检索融合
3. ⏸️ **企业文档权限管理** - 多租户架构与权限控制
4. ⏸️ **RAG 评估与优化平台** - 自动化评估与 A/B 测试

### 阶段二：Agent 开发 (5-8)
5. ⏸️ **多工具智能助手** - 工具调用与 ReAct 框架
6. ⏸️ **代码审查 Agent** - 自动化代码审查系统
7. ⏸️ **数据分析 SQL Agent** - 自然语言转 SQL
8. ⏸️ **多 Agent 协作系统** - 复杂任务分解与协作

### 阶段三：生产工程化 (9-12)
9. ⏸️ **流式 RAG API 服务** - FastAPI + 流式响应
10. ⏸️ **RAG 缓存与优化** - Redis 缓存与性能优化
11. ⏸️ **监控与告警系统** - Prometheus + Grafana
12. ⏸️ **端到端 RAG 平台** - 完整的生产级平台

## 📊 当前进度

- **已完成**: 1 / 12 项目 (8.3%)
- **当前项目**: 项目 1 - PDF 智能解析器 ✅
- **下一步**: 项目 2 - 混合检索系统

详细进度请查看 [PROJECT_STATUS.md](PROJECT_STATUS.md)

## 🎯 技术栈

- **核心框架**: LangChain, LangGraph
- **LLM**: OpenAI GPT-4, DeepSeek
- **向量数据库**: Chroma, FAISS
- **文档处理**: unstructured, pdfplumber, PaddleOCR
- **Web框架**: FastAPI
- **监控**: Prometheus, Grafana
- **其他**: Redis, PostgreSQL, Docker

## 🚀 快速开始

### 环境要求

- Python 3.9+
- pip / conda

### 安装步骤

1. 克隆仓库
```bash
git clone <repository-url>
cd langchain-advanced
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API keys
```

3. 安装项目依赖（以项目1为例）
```bash
cd 08_advanced_pdf_parser
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. 运行演示
```bash
python demo.py
```

## 📁 项目结构

```
langchain-advanced/
├── .comate/                    # 计划和配置
│   └── advanced_plan.md       # 总体项目计划
├── .gitignore                 # Git 忽略文件
├── .env.example               # 环境变量模板
├── README.md                  # 本文件
├── PROJECT_STATUS.md          # 项目进度跟踪
└── 08_advanced_pdf_parser/    # ✅ 项目 1
    ├── requirements.txt
    ├── README.md
    ├── table_extractor.py
    ├── image_ocr.py
    ├── layout_analyzer.py
    ├── advanced_loader.py
    └── demo.py
```

## 📚 已完成项目

### 1. PDF 智能解析器 ✅

**状态**: 已完成并通过测试

**功能特性**:
- 📊 智能表格提取（pdfplumber + camelot）
- 🖼️ 图片 OCR 识别（PaddleOCR）
- ?? 版面分析（多栏布局检测）
- 🔗 统一加载器接口
- 📝 完整的文档和示例

**快速体验**:
```bash
cd 08_advanced_pdf_parser
pip install -r requirements.txt
python demo.py
```

详细文档：[08_advanced_pdf_parser/README.md](08_advanced_pdf_parser/README.md)

## 🔗 相关资源

- **总体计划**: [.comate/advanced_plan.md](.comate/advanced_plan.md)
- **进度跟踪**: [PROJECT_STATUS.md](PROJECT_STATUS.md)
- **LangChain 官方文档**: https://python.langchain.com/
- **LangGraph 文档**: https://langchain-ai.github.io/langgraph/

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## ✨ 致谢

感谢 LangChain 社区和所有开源贡献者！

---

**持续更新中...** 🚀