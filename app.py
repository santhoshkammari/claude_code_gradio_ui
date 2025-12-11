"""
"""
import gradio as gr
import json
import asyncio
import threading
from datetime import datetime
from pathlib import Path
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock

tasks_file = Path("tasks.json")
client = None
loop = None

def init_event_loop():
    global loop
    if loop is None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        threading.Thread(target=loop.run_forever, daemon=True).start()

async def init_claude():
    global client
    if not client:
        client = ClaudeSDKClient(ClaudeAgentOptions(
            allowed_tools=["Read", "Write", "Bash", "Grep"],
            permission_mode="acceptEdits"
        ))
        await client.connect()

async def chat_claude(msg, history):
    await init_claude()
    await client.query(msg)
    response = ""
    async for m in client.receive_response():
        if isinstance(m, AssistantMessage):
            for b in m.content:
                if isinstance(b, TextBlock):
                    response += b.text
    history = history or []
    history.append({"role": "user", "content": msg})
    history.append({"role": "assistant", "content": response})
    return history

def chat_sync(msg, history):
    init_event_loop()
    future = asyncio.run_coroutine_threadsafe(chat_claude(msg, history), loop)
    return future.result()

def load_tasks():
    if tasks_file.exists():
        return json.loads(tasks_file.read_text())
    return {"active": [], "done": [], "jams": []}

def save_tasks(tasks):
    tasks_file.write_text(json.dumps(tasks, indent=2))

def get_task_card(task, category, idx):
    task_id = task.get("id", "TASK-001")
    time = task.get("time", "Just now")
    description = task.get("description", "")

    card_html = f"""
    <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; margin-bottom: 12px;" id="{task_id}">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span style="font-size: 13px; color: #6b7280;">📋 {task_id}</span>
            <span style="font-size: 12px; color: #9ca3af;">{time}</span>
        </div>
        <div style="font-size: 15px; font-weight: 600; color: #111827; margin-bottom: 6px;">{task['title']}</div>
        {f'<div style="font-size: 13px; color: #6b7280; line-height: 1.5; margin-bottom: 12px;">{description}</div>' if description else ''}
        <div style="display: flex; gap: 8px;">
            <button onclick="navigator.clipboard.writeText('delete:{task_id}')"
                style="background: #ef4444; color: white; border: none; padding: 6px 16px; border-radius: 6px; font-size: 13px; cursor: pointer;">Delete</button>
            <button onclick="navigator.clipboard.writeText('start:{task_id}')"
                style="background: #3b82f6; color: white; border: none; padding: 6px 16px; border-radius: 6px; font-size: 13px; cursor: pointer;">Start →</button>
        </div>
    </div>
    """
    return card_html

def delete_task(task_id, category):
    tasks = load_tasks()
    tasks[category] = [t for t in tasks.get(category, []) if t.get("id") != task_id]
    save_tasks(tasks)
    return render_backlog(category), render_needs_review(category)

def start_task(task_id, category):
    tasks = load_tasks()
    for t in tasks.get(category, []):
        if t.get("id") == task_id:
            t["status"] = "in_progress"
            t["section"] = "needs_review"
    save_tasks(tasks)
    return render_backlog(category), render_needs_review(category)

def render_backlog(category):
    tasks = load_tasks()
    task_list = tasks.get(category, [])
    backlog = [t for t in task_list if t.get("section") == "backlog"]

    html = f"""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
        <div style="width: 20px; height: 20px; border: 2px solid #6b7280; border-radius: 50%;"></div>
        <h3 style="margin: 0; font-size: 16px; font-weight: 600; color: #111827;">Backlog</h3>
        <span style="background: #f3f4f6; color: #6b7280; padding: 2px 8px; border-radius: 12px; font-size: 13px; font-weight: 500;">{len(backlog)}</span>
    </div>
    """

    if backlog:
        for idx, task in enumerate(backlog):
            html += get_task_card(task, category, idx)
    else:
        html += '<div style="text-align: center; padding: 40px; color: #9ca3af; font-size: 14px;">No backlog tasks</div>'

    return html

def render_needs_review(category):
    tasks = load_tasks()
    task_list = tasks.get(category, [])
    needs_review = [t for t in task_list if t.get("section") == "needs_review"]

    html = f"""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
        <div style="width: 20px; height: 20px; background: #10b981; border-radius: 50%;"></div>
        <h3 style="margin: 0; font-size: 16px; font-weight: 600; color: #111827;">Needs review</h3>
        <span style="background: #f3f4f6; color: #6b7280; padding: 2px 8px; border-radius: 12px; font-size: 13px; font-weight: 500;">{len(needs_review)}</span>
    </div>
    """

    if needs_review:
        for idx, task in enumerate(needs_review):
            html += get_task_card(task, category, idx)
    else:
        html += '<div style="text-align: center; padding: 40px; color: #9ca3af; font-size: 14px;">No tasks in review</div>'

    return html

def add_task(title, section, category):
    if not title.strip():
        return render_backlog(category), render_needs_review(category), ""

    tasks = load_tasks()
    task_count = len(tasks.get(category, []))
    new_task = {
        "id": f"TASK-{task_count + 1:03d}",
        "title": title,
        "section": section,
        "description": "",
        "status": "open",
        "time": datetime.now().strftime("%I:%M %p"),
        "created": datetime.now().isoformat()
    }

    tasks[category].append(new_task)
    save_tasks(tasks)

    return render_backlog(category), render_needs_review(category), ""

with gr.Blocks() as demo:


    with gr.Sidebar(position='right', open=True,width="27%"):
        gr.Markdown("### Claude Agent")
        chatbot = gr.Chatbot(height=400, show_label=False, type='messages', allow_tags=False)
        chat_input = gr.Textbox(
            placeholder="Message Claude...",
            show_label=False,
            container=False
        )
        chat_input.submit(chat_sync, [chat_input, chatbot], [chatbot]).then(lambda: "", None, chat_input)

    with gr.Sidebar(open=True, position='left',width="19%"):
        gr.Markdown("### Navigation")

    with gr.Tabs():
        with gr.Tab("Active"):
            gr.Markdown("### Coming soon...")

        with gr.Tab("Done"):
            with gr.Row():
                with gr.Column(scale=1):
                    done_backlog = gr.HTML(render_backlog("done"))
                with gr.Column(scale=1):
                    done_review = gr.HTML(render_needs_review("done"))

            with gr.Row():
                done_input = gr.Textbox(
                    placeholder="Add a completed task...",
                    show_label=False,
                    scale=3,
                    container=False
                )
                done_section = gr.Dropdown(
                    choices=["backlog", "needs_review"],
                    value="backlog",
                    show_label=False,
                    scale=1,
                    container=False
                )
                done_btn = gr.Button("+ Task", variant="primary", scale=1)

            done_btn.click(
                fn=lambda x, s: add_task(x, s, "done"),
                inputs=[done_input, done_section],
                outputs=[done_backlog, done_review, done_input]
            )
            done_input.submit(
                fn=lambda x, s: add_task(x, s, "done"),
                inputs=[done_input, done_section],
                outputs=[done_backlog, done_review, done_input]
            )

        with gr.Tab("Jams"):
            with gr.Row():
                with gr.Column(scale=1):
                    jams_backlog = gr.HTML(render_backlog("jams"))
                with gr.Column(scale=1):
                    jams_review = gr.HTML(render_needs_review("jams"))

            with gr.Row():
                jams_input = gr.Textbox(
                    placeholder="Add a jam...",
                    show_label=False,
                    scale=3,
                    container=False
                )
                jams_section = gr.Dropdown(
                    choices=["backlog", "needs_review"],
                    value="backlog",
                    show_label=False,
                    scale=1,
                    container=False
                )
                jams_btn = gr.Button("+ Task", variant="primary", scale=1)

            jams_btn.click(
                fn=lambda x, s: add_task(x, s, "jams"),
                inputs=[jams_input, jams_section],
                outputs=[jams_backlog, jams_review, jams_input]
            )
            jams_input.submit(
                fn=lambda x, s: add_task(x, s, "jams"),
                inputs=[jams_input, jams_section],
                outputs=[jams_backlog, jams_review, jams_input]
            )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
