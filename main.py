import collections
import os
import base64
import time
import textwrap
from typing import Dict, List, Optional, Tuple, Any


from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.config.astrbot_config import AstrBotConfig
from astrbot.core.star.filter.command import CommandFilter
from astrbot.core.star.filter.command_group import CommandGroupFilter
from astrbot.core.star.star_handler import star_handlers_registry, StarHandlerMetadata


@register(
    "astrbot_plugin_xirohelp", "xiro", "查看所有命令，包括插件，返回一张帮助图片", "1.0.2"
)
class MyPlugin(Star):
    # 内置指令文本，带 (admin) 标记的仅管理员可见
    BUILT_IN_COMMANDS_TEXT = textwrap.dedent("""
        /help : 查看帮助
        /llm : 开启/关闭 LLM (admin)
        /plugin : 插件管理 (admin)
        /plugin ls : 获取已经安装的插件列表 (admin)
        /plugin off : 禁用插件 (admin)
        /plugin on : 启用插件 (admin)
        /plugin get : 安装插件 (admin)
        /plugin help : 获取插件帮助 (admin)
        /t2i : 开关文本转图片
        /tts : 开关文本转语音（会话级别）
        /sid : 获取会话 ID 和 管理员 ID
        /op : 授权管理员 (admin)
        /deop : 取消授权管理员 (admin)
        /wl : 添加白名单
        /dwl : 删除白名单 (admin)
        /provider : 查看或者切换 LLM Provider (admin)
        /reset : 重置 LLM 会话
        /stop : 停止当前会话中正在运行的 Agent
        /model : 查看或者切换模型 (admin)
        /history : 查看对话记录
        /ls : 查看对话列表
        /new : 创建新对话
        /groupnew : 创建新群聊对话 (admin)
        /switch : 通过 /ls 前面的序号切换对话
        /rename : 重命名对话
        /del : 删除当前对话
        /key : 查看或者切换 Key (admin)
        /persona : 查看或者切换 Persona (admin)
        /dashboard_update : 更新管理面板 (admin)
        /set : 无描述
        /unset : 无描述
        /alter_cmd : 修改命令权限 (admin)
    """).strip()

    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self.logo_path = os.path.join(os.path.dirname(__file__), "astrbot_logo.jpg")
        self.template_path = os.path.join(os.path.dirname(__file__), "help.html")

    @filter.command("helps", alias={"帮助", "菜单", "功能"})
    async def get_help(self, event: AstrMessageEvent):
        """获取普通用户帮助信息"""
        async for result in self._show_help(event, is_admin=False):
            yield result

    @filter.command("adminhelps", alias={"管理帮助", "后台菜单", "管理菜单"})
    async def get_admin_help(self, event: AstrMessageEvent):
        """获取管理员帮助信息"""
        if not event.is_admin:
            yield event.plain_result("抱歉，此命令仅管理员可用。")
            return
        async for result in self._show_help(event, is_admin=True):
            yield result

    async def _show_help(self, event: AstrMessageEvent, is_admin: bool):
        """渲染并发送帮助信息"""
        plugin_commands_dict = self.get_all_commands(is_admin)
        if not plugin_commands_dict:
            yield event.plain_result("没有找到任何插件或命令")
            return
            
        # 进一步处理和分组
        sections = self._parse_plugin_commands_sorted_grouped(plugin_commands_dict, is_admin)
        
        # 准备模板数据
        plugins_data = []
        for name, cmds in sections:
            plugins_data.append({
                "name": name,
                "commands": [{"name": c, "desc": d} for c, d in cmds]
            })

        # 读取头像并转为 base64
        logo_base64 = ""
        help_avatar = self.config.get("help_avatar", [])
        avatar_path = ""
        
        if help_avatar:
            # v4.13.0 的 file 类型返回的是列表
            avatar_path = help_avatar[0] if isinstance(help_avatar, list) and help_avatar else help_avatar
            
        if avatar_path and isinstance(avatar_path, str):
            if avatar_path.startswith(("http://", "https://")):
                # 如果是网络图片，我们不能直接读取文件，但在 HTML 模板中可以直接使用 URL
                # 为了保持逻辑一致，我们这里如果是 URL 就直接把 URL 给 logo_base64，模板里需要适配
                logo_base64 = avatar_path
            elif os.path.exists(avatar_path):
                with open(avatar_path, "rb") as f:
                    logo_base64 = base64.b64encode(f.read()).decode("utf-8")
            else:
                # 尝试作为相对路径
                relative_path = os.path.join(os.path.dirname(__file__), avatar_path)
                if os.path.exists(relative_path):
                    with open(relative_path, "rb") as f:
                        logo_base64 = base64.b64encode(f.read()).decode("utf-8")
        
        # 如果没有配置头像或读取失败，使用默认 logo
        if not logo_base64 and os.path.exists(self.logo_path):
            with open(self.logo_path, "rb") as f:
                logo_base64 = base64.b64encode(f.read()).decode("utf-8")

        # 读取 HTML 模板
        with open(self.template_path, "r", encoding="utf-8") as f:
            template = f.read()

        # 渲染 HTML 转图片
        # 按照文档说明，使用 self.html_render
        if is_admin:
            help_title = self.config.get("admin_help_title", "AstrBot 管理员控制台")
            help_subtitle = self.config.get("admin_help_subtitle", "这里是系统管理员的专属功能")
        else:
            help_title = self.config.get("help_title", "AstrBot 帮助菜单")
            help_subtitle = self.config.get("help_subtitle", "")

        render_data = {
            "help_title": help_title,
            "help_subtitle": help_subtitle,
            "plugins": plugins_data,
            "logo_base64": logo_base64,
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        try:
            # 使用文档推荐的 html_render 接口
            # 增加 scale: css 确保尺寸稳定，使用 jpeg 优化传输速度
            image_url = await self.html_render(template, render_data, options={
                "type": "jpeg",
                "quality": 85,
                "scale": "css",
                "full_page": True
            })
            yield event.image_result(image_url)
        except Exception as e:
            logger.error(f"HTML 渲染失败: {e}")
            yield event.plain_result(f"帮助菜单生成失败，请联系管理员。错误: {e}")

    def get_all_commands(self, is_admin: bool = False) -> Dict[str, List[str]]:
        """获取所有其他插件及其命令列表, 格式为 {plugin_name: [command#desc]}"""
        plugin_commands: Dict[str, List[str]] = collections.defaultdict(list)
        
        # 获取插件显示名称映射
        name_map = {}
        plugin_name_map = self.config.get("plugin_name_map", [])
        if isinstance(plugin_name_map, list):
            for entry in plugin_name_map:
                for sep in (":", "#"):
                    if sep in entry:
                        orig, custom = entry.split(sep, 1)
                        name_map[orig.strip()] = custom.strip()
                        break

        try:
            all_stars_metadata = self.context.get_all_stars()
            all_stars_metadata = [star for star in all_stars_metadata if star.activated]
        except Exception as e:
            logger.error(f"获取插件列表失败: {e}")
            return {}
            
        if not all_stars_metadata:
            return {}
            
        for star in all_stars_metadata:
            plugin_name = getattr(star, "name", "未知插件")
            # 使用映射后的名称
            display_name = name_map.get(plugin_name, plugin_name)
            
            plugin_instance = getattr(star, "star_cls", None)
            module_path = getattr(star, "module_path", None)
            
            if plugin_name in ["astrbot", "astrbot_plugin_xirohelp", "astrbot-reminder", "builtin_commands"]:
                continue
                
            if not plugin_name or not module_path or not isinstance(plugin_instance, Star):
                continue
            if plugin_instance is self:
                continue
                
            for handler in star_handlers_registry:
                if not isinstance(handler, StarHandlerMetadata):
                    continue
                if handler.handler_module_path != module_path:
                    continue
                    
                command_name: Optional[str] = None
                description: Optional[str] = handler.desc
                is_admin_cmd = False
                
                for filter_ in handler.event_filters:
                    if isinstance(filter_, CommandFilter):
                        command_name = filter_.command_name
                    elif isinstance(filter_, CommandGroupFilter):
                        command_name = filter_.group_name
                    else:
                        # 动态判断是否为权限过滤器。
                        # 在 AstrBot 中，权限过滤器的属性通常包含 permission_type
                        p_type = getattr(filter_, "permission_type", None)
                        if p_type is not None and str(p_type).endswith(".ADMIN"):
                            is_admin_cmd = True
                        elif hasattr(filter_, "permission_type") and p_type == filter.PermissionType.ADMIN:
                            is_admin_cmd = True
                        
                if command_name:
                    # 如果不是管理员，且描述中包含 (admin)，或者指令本身是管理员权限，则在普通帮助中跳过
                    is_admin_desc = description and "(admin)" in description
                    
                    # 严格分离：普通帮助仅显示普通指令，管理员帮助仅显示管理员指令
                    if is_admin:
                        # 管理员帮助：仅显示带有管理员标记或权限的指令
                        if not (is_admin_cmd or is_admin_desc):
                            continue
                    else:
                        # 普通帮助：仅显示不带管理员标记或权限的指令
                        if is_admin_cmd or is_admin_desc:
                            continue
                        
                    formatted_command = f"{command_name}#{description}" if description else command_name
                    if formatted_command not in plugin_commands[display_name]:
                        plugin_commands[display_name].append(formatted_command)
        return dict(plugin_commands)

    def _parse_single_command_list(self, text_list, is_admin: bool = True) -> List[Tuple[str, str | None]]:
        commands = []
        lines = text_list.strip().splitlines() if isinstance(text_list, str) else [ln for ln in text_list if ln.strip()]

        for line in lines:
            raw = line
            stripped = line.strip()
            if not stripped or (stripped.startswith("[") and stripped.endswith("]")):
                continue
                
            # 管理员指令过滤逻辑
            is_admin_entry = "(admin)" in stripped
            
            if is_admin:
                # 管理员帮助：仅显示管理员指令
                if not is_admin_entry:
                    continue
            else:
                # 普通用户帮助：仅显示非管理员指令
                if is_admin_entry:
                    continue
                
            if (raw.startswith("  ") or raw.startswith("\t")) and commands:
                cmd, desc = commands[-1]
                commands[-1] = (cmd, (desc or "") + stripped)
                continue

            parts = None
            for sep in (" : ", " # ", "#", ":"):
                if sep in stripped:
                    parts = stripped.split(sep, 1)
                    break
            if parts and len(parts) == 2:
                cmd = parts[0][2:].strip() if parts[0].startswith("- ") else parts[0].strip()
                desc = parts[1].strip()
                # 去掉 desc 中的 (admin) 标记
                if desc:
                    desc = desc.replace("(admin)", "").strip()
            else:
                cmd = stripped[2:].strip() if stripped.startswith("- ") else stripped
                desc = None
            commands.append((cmd, desc))

        return [(c, (d.splitlines()[0].strip() if d else None)) for c, d in commands]

    def _parse_plugin_commands_sorted_grouped(self, plugin_dict: Dict[str, Any], is_admin: bool = True) -> List[Tuple[str, List[Tuple[str, str | None]]]]:
        # 是否显示内置指令
        show_builtin = self.config.get("show_builtin_cmds", False)
        if show_builtin:
            built_in_list = self._parse_single_command_list(self.BUILT_IN_COMMANDS_TEXT, is_admin)
            built_in_plugin = ("内部指令", built_in_list) if built_in_list else None
        else:
            built_in_plugin = None

        large_plugins, small_plugins = [], []
        blacklist = self.config.get("plugin_blacklist", [])
        
        for name, cmds_raw in plugin_dict.items():
            if name in ["内部指令", "builtin_commands"] or not cmds_raw:
                continue
            if name in blacklist:
                continue
            cmds = self._parse_single_command_list(cmds_raw, is_admin)
            if not cmds:
                continue
            (small_plugins if len(cmds) == 1 else large_plugins).append((name, cmds))

        large_plugins.sort(key=lambda x: len(x[1]), reverse=True)

        grouped_small_plugin = None
        if small_plugins:
            all_small = [c for _, cmds in small_plugins for c in cmds]
            if all_small:
                grouped_small_plugin = ("简易指令", all_small)

        result = []
        if built_in_plugin:
            result.append(built_in_plugin)
        result.extend(large_plugins)
        if grouped_small_plugin:
            result.append(grouped_small_plugin)

        # 添加自定义命令
        custom_cmds = self.config.get("custom_cmds", [])
        if custom_cmds:
            # 如果 custom_cmds 是列表，拼成字符串供解析
            custom_text = "\n".join(custom_cmds) if isinstance(custom_cmds, list) else custom_cmds
            custom_list = self._parse_single_command_list(custom_text, is_admin)
            if custom_list:
                result.append(("自定义命令", custom_list))

        return result
