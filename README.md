# astrbot_plugin_help

<div align="center">

![:astrbot_plugin_help](https://count.getloli.com/@:astrbot_plugin_help?theme=minecraft)

_✨ 高颜值、自动化的 [AstrBot](https://github.com/Soulter/AstrBot) 帮助菜单插件 ✨_

[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![AstrBot](https://img.shields.io/badge/AstrBot-3.4%2B-orange.svg)](https://github.com/Soulter/AstrBot)
[![Author](https://img.shields.io/badge/作者-xiro-blue)](https://github.com/soarnext)
[![Version](https://img.shields.io/badge/版本-v1.0-red)](https://github.com/soarnext/astrbot_plugin_help)

</div>

## 🤝 介绍

`astrbot_plugin_help` 是一款为 AstrBot 打造的帮助菜单插件。它能够自动扫描所有已激活插件的指令，并生成一张精美的帮助图片。支持权限分离、自定义头像、名称映射等丰富功能。

## ✨ 特性

- 🎨 **高颜值渲染**：基于 HTML 渲染，排版优雅，支持自定义头像。
- 🛡️ **权限分离**：自动识别管理员指令，普通用户与管理员看到的菜单互不干扰。
- ⚙️ **灵活配置**：支持插件黑名单、自定义名称映射、自定义额外指令等。
- 🚀 **自动化**：自动隐藏内置指令（可选）及 `builtin_commands`，自动排版适配。

## 📦 安装

1. 在 AstrBot 插件市场搜索 `astrbot_plugin_help` 并点击安装。
2. 或手动安装：
   ```bash
   cd /path/to/AstrBot/data/plugins
   git clone https://github.com/soarnext/astrbot_plugin_help
   ```
3. 重启 AstrBot 即可生效。

## 🐔 使用说明

### 指令表

| 指令 | 别名 | 权限 | 说明 |
| :--- | :--- | :--- | :--- |
| `/helps` | 帮助、菜单、功能 | 所有人 | 生成普通用户帮助图（仅含非管理员指令） |
| `/adminhelp` | 管理帮助、后台菜单 | 管理员 | 生成管理员帮助图（仅含管理员指令） |

## ⚙️ 配置项介绍

| 配置项 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `help_title` | 帮助菜单标题 | `AstrBot 帮助菜单` |
| `help_subtitle` | 帮助菜单副标题 | `(空)` (为空时自动紧凑排版) |
| `admin_help_title` | 管理员帮助标题 | `AstrBot 管理员控制台` |
| `help_avatar` | 菜单左上角头像 | `(默认 Logo)` |
| `plugin_blacklist` | 插件黑名单 | `["builtin_commands"]` |
| `plugin_name_map` | 插件显示名称映射 | `[]` (格式：`原始名: 自定义名`) |
| `show_builtin_cmds` | 是否显示内部指令 | `false` |
| `custom_cmds` | 自定义额外命令 | `[]` |

## 📄 开源协议

[MIT License](LICENSE)

---
[帮助文档](https://astrbot.app) | [GitHub 仓库](https://github.com/soarnext/astrbot_plugin_help)
