import asyncio
import json
import os
import random
import flet as ft

# مسار ملف حفظ البيانات محلياً
DATA_FILE = "habits_data.json"


# وظائف قراءة وحفظ البيانات
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # إضافة القائمة الجديدة مع أكثر من 10 عادات متنوعة
    return {
        "habits": [
            "قراءة صفحتين من القرآن الكريم 📖",
            "الاستماع لبودكاست/محتوى بالإنجليزية 🎧",
            "تعلم 5 مفردات جديدة بالإنجليزية 🗂️",
            "ممارسة تمارين تمدد (Stretching) 🧘",
            "قراءة فصل من كتاب نافع 📚",
            "ترتيب المكان وتنظيف المكتب 🧹",
            "كتابة وتدوين أفكار أو يوميات ✍️",
            # --- العادات الجديدة المضافة ---
            "حل مسألة برمجية أو خوارزمية بسيطة 💻",
            "شرب كوب كبير من الماء عند الاستيقاظ 💧",
            "القيام بـ 20 تمرين ضغط أو قرفصاء 🏋️‍♂️",
            "مراجعة الملاحظات والدروس اليومية 📝",
            "مشاهدة فيديو تعليمي قصير في مجالك 🎥",
            "التنفس العميق والملازمة لمدة 5 دقائق 🧘‍♂️",
            "المشي في الهواء الطلق لمدة 15 دقيقة 🚶‍♂️",
            "تنظيم قائمة المهام لليوم القادم 📋",
            "الابتعاد عن الشاشات قبل النوم بـ 30 دقيقة 📵",
            "الامتنان والتفكير في 3 أشياء إيجابية حدثت اليوم 🌟",
            "تنظيف وإغلاق جميع تبويبات المتصفح غير الضرورية 💻",
            "تعلم مفهوم جديد في البرمجة أو التطوير 🧠",
        ],
        "completed_sessions": 0,
    }


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# دالة مساعدة لإنشاء الأزرار بأمان تام
def make_button(btn_type, label, on_click=None):
    text_obj = ft.Text(label, weight=ft.FontWeight.BOLD)
    if btn_type == "elevated":
        btn = ft.ElevatedButton(content=text_obj)
    elif btn_type == "outlined":
        btn = ft.OutlinedButton(content=text_obj)
    else:
        btn = ft.ElevatedButton(content=text_obj)

    if on_click:
        btn.on_click = on_click
    return btn, text_obj


async def main(page: ft.Page):
    page.title = "مُطوّر العادات والتركيز 🎯"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.rtl = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    # تحميل البيانات
    user_data = load_data()
    habits = user_data.get("habits", [])
    completed_sessions = user_data.get("completed_sessions", 0)

    # حالة المؤقت
    timer_running = [False]
    selected_minutes = [30]
    seconds_left = [30 * 60]

    # --- العناصر البصرية ---
    habit_text = ft.Text(
        value="اضغط على الزر لاختيار عادة!",
        size=18,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
    )

    loading_ring = ft.ProgressRing(width=28, height=28, visible=False)

    timer_text = ft.Text(
        value="30:00",
        size=48,
        weight=ft.FontWeight.BOLD,
    )

    stats_text = ft.Text(
        value=f"🔥 الجلسات المكتملة: {completed_sessions}",
        size=15,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
    )

    new_habit_input = ft.TextField(
        label="أضف عادة جديدة",
        hint_text="مثال: كتابة كود لمدة 20 دقيقة",
        expand=True,
    )

    def sync_and_save():
        save_data(
            {"habits": habits, "completed_sessions": completed_sessions}
        )

    def update_timer_ui():
        mins = seconds_left[0] // 60
        secs = seconds_left[0] % 60
        timer_text.value = f"{mins:02d}:{secs:02d}"
        page.update()

    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
        page.update()

    theme_btn, _ = make_button("outlined", "🌙 / ☀️", on_click=toggle_theme)

    def change_duration(e):
        selected_minutes[0] = int(e.control.value)
        if not timer_running[0]:
            seconds_left[0] = selected_minutes[0] * 60
            update_timer_ui()

    time_dropdown = ft.Dropdown(
        width=130,
        value="30",
        options=[
            ft.dropdown.Option("15", "15 دقيقة"),
            ft.dropdown.Option("30", "30 دقيقة"),
            ft.dropdown.Option("45", "45 دقيقة"),
        ],
    )
    time_dropdown.on_change = change_duration

    # أزرار المؤقت
    btn_start_timer, btn_start_label = make_button("elevated", "▶️ بدء")
    btn_reset_timer, _ = make_button("outlined", "🔄 إعادة ضبط")

    async def run_timer_loop():
        nonlocal completed_sessions
        while timer_running[0] and seconds_left[0] > 0:
            await asyncio.sleep(1)
            if not timer_running[0]:
                break
            seconds_left[0] -= 1
            update_timer_ui()

        if seconds_left[0] == 0 and timer_running[0]:
            timer_running[0] = False
            completed_sessions += 1
            sync_and_save()
            stats_text.value = f"🔥 الجلسات المكتملة: {completed_sessions}"
            btn_start_label.value = "▶️ بدء"
            page.update()

            page.open(
                ft.AlertDialog(
                    title=ft.Text("إنجاز رائع! 🎉"),
                    content=ft.Text(
                        f"أنهيت جلسة الـ {selected_minutes[0]} دقيقة بنجاح!"
                    ),
                )
            )

    async def start_timer_click(e):
        if timer_running[0]:
            timer_running[0] = False
            btn_start_label.value = "▶️ استئناف"
            page.update()
        else:
            timer_running[0] = True
            btn_start_label.value = "⏸️ إيقاف"
            page.update()
            asyncio.create_task(run_timer_loop())

    def reset_timer_click(e):
        timer_running[0] = False
        seconds_left[0] = selected_minutes[0] * 60
        btn_start_label.value = "▶️ بدء"
        update_timer_ui()

    btn_start_timer.on_click = start_timer_click
    btn_reset_timer.on_click = reset_timer_click

    # زر السحب العشوائي
    btn_spin, _ = make_button("elevated", "🌀 اختار لي عادة الآن!")

    async def spin_click(e):
        if not habits:
            habit_text.value = "القائمة فارغة! أضف عادات أولاً."
            page.update()
            return

        timer_running[0] = False
        btn_start_label.value = "▶️ بدء"
        seconds_left[0] = selected_minutes[0] * 60
        update_timer_ui()

        loading_ring.visible = True
        habit_text.value = "جاري السحب العشوائي..."
        page.update()

        await asyncio.sleep(0.4)

        selected = random.choice(habits)
        habit_text.value = f"عادتك القادمة هي:\n{selected}"
        loading_ring.visible = False
        page.update()

    btn_spin.on_click = spin_click

    # إضافة وإدارة العادات
    def add_habit_click(e):
        val = new_habit_input.value.strip()
        if val:
            habits.append(val)
            sync_and_save()
            new_habit_input.value = ""
            render_habits_list()
            page.open(
                ft.SnackBar(
                    content=ft.Text("تمت إضافة العادة وحفظها!"), open=True
                )
            )

    btn_add_habit, _ = make_button(
        "elevated", "إضافة", on_click=add_habit_click
    )

    def delete_habit(habit_item):
        if habit_item in habits:
            habits.remove(habit_item)
            sync_and_save()
            render_habits_list()

    habits_list_column = ft.Column()

    def render_habits_list():
        habits_list_column.controls.clear()
        for h in habits:
            btn_del, _ = make_button(
                "outlined", "❌", on_click=lambda e, item=h: delete_habit(item)
            )
            habits_list_column.controls.append(
                ft.Container(
                    content=ft.ListTile(
                        title=ft.Text(h, size=15),
                        trailing=btn_del,
                    ),
                    padding=5,
                    margin=5,
                )
            )
        page.update()

    # التخطيط النهائي
    page.add(
        ft.AppBar(
            title=ft.Text("مُطوّر العادات والتركيز 🎯"),
            center_title=True,
            actions=[theme_btn],
        ),
        ft.Container(
            content=stats_text,
            padding=10,
        ),
        ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        habit_text,
                        loading_ring,
                        ft.Divider(),
                        btn_spin,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
            ),
        ),
        ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    "مدة الجلسة:", weight=ft.FontWeight.BOLD
                                ),
                                time_dropdown,
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        timer_text,
                        ft.Row(
                            [btn_start_timer, btn_reset_timer],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
            ),
        ),
        ft.Divider(),
        ft.Text("📝 قائمة عاداتك الشخصية", size=16, weight=ft.FontWeight.BOLD),
        ft.Row(
            [
                new_habit_input,
                btn_add_habit,
            ]
        ),
        habits_list_column,
    )

    render_habits_list()


ft.app(target=main)