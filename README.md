# 社交媒体自动化运营系统（Social Media Auto-Pilot）

## 概述
构建人机协同、具备自学习能力的社交媒体自动化运营闭环。

覆盖平台：**抖音、小红书、B站、X（推特）**

核心闭环：素材采集 → 内容生产 → 分发采集 → 数据分析 → 策略反馈

## 项目结构

```
├── src/                    # 核心源码
│   ├── api/               # FastAPI路由层
│   ├── services/          # 业务逻辑层（6大类30模块）
│   ├── infrastructure/    # 共享基础设施
│   ├── models/            # ORM数据模型
│   ├── schemas/           # Pydantic校验模型
│   └── tasks/             # 异步任务
├── config/                # 配置文件
├── data/                  # 运行时数据
├── logs/                  # 日志
├── tests/                 # 测试
└── scripts/               # 运维脚本
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements/base.txt

# 初始化数据库
python scripts/init_db.py

# 启动服务
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## 开发阶段

| 阶段 | 时间 | 核心目标 |
|------|------|---------|
| P0 人工主导期 | 第1-4周 | 素材采集→内容生成→人工审阅最小闭环 |
| P1 人机协同期 | 第5-12周 | 多平台分发、审阅规则引擎、数据看板 |
| P2 系统主导期 | 第13周起 | 效果分析、评论挖掘、偏好学习 |
| P3 持续优化 | 持续 | 策略自动调整、知识图谱、A/B测试 |
