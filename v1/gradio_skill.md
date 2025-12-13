# Gradio Working Patterns

## Known Limitations

### HTML Component Cannot Trigger Python
- `gr.HTML()` with `onclick` **cannot** call Python functions
- GitHub issue confirms this is intentional design
- Maintainers say it "opens enormous can of worms"

## Working Solutions

### Interactive Buttons
**Problem:** Need clickable buttons in dynamic lists
**Solution:** Use `@gr.render()` + native `gr.Button()`

```python
with gr.Tab("Tasks"):
    state = gr.State({"refresh": datetime.now().isoformat()})

    @gr.render(inputs=state)
    def render_tasks(s):
        tasks = load_tasks()
        for task in tasks:
            with gr.Group():
                gr.HTML(f"<div>{task['title']}</div>")
                btn = gr.Button("Delete")
                btn.click(
                    fn=lambda tid=task['id']: delete_task(tid),
                    outputs=[state]
                )
```

### State Management for Re-renders
**Problem:** UI doesn't refresh after actions
**Solution:** Return new state dict with timestamp

```python
def delete_task(task_id):
    # ... delete logic ...
    return {"refresh": datetime.now().isoformat()}
```

### Async Event Loop for SDK
**Problem:** Gradio sync functions + async SDK client
**Solution:** Thread-safe event loop

```python
loop = None

def init_event_loop():
    global loop
    if loop is None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        threading.Thread(target=loop.run_forever, daemon=True).start()

def sync_wrapper(msg):
    init_event_loop()
    future = asyncio.run_coroutine_threadsafe(async_fn(msg), loop)
    return future.result()
```

## Best Practices

1. **Use native components** - `gr.Button()`, `gr.Textbox()` over HTML hacks
2. **Use `@gr.render()`** - For dynamic content that updates
3. **State triggers re-render** - Change state value to force UI update
4. **Lambda closures** - Capture task IDs in button callbacks: `lambda tid=task['id']`
5. **HTML for styling only** - Use `gr.HTML()` for static styled content, not interactions
