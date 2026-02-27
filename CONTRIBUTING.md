# Contributing to ClawChat

感谢你对 ClawChat 的兴趣！🎉

## 如何贡献

### 1. 报告 Bug

如果你发现了 Bug，请创建一个 Issue 并包含以下信息：

- Bug 的简要描述
- 复现步骤
- 预期行为 vs 实际行为
- 环境信息 (浏览器、操作系统等)

### 2. 提出新功能

欢迎提出新功能！请创建 Issue 并描述：

- 功能描述
- 使用场景
- 可能的实现方案

### 3. 提交代码

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 开发环境设置

```bash
# 克隆项目
git clone https://github.com/yourusername/ClawChat.git
cd ClawChat/web

# 复制环境配置
cp .env.example .env

# 编辑 .env 填入你的 Gateway Token
# GATEWAY_TOKEN=your_token_here

# 启动开发服务器
python3 server.py
```

## 代码规范

- Python: 遵循 PEP 8
- JavaScript: 使用 ES6+ 语法
- Vue.js: 使用 Composition API

## 问题

如果你有任何问题，请随时创建 Issue。

---

感谢你的贡献！ ❤️
