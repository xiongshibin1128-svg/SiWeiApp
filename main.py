import flet as ft
from openai import OpenAI
import json

def main(page: ft.Page):
    # --- 1. 强制视觉修复 ---
    page.title = "7维思维特训 Pro (调试版)"
    page.theme_mode = ft.ThemeMode.LIGHT 
    page.bgcolor = ft.Colors.WHITE
    page.theme = ft.Theme(use_material3=False) 
    page.scroll = ft.ScrollMode.AUTO

    # --- 2. 状态看板 (破案关键) ---
    debug_status = ft.Text("系统检查中...", color=ft.Colors.GREY_700, size=12)
    
    # --- 3. 核心 AI 客户端 ---
    try:
        client = OpenAI(
            api_key="sk-de7d9953388c40b08eee22f642e4b0a8",
            base_url="https://api.deepseek.com"
        )
        debug_status.value = "✅ AI 引擎初始化成功"
    except Exception as e:
        debug_status.value = f"❌ 引擎初始化失败: {str(e)}"
        debug_status.color = ft.Colors.RED

    # --- 4. 换题逻辑 ---
    def get_topic(e):
        btn_action.disabled = True
        debug_status.value = "⏳ AI 正在连接网络中..."
        debug_status.color = ft.Colors.BLUE
        page.update()

        try:
            # 这是一个简单的测试请求，确保 AI 能通
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": "请出一道关于职场沟通的思维题，300字内。"}]
            )
            case_text.value = response.choices[0].message.content
            debug_status.value = "✅ AI 联网成功！内容已更新"
            debug_status.color = ft.Colors.GREEN
        except Exception as err:
            # 🌟 如果这里报错，你会直接在手机屏幕上看到原因
            debug_status.value = f"❌ 联网报错: {str(err)}"
            debug_status.color = ft.Colors.RED
        
        btn_action.disabled = False
        page.update()

    # --- 5. UI 界面 ---
    case_text = ft.Text("点击下方按钮，开始 AI 深度训练...", size=16, color=ft.Colors.BLACK)

    btn_action = ft.ElevatedButton(
        "获取新案例",
        icon="psychology",
        on_click=get_topic,
        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE)
    )

    page.add(
        ft.SafeArea(
            ft.Column([
                ft.Text("🚀 7维思维特训", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                debug_status,
                ft.Divider(height=20),
                ft.Container(
                    content=case_text,
                    padding=20, bgcolor=ft.Colors.GREY_50, border_radius=10,
                    border=ft.border.all(1, ft.Colors.GREY_300)
                ),
                ft.Container(height=30),
                btn_action
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
    )

ft.app(target=main)
