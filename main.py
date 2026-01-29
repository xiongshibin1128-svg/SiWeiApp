import flet as ft
from openai import OpenAI
import json
from datetime import datetime

def main(page: ft.Page):
    # --- 1. 现代化 UI 配置 ---
    page.title = "生命之书：深度思维训练"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.WHITE
    page.theme = ft.Theme(use_material3=True)
    page.scroll = ft.ScrollMode.AUTO

    # --- 2. 状态变量与 AI 配置 ---
    client = OpenAI(
        api_key="sk-de7d9953388c40b08eee22f642e4b0a8",
        base_url="https://api.deepseek.com"
    )

    state = {
        "story": "", "questions": [], "answers": [],
        "current_step": 0
    }

    # --- 3. 核心功能逻辑 ---

    def start_philosophical_session(e):
        """生成 500 字人生案例 + 引导问题（增加进度条反馈）"""
        # 1. 开启进度条，隐藏开始按钮
        btn_start.visible = False
        gen_progress_bar.visible = True
        status_log.value = "🕯️ 正在为您开启今日的生命探索，请稍候..."
        page.update()

        try:
            prompt = (
                "你是一位哲学家。请编写一个约 500 字的真实且感人的人生案例，"
                "内容侧重于生命意义、自我重塑或选择的困境。随后针对 7 维度提出 3 个依次递进的问题。"
                "务必以 JSON 格式返回：{'story': '...', 'questions': ['Q1', 'Q2', 'Q3']}"
            )
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            
            state.update({"story": data["story"], "questions": data["questions"], "answers": [], "current_step": 0})
            
            # 2. 切换界面
            home_view.visible = False
            story_box.value = state["story"]
            update_step_ui()
            session_view.visible = True
        except Exception as ex:
            status_log.value = f"❌ 连接失败: {str(ex)}"
            btn_start.visible = True
        
        gen_progress_bar.visible = False
        page.update()

    def update_step_ui():
        idx = state["current_step"]
        q_label.value = f"第 {idx + 1} 阶段思索：\n{state['questions'][idx]}"
        ans_input.value = ""

    def handle_next_step(e):
        """循序渐进回答逻辑"""
        user_ans = ans_input.value.strip()
        if not user_ans:
            return
        
        state["answers"].append(user_ans)
        if state["current_step"] < 2:
            state["current_step"] += 1
            update_step_ui()
        else:
            run_philosophical_eval()
        page.update()

    def run_philosophical_eval():
        """评分系统：增加圆形进度条防止卡死感"""
        session_view.visible = False
        loading_view.visible = True
        page.update()

        try:
            eval_prompt = (
                f"案例：{state['story']}\n用户的感悟：{state['answers']}\n"
                "请对 7 维度进行严谨评分，每个维度包含得分和 50-100 字的详细扣分说明。"
                "最后提供 200 字以上的局限性分析与提升建议。以 JSON 返回："
                "{'details': [{'name': '...', 'score': 0, 'reason': '...'}], 'summary': '...', 'advice': '...'}"
            )
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": eval_prompt}],
                response_format={"type": "json_object"}
            )
            report = json.loads(response.choices[0].message.content)
            
            # 保存到本地存储
            date_key = datetime.now().strftime("%Y-%m-%d")
            history = page.client_storage.get("growth_history") or {}
            history[date_key] = report
            page.client_storage.set("growth_history", history)

            display_final_report(report)
        except Exception as ex:
            status_log.value = f"❌ 阅卷出错: {str(ex)}"
        
        loading_view.visible = False
        page.update()

    def display_final_report(report):
        report_cards.controls.clear()
        for d in report["details"]:
            report_cards.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Text(d["name"], weight=ft.FontWeight.BOLD), ft.Text(f"{d['score']} 分", color=ft.Colors.INDIGO)]),
                        ft.Text(d["reason"], size=13, color=ft.Colors.GREY_700, line_height=1.4)
                    ]),
                    padding=15, bgcolor=ft.Colors.GREY_50, border_radius=10
                )
            )
        summary_display.value = f"【思维局限性深度分析】\n{report['summary']}\n\n【导师的提升建议】\n{report['advice']}"
        report_view.visible = True
        page.update()

    # --- 4. UI 界面组件 ---

    # 进度条组件
    gen_progress_bar = ft.ProgressBar(width=300, color=ft.Colors.INDIGO, visible=False)
    
    status_log = ft.Text("点击下方按钮，开启今日的心灵之旅", size=12, color=ft.Colors.GREY_500)
    btn_start = ft.ElevatedButton("开始今日思考", on_click=start_philosophical_session, icon=ft.Icons.MENU_BOOK)

    home_view = ft.Column([
        ft.Text("📖 生命之书", size=36, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_900),
        status_log,
        ft.Container(height=20),
        gen_progress_bar, # 进度条放在这里
        btn_start,
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    story_box = ft.Text("", size=15, line_height=1.6, color=ft.Colors.BLACK)
    q_label = ft.Text("", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_700)
    ans_input = ft.TextField(label="写下您的感悟...", multiline=True, min_lines=5, border_radius=10)
    
    session_view = ft.Column([
        ft.Container(content=story_box, padding=25, bgcolor=ft.Colors.INDIGO_50, border_radius=15),
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        q_label,
        ans_input,
        ft.ElevatedButton("回答完毕，进入下一步", on_click=handle_next_step, icon=ft.Icons.AUTO_AWESOME_ROUNDED)
    ], visible=False)

    # 评分时的加载界面
    loading_view = ft.Column([
        ft.ProgressRing(color=ft.Colors.INDIGO),
        ft.Container(height=20),
        ft.Text("导师正在悉心感悟您的文字，生成深度报告中...", text_align=ft.TextAlign.CENTER)
    ], visible=False, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    report_cards = ft.Column(spacing=15)
    summary_display = ft.Text("", size=14, color=ft.Colors.GREY_900, line_height=1.5)
    report_view = ft.Column([
        ft.Text("📊 今日思维画像", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO),
        report_cards,
        ft.Container(content=summary_display, padding=20, bgcolor=ft.Colors.AMBER_50, border_radius=12),
        ft.ElevatedButton("完成修行", on_click=lambda _: page.window_destroy())
    ], visible=False)

    page.add(ft.SafeArea(ft.Column([home_view, session_view, loading_view, report_view])))

ft.app(target=main)
