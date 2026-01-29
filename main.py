import flet as ft
import random
import time
import json
import os
from datetime import datetime
from openai import OpenAI

# --- 1. 定义 7 大思维能力 ---
SKILL_QUESTIONS = [
    ("批判性思维", "这件事里的信息真实吗？有逻辑漏洞吗？是事实还是观点？"),
    ("复盘反思", "如果让你重新处理这件事，你会在哪个环节做得不一样？"),
    ("发散性思维", "除了目前的做法，还有哪些看似荒谬但可行的方案？"),
    ("结构化思维", "请把这件事拆解成 3 个关键步骤或要素 (1, 2, 3)。"),
    ("共情能力", "事件中的核心人物当时是什么情绪？他的痛点是什么？"),
    ("系统性思维", "这件事发生后，会引发什么样的连锁反应（蝴蝶效应）？"),
    ("第一性原理", "抛开表象，这件事最本质的核心目标（底层的 1）是什么？")
]

# --- 🛡️ 离线保底题库 ---
BACKUP_TOPICS = [
    "【中年危机】35岁大厂程序员被裁，背着房贷不敢告诉家人，每天假装出门上班，在星巴克坐一整天。这种生活该如何破局？",
    "【彩礼之争】谈了5年的情侣，因为女方父母坚持要28万彩礼用于给弟弟买房，男方愤而分手。这不仅是钱的问题，更是价值观的碰撞。",
    "【全职妈妈】名校硕士毕业当全职妈妈，5年后想重返职场却屡屡碰壁，还被丈夫嫌弃“不挣钱”。她的价值到底在哪里？",
]

# --- ⏳ 加载时的趣味提示语 ---
LOADING_TIPS = [
    "🤖 AI 正在疯狂挠头构思剧本中...",
    "🌍 正在连接宇宙脑电波，请稍候...",
    "📖 DeepSeek 正在翻阅《人类迷惑行为大赏》...",
    "☕ 喝口水，精彩的大瓜马上就来...",
    "🤔 正在为您编造一个惊心动魄的故事...",
    "🐢 网速有点慢，正在骑自行车去抓数据...",
]

def main(page: ft.Page):
    page.title = "Day 4: 思维进阶训练营"
    
    # 【修复关键点 1】强制使用浅色模式 (解决文字看不清的问题)
    page.theme_mode = ft.ThemeMode.LIGHT 
    
    # 【修复关键点 2】关闭 Material 3 的默认变色 (让卡片变回纯净的白色)
    page.theme = ft.Theme(use_material3=False)
    
    page.bgcolor = "#F5F7FA"
    page.scroll = ft.ScrollMode.AUTO

    current_mode = "random"

    # ==========================================
    # 👇 请在这里确认你的 KEY 是否正确
    # ==========================================
    client = OpenAI(
        api_key="sk-de7d9953388c40b08eee22f642e4b0a8", 
        base_url="https://api.deepseek.com"
    )

    # ==========================================
    # 💾 数据存储功能
    # ==========================================
    def save_history_record(topic, user_answers, ai_report):
        record = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "topic": topic,
            "user_answers": user_answers,
            "score": ai_report.get("total_score", 0),
            "ai_details": ai_report.get("details", [])
        }
        history_list = page.client_storage.get("history_list")
        if history_list is None:
            history_list = []
        history_list.insert(0, record)
        page.client_storage.set("history_list", history_list)

    def load_history_records():
        history_list = page.client_storage.get("history_list")
        if history_list is None:
            return []
        return history_list

    # ==========================================
    # 📡 数据获取区
    # ==========================================
    def get_ai_life_story():
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一位深刻的现实主义小说家。"},
                    {"role": "user",
                     "content": "请写一个**详细的**（300字左右）、关于【普通人生活困境、职场潜规则、家庭隐形矛盾】的微故事。要求：\n1. 有具体的人物和场景。\n2. 必须有激烈的**内心冲突**或**对话**。\n3. 不要直接给结局，留出思考空间。\n\n例如：写一个想辞职去流浪的乖乖女，面对父母催婚和体面工作的撕扯。"}
                ]
            )
            return "【📖 AI 深度生活案例】\n\n" + response.choices[0].message.content
        except Exception as e:
            return f"AI 思考超时: {e}"

    def get_ai_fake_news():
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一位资深的社会新闻评论员。"},
                    {"role": "user",
                     "content": "请虚构一个极具争议的**社会热点新闻**（300字左右）。\n内容包括：\n1. 【新闻标题】（惊悚一点）\n2. 【事件经过】（包含反转或细节）\n3. 【网友评论】（模拟两派截然不同的观点互喷）\n\n主题可以是：教育内卷、性别对立、职场整顿、老人碰瓷等。"}
                ]
            )
            return "【🔥 AI 模拟社会热点】\n(注：此为AI生成供训练用的虚拟案例)\n\n" + response.choices[0].message.content
        except Exception as e:
            topic = random.choice(BACKUP_TOPICS)
            return f"【离线精选】\n\n{topic}"

    def get_ai_evaluation(formatted_answer):
        system_prompt = """
        你是一位严厉的思维导师。用户会根据 7 个维度分别回答 7 个问题。
        请根据用户的回答，严格给这 7 个能力分别打分（0-100）。
        务必严格按照 JSON 格式返回：
        {"total_score": int, "details": [{"name": "批判性思维", "score": int, "reason": "str", "advice": "str"}, ...]}
        """
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"用户回答：\n{formatted_answer}"},
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            time.sleep(1)
            return {"total_score": 0,
                    "details": [{"name": "网络错误", "score": 0, "reason": "评分失败", "advice": "请检查网络"}]}

    # ==========================================
    # 🎨 界面组件区
    # ==========================================
    
    current_case_text = ft.Text("", size=16, color="#333333", visible=True)

    loading_spinner = ft.Container(
        content=ft.Column(
            controls=[
                ft.ProgressRing(width=40, height=40, stroke_width=4, color="blue"),
                ft.Container(height=10),
                ft.Text("正在思考中...", size=14, color="grey", ref=ft.Ref()),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        height=300,
        alignment=ft.Alignment(0, 0), 
        visible=False
    )

    question_container = ft.Container(
        content=ft.Stack(controls=[current_case_text, loading_spinner]),
        padding=20, bgcolor="white", border_radius=10, 
        border=ft.border.all(1, "#dddddd"),
    )

    dlg_case = ft.AlertDialog(
        title=ft.Text("内容详情"),
        content=ft.Text(""),
        actions=[ft.TextButton("关闭", on_click=lambda e: page.close(dlg_case))],
    )

    def show_case_dialog(content_text):
        dlg_case.content.value = content_text
        page.open(dlg_case)
        page.update()

    def refresh_question(e):
        btn_refresh.disabled = True
        btn_refresh.text = "构思中..."

        current_case_text.visible = False
        loading_spinner.visible = True
        loading_spinner.content.controls[2].value = random.choice(LOADING_TIPS)
        page.update()

        new_content = ""
        if current_mode == "life":
            new_content = get_ai_life_story()
        elif current_mode == "news":
            new_content = get_ai_fake_news()
        else:
            new_content = current_case_text.value

        current_case_text.value = new_content
        for item in input_fields_refs: item['field'].value = ""

        loading_spinner.visible = False
        current_case_text.visible = True
        btn_refresh.disabled = False
        btn_refresh.text = "换一题"
        page.update()

    btn_refresh = ft.ElevatedButton(
        "换一题", icon="refresh", icon_color="blue", color="blue", bgcolor="#E3F2FD",
        on_click=refresh_question, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
    )

    input_fields_refs = []
    exam_controls_list = [
        ft.Row([
            ft.Text("🧐 深度思考 7 步法", size=24, weight="bold"),
            ft.Container(expand=True),
            btn_refresh
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        question_container,
        ft.Container(height=10),
        ft.Text("请依次回答以下 7 个引导问题：", color="blue", weight="bold"),
        ft.Divider(),
    ]

    for skill_name, question_text in SKILL_QUESTIONS:
        exam_controls_list.append(ft.Text(f"【{skill_name}】", weight="bold", size=16))
        exam_controls_list.append(ft.Text(f"❓ {question_text}", size=14, color="grey"))
        field = ft.TextField(hint_text="在此输入...", multiline=True, min_lines=2, border_radius=8, bgcolor="white",
                             text_size=14)
        input_fields_refs.append({"skill": skill_name, "field": field})
        exam_controls_list.append(field)
        exam_controls_list.append(ft.Container(height=15))

    def submit_answer(e):
        full_answer_text = ""
        is_empty = True
        for item in input_fields_refs:
            content = item['field'].value
            if content: is_empty = False
            full_answer_text += f"【{item['skill']}】：{content}\n"

        if is_empty:
            page.snack_bar = ft.SnackBar(ft.Text("请至少回答一个问题"))
            page.snack_bar.open = True
            page.update()
            return

        btn_submit.text = "AI 阅卷中..."
        btn_submit.disabled = True
        page.update()

        report = get_ai_evaluation(full_answer_text)
        save_history_record(current_case_text.value, full_answer_text, report)
        render_result_page(report)

        view_home.visible = False
        view_exam.visible = False
        view_history.visible = False
        view_result.visible = True
        page.floating_action_button = None

        btn_submit.text = "提交所有回答"
        btn_submit.disabled = False
        page.update()

    btn_submit = ft.ElevatedButton("提交所有回答", width=300, height=50, bgcolor="blue", color="white",
                                   on_click=submit_answer)
    exam_controls_list.append(btn_submit)
    exam_controls_list.append(ft.TextButton("放弃本次训练", on_click=lambda e: reset_app()))

    view_exam = ft.Column(controls=exam_controls_list, horizontal_alignment="center", visible=False)

    history_list_container = ft.Column(scroll=ft.ScrollMode.AUTO)

    def render_history_page():
        records = load_history_records()
        history_list_container.controls.clear()

        if not records:
            history_list_container.controls.append(ft.Text("暂无训练记录，快去开始第一次训练吧！", size=16, color="grey"))
        else:
            for rec in records:
                score = rec.get('score', 0)
                score_color = "green" if score >= 80 else "orange" if score >= 60 else "red"
                details_controls = [
                    ft.Text("📝 题目内容：", weight="bold"),
                    ft.Container(content=ft.Text(rec.get('topic', '')[:100] + "..."), padding=10, bgcolor="#f0f0f0",
                                 border_radius=5),
                    ft.Container(height=10),
                    ft.Text("🤖 AI 评语详情：", weight="bold"),
                ]
                for det in rec.get('ai_details', []):
                    details_controls.append(
                        ft.Text(f"{det['name']}: {det['score']}分 - {det['advice']}", size=13)
                    )
                tile = ft.ExpansionTile(
                    title=ft.Text(f"{rec['date']}", weight="bold"),
                    subtitle=ft.Text(f"得分: {score} 分", color=score_color),
                    leading=ft.Icon("history", color="blue"),
                    controls=[ft.Container(content=ft.Column(details_controls), padding=15)]
                )
                history_list_container.controls.append(tile)
        page.update()

    view_history = ft.Column(
        controls=[
            ft.Row([
                ft.IconButton("arrow_back", on_click=lambda e: reset_app()),
                ft.Text("📜 历史训练档案", size=24, weight="bold"),
            ]),
            ft.Divider(),
            history_list_container
        ],
        visible=False
    )

    loading_ring_home = ft.ProgressRing(visible=False)

    def go_to_exam(mode):
        nonlocal current_mode
        current_mode = mode
        loading_ring_home.visible = True
        view_home.visible = False
        page.update()
        time.sleep(0.1)
        refresh_question(None)
        loading_ring_home.visible = False
        view_exam.visible = True
        page.floating_action_button = ft.FloatingActionButton(
            icon="article_outlined", text="看题", bgcolor="blue",
            on_click=lambda e: show_case_dialog(current_case_text.value)
        )
        page.update()

    def go_to_history(e):
        view_home.visible = False
        view_history.visible = True
        render_history_page()
        page.update()

    def create_mode_card(title, icon, color, mode_key):
        return ft.GestureDetector(
            on_tap=lambda e: go_to_exam(mode_key),
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(icon, size=50, color=color),
                    ft.Text(title, size=18, weight="bold", color="#333333"),
                    ft.Text("点击开始 ->", size=12, color="grey")
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=150, height=180, bgcolor="white", border_radius=15,
                shadow=ft.BoxShadow(blur_radius=15, color="#1A000000", offset=ft.Offset(0, 5))
            )
        )

    btn_history = ft.Container(
        content=ft.Row([
            ft.Icon("history_edu", color="white"),
            ft.Text("查看成长档案 (历史记录)", color="white", weight="bold")
        ], alignment=ft.MainAxisAlignment.CENTER),
        width=320, height=50, bgcolor="orange", border_radius=25,
        on_click=go_to_history,
        shadow=ft.BoxShadow(blur_radius=10, color="#1A000000", offset=ft.Offset(0, 5))
    )

    view_home = ft.Column(
        controls=[
            ft.Container(height=20),
            ft.Text("🚀 7维思维特训", size=30, weight="bold"),
            ft.Container(height=30),
            loading_ring_home,
            ft.Row([
                create_mode_card("AI 深度生活", "emoji_nature", "green", "life"),
                create_mode_card("AI 模拟热搜", "whatshot", "red", "news"),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=20),
            ft.Row([
                create_mode_card("自定义输入", "edit_note", "blue", "custom"),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=30),
            btn_history
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, visible=True
    )

    results_container = ft.Column()

    def render_result_page(data):
        results_container.controls.clear()
        total_score = data.get("total_score", 0)
        results_container.controls.append(
            ft.Row([ft.Text("综合思维评分", size=24, weight="bold"),
                    ft.Text(f"{total_score}分", size=30, weight="bold", color="blue")],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )
        results_container.controls.append(ft.Divider())

        details = data.get("details", [])
        if not details:
            results_container.controls.append(ft.Text("无数据", color="red"))
            return

        for item in details:
            score = item.get('score', 0)
            color = "green" if score >= 80 else "orange"
            if score < 60: color = "red"
            tile = ft.ExpansionTile(
                title=ft.Text(item.get('name', '未知'), weight="bold"),
                trailing=ft.Text(f"{score}分", color=color, weight="bold"),
                controls=[ft.Container(content=ft.Column([
                    ft.Text(f"❌ 扣分：{item.get('reason', '')}", size=14, color="red"),
                    ft.Container(height=5),
                    ft.Text(f"💡 建议：{item.get('advice', '')}", color="blue", size=14, weight="bold")
                ]), padding=15, bgcolor="#FAFAFA")]
            )
            results_container.controls.append(tile)

    view_result = ft.Column(
        controls=[
            ft.Text("📊 本次训练报告", size=24, weight="bold"),
            ft.Text("(已自动保存至历史档案)", size=12, color="grey"),
            ft.Container(height=20),
            ft.Container(content=results_container, padding=20, bgcolor="white", border_radius=10),
            ft.Container(height=20),
            ft.ElevatedButton("再练一次", on_click=lambda e: reset_app())
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, visible=False
    )

    def reset_app():
        view_home.visible = True
        view_exam.visible = False
        view_result.visible = False
        view_history.visible = False
        page.floating_action_button = None
        page.update()

    page.add(ft.Container(content=ft.Column([view_home, view_exam, view_result, view_history]), 
                          padding=20, width=400,
                          alignment=ft.Alignment(0, -1)))

ft.app(target=main)
