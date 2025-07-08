# AI-Fortunetelling-App Makefile

.PHONY: help install test lint clean run build docs

# 默认目标，显示帮助信息
help:
	@echo "可用命令:"
	@echo "  make install        - 安装依赖"
	@echo "  make test           - 运行测试"
	@echo "  make lint           - 运行代码检查"
	@echo "  make clean          - 清理临时文件"
	@echo "  make run            - 运行应用程序"
	@echo "  make build          - 构建项目"
	@echo "  make docs           - 生成文档"

# 安装项目依赖
install:
	pip install -e .
	pip install -r requirements-dev.txt

# 运行测试
test:
	pytest

# 代码质量检查
lint:
	flake8 src tests
	black --check src tests
	isort --check-only src tests

# 格式化代码
format:
	black src tests
	isort src tests

# 清理临时文件和构建产物
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

# 运行应用程序
run:
	python src/ai_fortunetelling_app/chat_services/AI_Fortunetelling.py

# 构建项目
build:
	python -m build

# 生成文档
docs:
	cd docs && sphinx-build -b html source build/html