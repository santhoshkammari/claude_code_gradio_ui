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

def delete_task(task_id, category):
    tasks = load_tasks()
    tasks[category] = [t for t in tasks.get(category, []) if t.get("id") != task_id]
    save_tasks(tasks)
    return {"refresh": datetime.now().isoformat()}

def start_task(task_id, category):
    tasks = load_tasks()
    for t in tasks.get(category, []):
        if t.get("id") == task_id:
            t["status"] = "in_progress"
            t["section"] = "needs_review"
    save_tasks(tasks)
    return {"refresh": datetime.now().isoformat()}

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
            task_id = task.get("id", "TASK-001")
            time = task.get("time", "Just now")
            description = task.get("description", "")

            html += f"""
            <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="font-size: 13px; color: #6b7280;">📋 {task_id}</span>
                    <span style="font-size: 12px; color: #9ca3af;">{time}</span>
                </div>
                <div style="font-size: 15px; font-weight: 600; color: #111827; margin-bottom: 6px;">{task['title']}</div>
                {f'<div style="font-size: 13px; color: #6b7280; line-height: 1.5; margin-bottom: 12px;">{description}</div>' if description else ''}
                <div style="display: flex; gap: 8px;">
                    <button onclick="
                        const input = document.querySelector('[data-testid*=\\'textbox\\'][style*=\\'display: none\\']');
                        if (input && input.querySelector('textarea')) {{
                            const textarea = input.querySelector('textarea');
                            textarea.value = 'delete:{category}:{task_id}';
                            textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        }}
                    " style="background: #ef4444; color: white; border: none; padding: 6px 16px; border-radius: 6px; font-size: 13px; cursor: pointer;">Delete</button>
                    <button onclick="
                        const input = document.querySelector('[data-testid*=\\'textbox\\'][style*=\\'display: none\\']');
                        if (input && input.querySelector('textarea')) {{
                            const textarea = input.querySelector('textarea');
                            textarea.value = 'start:{category}:{task_id}';
                            textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        }}
                    " style="background: #3b82f6; color: white; border: none; padding: 6px 16px; border-radius: 6px; font-size: 13px; cursor: pointer;">Start →</button>
                </div>
            </div>
            """
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
            task_id = task.get("id", "TASK-001")
            time = task.get("time", "Just now")
            description = task.get("description", "")

            html += f"""
            <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="font-size: 13px; color: #6b7280;">📋 {task_id}</span>
                    <span style="font-size: 12px; color: #9ca3af;">{time}</span>
                </div>
                <div style="font-size: 15px; font-weight: 600; color: #111827; margin-bottom: 6px;">{task['title']}</div>
                {f'<div style="font-size: 13px; color: #6b7280; line-height: 1.5; margin-bottom: 12px;">{description}</div>' if description else ''}
                <div style="display: flex; gap: 8px;">
                    <button onclick="
                        const input = document.querySelector('[data-testid*=\\'textbox\\'][style*=\\'display: none\\']');
                        if (input && input.querySelector('textarea')) {{
                            const textarea = input.querySelector('textarea');
                            textarea.value = 'delete:{category}:{task_id}';
                            textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        }}
                    " style="background: #ef4444; color: white; border: none; padding: 6px 16px; border-radius: 6px; font-size: 13px; cursor: pointer;">Delete</button>
                </div>
            </div>
            """
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

def handle_action(command, category):
    if not command:
        return render_backlog(category), render_needs_review(category), ""

    parts = command.split(":")
    if len(parts) == 3:
        action, cat, task_id = parts
        if action == "delete":
            return delete_task(task_id, cat) + ("",)
        elif action == "start":
            return start_task(task_id, cat) + ("",)

    return render_backlog(category), render_needs_review(category), ""

with gr.Blocks() as demo:


    with gr.Sidebar(position='right', open=True,width="27%"):
        gr.Markdown("### Claude Agent")
        chatbot = gr.Chatbot(height=400, show_label=False)
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
            active_state = gr.State({"refresh": datetime.now().isoformat()})

            @gr.render(inputs=active_state)
            def render_active(state):
                tasks = load_tasks()
                backlog = [t for t in tasks.get("active", []) if t.get("section") == "backlog"]
                needs_review = [t for t in tasks.get("active", []) if t.get("section") == "needs_review"]

                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML(f"""
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                            <div style="width: 20px; height: 20px; border: 2px solid #6b7280; border-radius: 50%;"></div>
                            <h3 style="margin: 0; font-size: 16px; font-weight: 600; color: #111827;">Backlog</h3>
                            <span style="background: #f3f4f6; color: #6b7280; padding: 2px 8px; border-radius: 12px; font-size: 13px; font-weight: 500;">{len(backlog)}</span>
                        </div>
                        """)

                        if backlog:
                            for task in backlog:
                                with gr.Group(elem_classes="task-card"):
                                    gr.HTML(f"""
                                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                                        <div style="display: flex; align-items: center; gap: 8px;">
                                            <span style="font-size: 13px; color: #6b7280; font-weight: 500;">📋 {task['id']}</span>
                                            <span style="background: #f3f4f6; color: #6b7280; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 500;">{task['time']}</span>
                                        </div>
                                    </div>
                                    <div style="font-size: 15px; font-weight: 600; color: #111827; margin-bottom: 8px; line-height: 1.4;">{task['title']}</div>
                                    """)
                                    if task.get('description'):
                                        gr.HTML(f"<div style='font-size: 13px; color: #6b7280; line-height: 1.5; margin-bottom: 14px;'>{task['description']}</div>")
                                    with gr.Row():
                                        del_btn = gr.Button("🗑️ Delete", variant="stop", size="sm", scale=1)
                                        start_btn = gr.Button("▶️ Start", variant="primary", size="sm", scale=1)

                                        del_btn.click(
                                            fn=lambda tid=task['id']: delete_task(tid, "active"),
                                            outputs=[active_state]
                                        )
                                        start_btn.click(
                                            fn=lambda tid=task['id']: start_task(tid, "active"),
                                            outputs=[active_state]
                                        )
                        else:
                            gr.HTML("<div style='text-align: center; padding: 40px; color: #9ca3af;'>No backlog tasks</div>")

                    with gr.Column(scale=1):
                        gr.HTML(f"""
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                            <div style="width: 20px; height: 20px; background: #10b981; border-radius: 50%;"></div>
                            <h3 style="margin: 0; font-size: 16px; font-weight: 600; color: #111827;">Needs review</h3>
                            <span style="background: #f3f4f6; color: #6b7280; padding: 2px 8px; border-radius: 12px; font-size: 13px; font-weight: 500;">{len(needs_review)}</span>
                        </div>
                        """)

                        if needs_review:
                            for task in needs_review:
                                with gr.Group(elem_classes="task-card"):
                                    gr.HTML(f"""
                                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                                        <div style="display: flex; align-items: center; gap: 8px;">
                                            <span style="font-size: 13px; color: #6b7280; font-weight: 500;">📋 {task['id']}</span>
                                            <span style="background: #d1fae5; color: #059669; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 500;">In Review</span>
                                        </div>
                                    </div>
                                    <div style="font-size: 15px; font-weight: 600; color: #111827; margin-bottom: 8px; line-height: 1.4;">{task['title']}</div>
                                    """)
                                    if task.get('description'):
                                        gr.HTML(f"<div style='font-size: 13px; color: #6b7280; line-height: 1.5; margin-bottom: 14px;'>{task['description']}</div>")
                                    del_btn = gr.Button("🗑️ Delete", variant="stop", size="sm")
                                    del_btn.click(
                                        fn=lambda tid=task['id']: delete_task(tid, "active"),
                                        outputs=[active_state]
                                    )
                        else:
                            gr.HTML("<div style='text-align: center; padding: 40px; color: #9ca3af;'>No tasks in review</div>")

            with gr.Row():
                active_input = gr.Textbox(
                    placeholder="Add a task...",
                    show_label=False,
                    container=False
                )
                active_btn = gr.Button("+ Task", variant="primary")

            def add_and_refresh(title):
                add_task(title, "backlog", "active")
                return {"refresh": datetime.now().isoformat()}, ""

            active_btn.click(
                fn=add_and_refresh,
                inputs=[active_input],
                outputs=[active_state, active_input]
            )
            active_input.submit(
                fn=add_and_refresh,
                inputs=[active_input],
                outputs=[active_state, active_input]
            )

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

        with gr.Tab("AutoPlan"):
            gr.Markdown("AutoPlan content coming soon...")

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        css="""
            footer {display: none !important;}
            .gradio-container {
                margin-bottom: 0 !important;
                background: #f8fafc !important;
            }

            /* Column styling */
            .column {
                background: #ffffff;
                border-radius: 16px;
                padding: 20px;
            }

            /* Task card styling */
            .task-card {
                background: #ffffff !important;
                border: 1px solid #e5e7eb !important;
                border-radius: 12px !important;
                padding: 16px !important;
                margin-bottom: 12px !important;
                box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02) !important;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }

            .task-card:hover {
                box-shadow: 0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04) !important;
                border-color: #cbd5e1 !important;
                transform: translateY(-1px);
            }

            /* Section headers */
            .section-header {
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 16px;
                padding-bottom: 12px;
                border-bottom: 1px solid #f3f4f6;
            }

            /* Button styling */
            button[variant="stop"] {
                background: #fee2e2 !important;
                color: #dc2626 !important;
                border: 1px solid #fecaca !important;
                border-radius: 8px !important;
                font-weight: 500 !important;
                font-size: 13px !important;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }

            button[variant="stop"]:hover {
                background: #fecaca !important;
                border-color: #fca5a5 !important;
                transform: translateY(-1px);
                box-shadow: 0 2px 8px rgba(220, 38, 38, 0.15) !important;
            }

            button[variant="primary"] {
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
                color: white !important;
                border: none !important;
                border-radius: 8px !important;
                font-weight: 500 !important;
                font-size: 13px !important;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }

            button[variant="primary"]:hover {
                background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35) !important;
            }

            button {
                border-radius: 8px !important;
                font-weight: 500 !important;
            }

            /* Input styling */
            .input-container input, .input-container textarea {
                border: 1px solid #e5e7eb !important;
                border-radius: 8px !important;
                padding: 10px 14px !important;
                transition: all 0.2s ease !important;
            }

            .input-container input:focus, .input-container textarea:focus {
                border-color: #3b82f6 !important;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
            }

            /* Tab styling */
            .tab-nav button {
                border-radius: 8px 8px 0 0 !important;
                font-weight: 500 !important;
                color: #6b7280 !important;
                transition: all 0.2s ease !important;
            }

            .tab-nav button:hover {
                background: #f9fafb !important;
                color: #374151 !important;
            }

            .tab-nav button[aria-selected="true"] {
                background: white !important;
                border-bottom: 3px solid #3b82f6 !important;
                color: #3b82f6 !important;
            }

            /* Empty state styling */
            .empty-state {
                text-align: center;
                padding: 60px 20px;
                color: #9ca3af;
                font-size: 14px;
            }

            /* Add Task button special styling */
            button:contains("+ Task") {
                background: #f97316 !important;
                box-shadow: 0 2px 8px rgba(249, 115, 22, 0.25) !important;
            }

            button:contains("+ Task"):hover {
                background: #ea580c !important;
                box-shadow: 0 4px 12px rgba(249, 115, 22, 0.35) !important;
            }
        """
    )
