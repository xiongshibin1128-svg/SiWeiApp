import flet as ft
import time

# --- 题目配置 ---
SKILL_QUESTIONS = [
    ("批判性思维", "信息真实吗？有逻辑漏洞吗？"),
    ("复盘反思", "重来一次你会怎么做？"),
    ("发散性思维", "还有哪些看似荒谬但可行的方案？"),
    ("结构化思维", "请拆解成 3 个关键步骤 (1, 2, 3)。"),
    ("共情能力", "对方当时是什么情绪？痛点在哪？"),
    ("系统性思维", "这会引发什么连锁反应？"),
    ("第一性原理", "这件事最本质的目标是什么？")
]

def main(page: ft.Page):
    page.title = "思维训练"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 10 

    # --- 模拟 AI ---
    def get_ai_content(prompt):
        time.sleep(1) 
        return "【演示题目】\n35岁程序员被裁，不敢告诉家人，每天假装上班。这种生活该如何破局？\n\n(APP演示模式)"

    def get_score(ans):
        time.sleep(1)
        return 88 

    # --- UI 组件 ---
    txt_content = ft.Text("点击下方按钮开始选题", size=16)
    loading = ft.ProgressBar(visible=False)
    
    container = ft.Container(
        content=ft.Column([txt_content, loading]), 
        padding=15, 
        bgcolor=ft.colors.BLUE_50, 
        border_radius=10
    )
    
    inputs = []
    for q, sub in SKILL_QUESTIONS:
        inputs.append(ft.Text(f"【{q}】", weight="bold", size=16))
        inputs.append(ft.Text(sub, size=12, color="grey"))
        inputs.append(ft.TextField(border_color="blue", text_size=14))
        inputs.append(ft.Container(height=10))

    def load_q(e):
        txt_content.visible = False
        loading.visible = True
        page.update()
        txt_content.value = get_ai_content("")
        loading.visible = False
        txt_content.visible = True
        page.update()

    def submit(e):
        btn_sub.text = "评分中..."
        btn_sub.disabled = True
        page.update()
        score = get_score("")
        page.snack_bar = ft.SnackBar(ft.Text(f"提交成功！得分: {score}"))
        page.snack_bar.open = True
        btn_sub.text = "提交答案"
        btn_sub.disabled = False
        page.update()

    btn_start = ft.ElevatedButton("随机选题", on_click=load_q, bgcolor="blue", color="white", width=300)
    btn_sub = ft.ElevatedButton("提交答案", on_click=submit, bgcolor="green", color="white", width=300, height=50)

    page.add(
        ft.Text("🚀 7维思维训练", size=24, weight="bold"),
        container,
        ft.Container(height=20),
        ft.Column(inputs),
        ft.Container(height=10),
        ft.Column([btn_start, btn_sub], horizontal_alignment="center")
    )

ft.app(target=main)
