import flet as ft
import json
import time
from datetime import datetime
from openai import OpenAI

# --- 1. 定义 7 大思维追问 (AI 训练的核心) ---
SKILL_QUESTIONS = [
    ("批判性思维", "这件事里的信息真实吗？有逻辑漏洞吗？是事实还是观点？"),
    ("复盘反思", "如果让你重新处理这件事，你会在哪个环节做得不一样？"),
    ("发散性思维", "除了目前的做法，还有哪些看似荒谬但可行的方案？"),
    ("结构化思维", "请把这件事拆解成 3 个关键步骤或要素 (1, 2, 3)。"),
    ("共情能力", "事件中的核心人物当时是什么情绪？他的痛点是什么？"),
    ("系统性思维", "这件事发生后，会引发什么样的连锁反应（蝴蝶效应）？"),
    ("第一性原理", "抛开表象，这件事最本质的核心目标（底层的 1）是什么？")
]

def main(page: ft.Page):
    # --- 2. 页面全局配置 (解决白屏/适配问题) ---
    page.title = "7维思维特训 AI版"
    page.theme_mode = ft.ThemeMode.LIGHT 
    page.bgcolor = "#F8FAFC"
    page.scroll = ft.ScrollMode.AUTO
    page.theme = ft.Theme(use_material3=False) # 强制关闭M3以防视觉冲突

    # --- 3. OpenAI 客户端配置 ---
    client = OpenAI(
        api_key="sk-de7d9953388c40b08eee22f642e4b0a8",
        base_url="https://api.deepseek.com"
    )

    # --- 4. 状态与数据变量 ---
    current_case_content = ""
    status_text = ft.Text("系统就绪", color="#64748B", size=12)

    # ==========================================
    # 📡 AI 核心逻辑区
    # ==========================================

    def get_ai_topic(e):
        """让 AI 编造一个深度生活故事"""
        nonlocal current_case_content
        status_text.value = "⏳ AI 正在为您构思剧本..."
        status_msg_bar.bgcolor = "#E0F2FE"
        page.update()
        
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": "请写一个300字左右、关于职场或家庭困境的冲突故事，不要给结局。"}]
            )
            current_case_content = response.choices[0].message.content
            case_display.value = current_case_content
            status_text.value = "✅ 故事生成成功，请开始作答"
            status_msg_bar.bgcolor = "#DCFCE7"
        except Exception as err:
            status_text.value = f"❌ 联网失败: {str(err)}"
            status_msg_bar.bgcolor = "#FEE2E2"
        page.update()

    def submit_for_ai_score(e):
        """把 7 个回答发给 AI 进行打分"""
        full_answer = ""
        for item in answer_fields:
            full_answer += f"【{item['skill']}】: {item['field'].value}\n"
        
        status_text.value = "🤖 AI 正在深度阅卷评分..."
        status_msg_bar.bgcolor = "#FEF9C3"
        submit_btn.disabled = True
        page.update()

        try:
            # AI 评分 Prompt
            prompt = f"针对案例：{current_case_content}\n用户的回答如下：\n{full_answer}\n请作为导师给出总分和各维度点评。请用JSON返回，格式：{{'total_score': 分数, 'advice': '总建议'}}"
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            score_display.value = f"AI 综合评分：{result['total_score']} 分"
            advice_display.value = f"导师建议：{result['advice']}"
            result_panel.visible = True
            status_text.value = "✅ 评分完成！"
        except Exception as err:
            status_text.value = f"❌ 评分出错: {str(err)}"
        
        submit_btn.disabled = False
        page.update()

    # ==========================================
    # 🎨 界面组件区
    # ==========================================
    
    # 顶部的状态条
    status_msg_bar = ft.Container(content=status_text, padding=10, border_radius=5, bgcolor="#F1F5F9")
    
    # 案例展示区域
    case_display = ft.Text("点击下方按钮换一题...", size=16, color="#1E293B")
    
    # 7个问题的输入框
    answer_fields = []
    question_controls = []
    for skill, q_text in SKILL_QUESTIONS:
        field = ft.TextField(hint_text="你的思考...", multiline=True, min_lines=2, bgcolor="white", text_size=14)
        answer_fields.append({"skill": skill, "field": field})
        question_controls.append(ft.Text(f"❓ {skill}: {q_text}", size=14, weight="bold"))
        question_controls.append(field)
        question_controls.append(ft.Container(height=10))

    # 结果显示面板
    score_display = ft.Text("", size=24, weight="bold", color="blue")
    advice_display = ft.Text("", size=14, color="#334155")
    result_panel = ft.Container(
        content=ft.Column([score_display, advice_display]),
        padding=20, bgcolor="#F0F9FF", border_radius=10, visible=False
    )

    submit_btn = ft.ElevatedButton("提交 AI 阅卷", on_click=submit_for_ai_score, bgcolor="blue", color="white")

    # ==========================================
    # 📦 页面组装
    # ==========================================
    page.add(
        ft.SafeArea(
            ft.Column([
                ft.Text("🚀 7维思维特训 Pro", size=28, weight="bold", color="#0F172A"),
                status_msg_bar,
                ft.Container(height=10),
                
                # 换题区
                ft.Container(
                    content=ft.Column([
                        case_display,
                        ft.ElevatedButton("换一题 (AI生成)", icon="refresh", on_click=get_ai_topic)
                    ]),
                    padding=20, bgcolor="white", border_radius=15, border=ft.border.all(1, "#E2E8F0")
                ),
                
                ft.Divider(height=40),
                
                # 答题区
                ft.Text("📝 请输入你的深度分析：", size=18, weight="bold"),
                ft.Column(question_controls),
                
                ft.Container(height=20),
                submit_btn,
                
                ft.Container(height=20),
                result_panel,
                ft.Container(height=50) # 底部留白
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
    )

ft.app(target=main)
