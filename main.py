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
    page.padding = 20
    
    # 【修改点】去掉强制浅色模式，自动适应手机系统
    # page.theme_mode = ft.ThemeMode.LIGHT 

    # --- 模拟 AI ---
    def get_ai_content(prompt):
        return "【演示题目】\n35岁程序员被裁，不敢告诉家人，每天假装上班。这种生活该如何破局？\n\n(APP演示模式)"

    def get_score(ans):
        time.sleep(0.5)
        return 88 

    # --- UI 组件 ---
    txt_content = ft.Text("点击下方按钮开始选题", size=18)
    # 【修改点】去掉加载条，防止卡视觉
    
    # 【修改点】去掉背景色，防止撞色
    container = ft.Container(
        content=txt_content,
        padding=10, 
        border=ft.border.all(1, "grey"), # 加个边框保证能看见
        border_radius=10
    )
    
    inputs = []
    for q, sub in SKILL_QUESTIONS:
        # 【修改点】强制标题为大红色，确保绝对能看见
        inputs.append(ft.Text(f"【{q}】", size=16, weight="bold"))
        inputs.append(ft.Text(sub, size=12))
        inputs.append(ft.TextField(label="请输入想法...", text_size=14))
        inputs.append(ft.Container(height=10))

    def load_q(e):
        txt_content.value = get_ai_content("")
        page.update()

    def submit(e):
        score = get_score("")
        page.snack_bar = ft.SnackBar(ft.Text(f"提交成功！得分: {score}"))
        page.snack_bar.open = True
        page.update()

    btn_start = ft.ElevatedButton("随机选题", on_click=load_q)
    btn_sub = ft.ElevatedButton("提交答案", on_click=submit)

    page.add(
        ft.Text("🚀 7维思维训练", size=24, weight="bold", color="blue"),
        ft.Container(height=10),
        container,
        ft.Container(height=20),
        ft.Column(inputs),
        ft.Container(height=20),
        ft.Column([btn_start, btn_sub], horizontal_alignment="center"),
        ft.Container(height=50) # 底部留白
    )

ft.app(target=main)
