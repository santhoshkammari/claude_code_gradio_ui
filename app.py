import gradio as gr
import json
from datetime import datetime
from pathlib import Path

tasks_file = Path("tasks.json")

def load_tasks():
    if tasks_file.exists():
        return json.loads(tasks_file.read_text())
    return {"active": [], "done": [], "jams": []}

def save_tasks(tasks):
    tasks_file.write_text(json.dumps(tasks, indent=2))

def get_task_card(task, category):
    replies = task.get("replies", 0)
    time = task.get("time", "Just now")

    card_html = f"""
    <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; margin-bottom: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
        <div style="display: flex; align-items: start; gap: 12px;">
            <div style="width: 32px; height: 32px; background: #3b82f6; border-radius: 6px; flex-shrink: 0;"></div>
            <div style="flex: 1;">
                <div style="font-size: 14px; font-weight: 600; color: #111827; margin-bottom: 4px;">{task['title']}</div>
                <div style="display: flex; align-items: center; gap: 8px; font-size: 12px; color: #6b7280;">
                    <span>👤 {replies} replies</span>
                    <span>•</span>
                    <span>{time}</span>
                </div>
            </div>
        </div>
    </div>
    """
    return card_html

def render_tasks(category):
    tasks = load_tasks()
    task_list = tasks.get(category, [])

    if not task_list:
        return f"""
        <div style="text-align: center; padding: 60px 20px; color: #9ca3af;">
            <div style="font-size: 48px; margin-bottom: 16px;">📋</div>
            <div style="font-size: 16px; font-weight: 500; margin-bottom: 8px;">No {category} tasks</div>
            <div style="font-size: 14px;">Create a task to get started!</div>
        </div>
        """

    html = ""
    for task in task_list:
        html += get_task_card(task, category)

    return html

def add_task(title, category):
    if not title.strip():
        return render_tasks(category), ""

    tasks = load_tasks()
    new_task = {
        "title": title,
        "replies": 0,
        "time": datetime.now().strftime("%I:%M %p"),
        "created": datetime.now().isoformat()
    }

    tasks[category].append(new_task)
    save_tasks(tasks)

    return render_tasks(category), ""

with gr.Blocks() as demo:

    gr.HTML("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="font-size: 28px; font-weight: 700; color: #111827; margin-bottom: 8px;">📝 Scratchpad</h1>
        <p style="color: #6b7280; font-size: 14px;">Manage your tasks efficiently</p>
    </div>
    """)

    with gr.Tabs():
        with gr.Tab("Active"):
            with gr.Column():
                active_tasks = gr.HTML(render_tasks("active"))

                with gr.Row():
                    active_input = gr.Textbox(
                        placeholder="Add a new task...",
                        show_label=False,
                        scale=4,
                        container=False
                    )
                    active_btn = gr.Button("+ Task", variant="primary", scale=1)

                active_btn.click(
                    fn=lambda x: add_task(x, "active"),
                    inputs=[active_input],
                    outputs=[active_tasks, active_input]
                )
                active_input.submit(
                    fn=lambda x: add_task(x, "active"),
                    inputs=[active_input],
                    outputs=[active_tasks, active_input]
                )

        with gr.Tab("Done"):
            with gr.Column():
                done_tasks = gr.HTML(render_tasks("done"))

                with gr.Row():
                    done_input = gr.Textbox(
                        placeholder="Add a completed task...",
                        show_label=False,
                        scale=4,
                        container=False
                    )
                    done_btn = gr.Button("+ Task", variant="primary", scale=1)

                done_btn.click(
                    fn=lambda x: add_task(x, "done"),
                    inputs=[done_input],
                    outputs=[done_tasks, done_input]
                )
                done_input.submit(
                    fn=lambda x: add_task(x, "done"),
                    inputs=[done_input],
                    outputs=[done_tasks, done_input]
                )

        with gr.Tab("Jams"):
            with gr.Column():
                jams_tasks = gr.HTML(render_tasks("jams"))

                with gr.Row():
                    jams_input = gr.Textbox(
                        placeholder="Add a jam...",
                        show_label=False,
                        scale=4,
                        container=False
                    )
                    jams_btn = gr.Button("+ Task", variant="primary", scale=1)

                jams_btn.click(
                    fn=lambda x: add_task(x, "jams"),
                    inputs=[jams_input],
                    outputs=[jams_tasks, jams_input]
                )
                jams_input.submit(
                    fn=lambda x: add_task(x, "jams"),
                    inputs=[jams_input],
                    outputs=[jams_tasks, jams_input]
                )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
