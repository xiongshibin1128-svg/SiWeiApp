import flet as ft
from openai import OpenAI
import json
import time

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
    # --- 2. 现代页面配置：解决视觉冲突 ---
    page.title = "7维思维特训 AI版"
    page.theme_mode = ft.ThemeMode.LIGHT 
    page.bgcolor = ft.Colors.WHITE # 强制纯白
    page.scroll = ft.ScrollMode.AUTO
    
    # OpenAI 客户端配置 (DeepSeek)
    client = OpenAI(
        api_key="sk-de7d9953388c40b08eee22f642e4b0a8",
        base_url="https://api.deepseek.com"
    )

    # 全局变量存储当前题目
    current_case_content = ""
    
    # 状态提示区域
    status_log = ft.Text("系统就绪", color=ft.Colors.GREY_700, size=12)

    # --- 3. AI 逻辑区 ---

    def get_ai_topic(e):
        """让 AI 编造一个深度生活故事"""
        nonlocal current_case_content
        btn_generate.disabled = True
        status_log.value = "⏳ AI 正在为您构思剧本..."
        status_log.color = ft.Colors.BLUE
        page.update()
        
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": "请写一个300字左右、关于职场或家庭困境的冲突故事，不要给结局。"}]
            )
            current_case_content = response.choices[0].message.content
            case_display.value = current_case_content
            status_log.value = "✅ 故事生成成功，请在下方作答"
            status_log.color = ft.Colors.GREEN
        except Exception as err:
            status_log.value = f"❌ 联网失败: {str(err)}"
            status_log.color = ft.Colors.RED
        
        btn_generate.disabled = False
        page.update()

    def submit_for_ai_score(e):
        """把用户的 7 个回答发给 AI 进行打分"""
        if not current_case_content:
            status_log.value = "⚠️ 请先获取案例再提交"
            page.update()
            return

        full_answer = ""
        for item in answer_fields:
            full_answer += f"【{item['skill']}】: {item['field'].value}\n"
        
        btn_submit.disabled = True
        status_log.value = "🤖 AI 导师正在深度阅卷评分..."
        status_log.color = ft.Colors.ORANGE
        page.update()

        try:
            # AI 评分 Prompt：强迫返回 JSON
            prompt = f"针对案例：{current_case_content}\n用户的 7 维度回答如下：\n{full_answer}\n请作为导师给出 0-100 的总分和一段深度建议。务必严格用 JSON 格式返回，例如：{{'score': 85, 'advice': '建议...'}}"
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            score_text.value = f"AI 综合评分：{result.get('score', 0)} 分"
            advice_text.value = f"导师点评：{result.get('advice', '')}"
            result_container.visible = True
            status_log.value = "✅ 评分已出，请查阅！"
            status_log.color = ft.Colors.GREEN
        except Exception as err:
            status_log.value = f"❌ 评分出错: {str(err)}"
            status_log.color = ft.Colors.RED
        
        btn_submit.disabled = False
        page.update()

    # --- 4. UI 组件区 ---
    
    case_display = ft.Text("点击下方按钮开启特训...", size=16, color=ft.Colors.BLACK, line_height=1.5)
    
    # 循环生成 7 个输入框
    answer_fields = []
    question_controls = []
    for skill, q_text in SKILL_QUESTIONS:
        field = ft.TextField(
            label=f"你的【{skill}】分析",
            hint_text=q_text,
            multiline=True, min_lines=2,
            bgcolor=ft.Colors.GREY_50,
            border_color=ft.Colors.GREY_300,
            text_size=14, color=ft.Colors.BLACK
        )
        answer_fields.append({"skill": skill, "field": field})
        question_controls.append(field)
        question_controls.append(ft.Container(height=10))

    score_text = ft.Text("", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE)
    advice_text = ft.Text("", size=14, color=ft.Colors.GREY_800)
    result_container = ft.Container(
        content=ft.Column([score_text, advice_text]),
        padding=20, bgcolor=ft.Colors.BLUE_50, border_radius=10, visible=False
    )

    btn_generate = ft.ElevatedButton("换一题 (AI生成)", icon="refresh", on_click=get_ai_topic, style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE))
    btn_submit = ft.ElevatedButton("提交所有回答，让 AI 评分", on_click=submit_for_ai_score, width=300, height=50, style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE))

    # --- 5. 组装页面 ---
    page.add(
        ft.SafeArea( # 自动避开手机挖孔/刘海
            ft.Column([
                ft.Text("🚀 7维思维特训 Pro", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                status_log,
                ft.Divider(height=30, color=ft.Colors.GREY_200),
                
                # 题目区
                ft.Container(
                    content=ft.Column([case_display, btn_generate]),
                    padding=20, bgcolor=ft.Colors.GREY_100, border_radius=15, border=ft.border.all(1, ft.Colors.GREY_300)
                ),
                
                ft.Container(height=20),
                ft.Text("📝 请输入你的分析：", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                
                # 答题区
                ft.Column(question_controls),
                
                ft.Container(height=20),
                btn_submit,
                
                ft.Container(height=20),
                result_container,
                ft.Container(height=50) # 底部留白，防止被遮挡
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
    )

ft.app(target=main)
