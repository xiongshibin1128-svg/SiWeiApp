import flet as ft
import traceback # 🌟 核心：用于捕捉错误真相

def main(page: ft.Page):
    # 🌟 强制最简配置，排除渲染干扰
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.WHITE
    page.scroll = ft.ScrollMode.AUTO

    def handle_exception(e_text):
        """如果出错了，把错误直接写在屏幕上"""
        page.clean()
        page.add(
            ft.Text("❌ 程序运行出错了！", size=30, color="red", weight="bold"),
            ft.Text("请把下面的内容截图发给 AI：", size=16),
            ft.Container(
                content=ft.Text(e_text, color="red", selectable=True),
                padding=10, bgcolor="#FFF0F0", border_radius=5
            )
        )
        page.update()

    try:
        # --- 这里放你原来的业务逻辑 ---
        from openai import OpenAI
        
        # 调试文字
        status = ft.Text("系统启动中...", color="blue")
        page.add(ft.SafeArea(ft.Column([
            ft.Text("📖 生命之书：诊断版", size=24, weight="bold"),
            status,
            ft.ElevatedButton("点击测试 AI 连接", 
                on_click=lambda _: status.update(value="正在尝试连接 AI..."))
        ])))
        
        # 模拟一个可能的错误点（比如 API Key 未定义等）
        # 这里如果报错，会被下方的 except 抓住
        
    except Exception:
        # 🌟 关键：捕捉所有报错并显示
        error_info = traceback.format_exc()
        handle_exception(error_info)

ft.app(target=main)
