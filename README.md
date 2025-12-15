# AI 单词本

双语、AI 辅助的词汇本，具备艾宾浩斯复习功能，使用 SQLite 存储，支持单容器 Docker 部署。

## 功能
- 用户注册/登录（JWT），管理员用户列表，AI 提供商配置存储。
- 添加部分信息的单词；离线 AI 桩代码返回带有例句和翻译的双语 JSON。
- 艾宾浩斯式间隔重复复习，支持 英→中 或 中→英 模式，一键反馈结果。
- 落地页和仪表盘支持浅色/深色主题切换和中/英界面文案。
- 默认使用 SQLite 持久化；提供 Dockerfile 用于单容器部署；GitHub Action 构建最新镜像。

## 快速开始

### 本地开发

1. 创建并激活虚拟环境：
   `ash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/Mac:
   # source .venv/bin/activate
   `

2. 安装依赖：
   `ash
   pip install -r requirements.txt
   `

3. 配置环境变量：
   本项目使用环境变量进行配置。请复制示例文件 \.env.example\ 为 \.env\，并根据需要修改配置（如管理员密码、密钥等）：
   `ash
   # Windows
   copy .env.example .env
   
   # Linux/Mac
   cp .env.example .env
   `
   
   \.env\ 文件内容示例：
   `ini
   ADMIN_EMAIL=admin@example.com
   ADMIN_PASSWORD=admin_password_change_me
   SECRET_KEY=super-secret-key-change-me
   DATABASE_URL=sqlite:///./data.db
   `

4. 运行应用：
   `ash
   uvicorn app.main:app --reload
   `

访问 http://127.0.0.1:8000 进行注册、登录和管理单词。

## Docker 部署

### 使用 Docker Compose (推荐)

1. 确保已安装 Docker 和 Docker Compose。
2. 同样需要先配置 \.env\ 文件（参考上述步骤），Docker Compose 会自动读取其中的环境变量。
3. 运行：
   `ash
   docker-compose up -d
   `
   应用将在端口 8000 上运行，数据将持久化在 \./data\ 目录中。

### 手动构建镜像

1. 构建镜像：
   `ash
   docker build -t ai-word-notebook .
   `

2. 运行容器：
   `ash
   docker run -p 8000:8000 --env-file .env -v E:\English-words-2/data:/app/data ai-word-notebook
   `

## 测试

运行调度器测试：

`ash
python -m pytest
`

## CI/CD
工作流 \.github/workflows/docker-image.yml\ 会在推送到 \main\ 分支时构建并推送 \ghcr.io/<owner>/<repo>/ai-word-notebook:latest\。
