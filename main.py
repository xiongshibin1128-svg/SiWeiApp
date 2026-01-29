import flet as ft
from openai import OpenAI
import json
from datetime import datetime

def main(page: ft.Page):
    # --- 1. 网页版配置 ---
    page.title = "生命之书"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.WHITE
    # 使用最新 M3 设计，指定靛蓝色种子
    page.theme = ft.Theme(use_material3=True, color_scheme_seed=ft.Colors.INDIGO)
    page.scroll = ft.ScrollMode.AUTO

    # --- 2. AI 配置 ---
    client = OpenAI(
        api_key="sk-de7d9953388c40b08eee22f642e4b0a8",
        base_url="https://api.deepseek.com"
    )

    state = {
        "story": "", "questions": [], "answers": [], "current_step": 0
    }

    # --- 3. 业务逻辑 ---

    def start_session(e):
        """生成阶段"""
        btn_start.visible = False
        progress_bar.visible = True
        status_text.value = "🕯️ 正在为您开启今日的生命探索，AI 撰写中..."
        page.update()

        try:
            prompt = (
                "你是一位哲学家。请编写一个约 500 字的感人人生案例，"
                "侧重生命意义与内心抉择。随后针对 7 个深度思维维度，提出 3 个依次递进的引导问题。"
                "务必以 JSON 格式返回：{'story': '...', 'questions': ['Q1', 'Q2', 'Q3']}"
            )
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            state.update({"story": data["story"], "questions": data["questions"], "answers": [], "current_step": 0})
            
            # 切换到答题页
            home_view.visible = False
            story_box.value = state["story"]
            update_q_ui()
            session_view.visible = True
        except Exception as ex:
            status_text.value = f"❌ 连接失败: {str(ex)}"
            btn_start.visible = True
        
        progress_bar.visible = False
        page.update()

    def update_q_ui():
        idx = state["current_step"]
        q_label.value = f"第 {idx + 1} 阶段思索：\n{state['questions'][idx]}"
        ans_input.value = ""

    def handle_next(e):
        if not ans_input.value.strip(): return
        state["answers"].append(ans_input.value)
        
        if state["current_step"] < 2:
            state["current_step"] += 1
            update_q_ui()
        else:
            run_eval()
        page.update()

    def run_eval():
        """评分阶段"""
        session_view.visible = False
        loading_view.visible = True
        page.update()

        try:
            eval_prompt = (
                f"案例：{state['story']}\n感悟：{state['answers']}\n"
                "请对 7 维度进行严谨评分，含得分和 50 字以上扣分说明。"
                "最后提供 200 字以上提升建议。以 JSON 返回："
                "{'details': [{'name': '...', 'score': 0, 'reason': '...'}], 'summary': '...', 'advice': '...'}"
            )
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": eval_prompt}],
                response_format={"type": "json_object"}
            )
            report = json.loads(response.choices[0].message.content)
            
            # 网页版保存数据到浏览器缓存
            date_key = datetime.now().strftime("%Y-%m-%d")
            history = page.client_storage.get("life_book_db") or {}
            history[date_key] = report
            page.client_storage.set("life_book_db", history)

            show_report(report)
        except Exception as ex:
            loading_view.visible = False
            session_view.visible = True
            page.snack_bar = ft.SnackBar(ft.Text(f"出错: {str(ex)}"))
            page.snack_bar.open = True
        page.update()

    def show_report(report):
        report_items.controls.clear()
        for d in report["details"]:
            report_items.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Text(d["name"], weight="bold"), ft.Text(f"{d['score']} 分", color="blue")]),
                        ft.Text(d["reason"], size=13, color="grey")
                    ]),
                    padding=10, border=ft.border.all(1, "#eeeeee"), border_radius=8
                )
            )
        summary_box.value = f"【深度分析】\n{report['summary']}\n\n【提升建议】\n{report['advice']}"
        report_view.visible = True
        page.update()

    # --- 4. UI 组件 ---
    progress_bar = ft.ProgressBar(width=200, color="indigo", visible=False)
    status_text = ft.Text("点击下方按钮，开启今日心灵之旅", size=12, color="grey")
    btn_start = ft.ElevatedButton("开始今日思考", on_click=start_session, icon=ft.Icons.MENU_BOOK)

    home_view = ft.Column([
        ft.Text("📖 生命之书", size=32, weight="bold", color="indigo"),
        status_text,
        ft.Container(height=20),
        progress_bar,
        btn_start,
    ], horizontal_alignment="center")

    story_box = ft.Text("", size=16, line_height=1.6)
    q_label = ft.Text("", size=18, weight="bold", color="indigo")
    ans_input = ft.TextField(label="您的感悟", multiline=True, min_lines=4)
    
    session_view = ft.Column([
        ft.Container(content=story_box, padding=15, bgcolor=ft.Colors.INDIGO_50, border_radius=10),
        ft.Divider(), q_label, ans_input,
        ft.ElevatedButton("下一步", on_click=handle_next)
    ], visible=False)

    loading_view = ft.Column([ft.ProgressRing(), ft.Text("导师思考中...")], visible=False, horizontal_alignment="center")

    report_items = ft.Column()
    summary_box = ft.Text("")
    report_view = ft.Column([
        ft.Text("📊 思维画像", size=24, weight="bold"),
        report_items,
        ft.Container(content=summary_box, padding=15, bgcolor=ft.Colors.AMBER_50, border_radius=10),
        ft.ElevatedButton("完成", on_click=lambda _: page.window_destroy())
    ], visible=False)

    page.add(ft.SafeArea(ft.Column([home_view, session_view, loading_view, report_view])))

ft.app(target=main)
