# 在线英语单词本 - 产品与架构规范

## 目标
- 提供多语言（中文/英文）的网页体验，用于收集、完善和复习词汇。
- 利用 AI 补全功能，通过标准化的 JSON 结果（定义、词性、翻译、例句）丰富部分提供的单词数据。
- 支持管理员和学习者两种角色，提供轻量级、美观的 UI，并支持浅色/深色主题。

## 角色
- **管理员 (Admin)**：管理用户、AI 提供商/密钥、速率限制和模型预设。需要受保护的控制台。
- **用户 (User)**：注册/登录，维护个人单词本，请求 AI 补全，并练习抽认卡。

## 核心用户流程
1. **注册/登录**
   - 邮箱/密码或社交登录；每个用户存储语言偏好。
   - 首次登录时，提示选择界面语言（中文/英文）和主题。

2. **添加单词**
   - 接受部分数据：仅中文、仅英文或两者都有。
   - 用户选择翻译方向：中→英 或 英→中（支持多种词性）。
   - UI 表单：基础单词、可选词性、含义、备注。
   - 用户可以将当前条目发送给 AI 进行补全。

3. **AI 补全**
   - 请求被路由到 AI 服务，使用标准化提示词，期望严格的 JSON 格式：
     ```json
     {
       "word": "",
       "phonetics": {
         "uk": "",
         "us": ""
       },
       "partsOfSpeech": [
         {"pos": "noun", "meaningEn": "", "meaningZh": ""}
       ],
       "examples": [
         {"sentenceEn": "", "sentenceZh": ""}
       ],
       "synonyms": [""],
       "antonyms": [""],
       "direction": "zh_to_en | en_to_zh"
     }
     ```
   - 后端在保存前验证 JSON 模式。
   - 管理员可以配置模型名称、温度和最大 token 数；按租户存储。

4. **抽认卡 (基于艾宾浩斯)**
   - 用户选择复习方向：英→中 或 中→英。
   - 用户选择复习单词数量；后端根据间隔重复计划（艾宾浩斯间隔：5分钟, 30分钟, 12小时, 1天, 2天, 4天, 7天...）抽取单词。
   - 复习界面显示单个提示，并有三个按钮：**认识**、**模糊**、**不认识**。
   - 响应会更新下次复习日期（模糊/不认识会缩短间隔；认识会延长间隔）。

5. **单词本管理**
   - 对单词、标签和复习状态进行增删改查 (CRUD)。
   - 批量导入/导出 (CSV/JSON)，支持语言自动检测。

## 非功能性需求
- 极简 UI，主题切换和语言切换始终可见。
- 响应式布局，适配移动端/桌面端。
- 可审计的管理员操作；AI 使用日志。
- 基于角色的访问控制。
- AI 端点的速率限制。
- 持久化：使用 SQLite 进行初始存储，保持操作简单和可移植。
- 打包：单容器 Docker 部署，包含应用 + 数据库。
- CI/CD：GitHub Action 构建并发布最新的容器镜像。

## 数据模型 (初始)
- **User**: id, email, password hash, role (admin/user), locale, theme, createdAt.
- **WordEntry**: id, ownerId, baseText, language (en/zh), phonetics (JSON), partsOfSpeech (JSON array), examples (JSON array), synonyms, antonyms, tags, direction, createdAt, updatedAt.
- **ReviewSchedule**: id, wordId, userId, lastReviewedAt, nextReviewAt, easinessFactor, intervalIndex, successStreak.
- **AIConfig**: id, provider, model, apiKey alias/secret store pointer, temperature, maxTokens, rateLimit.
- **AuditLog**: id, actorId, action, payload, createdAt.

## 部署与运维
- **运行时**: 单个 Docker 容器，包含 Web 应用程序和 SQLite 数据库文件（建议挂载卷以确保持久性）。
- **环境**: 镜像应暴露最少的环境变量用于机密信息（管理员种子用户、AI 提供商密钥、默认语言）。
- **CI/CD**: GitHub Action 在推送到 main 分支时构建容器，并发布 `latest` 标签以便快速部署。

## API 草图
- `POST /api/auth/register` / `POST /api/auth/login`.
- `GET/POST/PUT/DELETE /api/words` 用于 CRUD。
- `POST /api/words/:id/complete` 触发 AI 补全；返回验证后的 JSON。
- `POST /api/review/plan` 带 `{ count, direction }` 返回选定的单词。
- `POST /api/review/:id/answer` 根据用户响应更新复习计划。
- `GET/PUT /api/admin/ai-config` (仅管理员) 用于提供商/模型设置。
- `GET /api/admin/users` 和角色更新。

## AI 提示词指南
- 包含方向标志（中→英 或 英→中）和提供的字段。
- 强制仅返回 JSON；如果非 JSON 则拒绝。
- 包含至少两个带有翻译的例句。

## UX 说明
- 落地页：快速添加表单 + 练习 CTA。
- 复习页面：键盘快捷键（1: 认识, 2: 模糊, 3: 不认识）。
- 顶部标题栏中的主题和语言切换；记住偏好。
- 管理员控制台使用表格视图查看用户和 AI 配置。

## 未来增强
- 音标发音播放。
- 名词的图像关联。
