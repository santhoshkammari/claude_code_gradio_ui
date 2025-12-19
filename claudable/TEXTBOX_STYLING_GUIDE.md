# Gradio Textbox Styling: Complete Guide

This document explains the various approaches to styling textboxes in Gradio applications, from built-in themes to custom CSS implementations.

## 1. Built-in Themes

Gradio provides several built-in themes that give you a consistent look and feel:

### Available Themes:
- `gr.themes.Default()` - The standard Gradio theme
- `gr.themes.Soft()` - A softer, more rounded theme
- `gr.themes.Glass()` - A glassmorphism effect theme
- `gr.themes.Monochrome()` - A single-color theme
- `gr.themes.Ocean()` - Blue-themed color scheme
- `gr.themes.Citrus()` - Warm, fruity color theme

### Usage Example:
```python
import gradio as gr

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    textbox = gr.Textbox(label="Themed Textbox")
```

## 2. Component-level Styling with elem_classes

Each component accepts an `elem_classes` parameter that allows you to apply custom CSS classes:

### Parameters:
- `elem_classes`: A string or list of strings that are assigned as CSS classes to the component
- `elem_id`: A string that is assigned as the CSS ID of the component
- `container`: Controls whether the component is placed in a container (adds padding)

### Example:
```python
textbox = gr.Textbox(
    label="Custom Styled Textbox", 
    elem_classes=["rounded-textbox", "large-font"],
    container=False  # Removes default container padding
)
```

## 3. Custom CSS Styling

You can add custom CSS in multiple ways:

### A. CSS parameter in Blocks/Interface:
```python
css = """
.rounded-textbox {
    border-radius: 12px !important;
    border: 2px solid #e2e8f0 !important;
}
"""

with gr.Blocks(css=css) as demo:
    textbox = gr.Textbox(elem_classes=["rounded-textbox"])
```

### B. External CSS file:
```python
with gr.Blocks(css=open("styles.css", "r").read()) as demo:
    textbox = gr.Textbox(elem_classes=["custom-style"])
```

## 4. Advanced Styling Options

### HTML Attributes
Components support HTML attributes through the `html_attributes` parameter:

```python
from gradio.components.textbox import InputHTMLAttributes

textbox = gr.Textbox(
    label="Text with HTML attributes",
    html_attributes=InputHTMLAttributes(
        spellcheck=False,
        autocomplete="off",
        autocorrect="off"
    )
)
```

### Container Control
You can control how the textbox appears by toggling the container:

```python
# With container (default) - includes padding and border
textbox1 = gr.Textbox(label="With Container", container=True)

# Without container - more compact appearance
textbox2 = gr.Textbox(label="Without Container", container=False)
```

## 5. Multi-line Textbox Styling

Multi-line textboxes (textareas) can be styled differently:

```python
multiline = gr.Textbox(
    lines=5,           # Initial visible lines
    max_lines=15,      # Maximum expandable lines
    elem_classes=["gradient-textbox"],
    placeholder="Enter multiple lines..."
)
```

## 6. Styling Best Practices

### A. Consistent Class Names
Use consistent, semantic class names in `elem_classes`:

```python
# Good
gr.Textbox(elem_classes=["input-primary"])
gr.Textbox(elem_classes=["input-secondary"])

# Avoid
gr.Textbox(elem_classes=["class123"])
```

### B. Use !important for Gradio CSS Override
Gradio's default styles are quite specific, so often you'll need `!important`:

```css
.my-textbox {
    border-radius: 12px !important;
    padding: 12px !important;
}
```

### C. Responsive Design
Consider responsive design for different screen sizes:

```css
.my-textbox {
    padding: 12px !important;
    font-size: 16px !important;
}

@media (max-width: 768px) {
    .my-textbox {
        font-size: 14px !important;
        padding: 8px !important;
    }
}
```

## 7. Complete Example

Here's a comprehensive example combining multiple approaches:

```python
import gradio as gr

def process_text(text):
    return f"Processed: {text}"

with gr.Blocks(
    theme=gr.themes.Soft(),
    css="""
    .modern-textbox {
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 12px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
    }
    
    .modern-textbox:focus-within {
        border-color: #6366f1 !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2) !important;
    }
    """
) as demo:
    textbox = gr.Textbox(
        label="Modern Styled Textbox",
        placeholder="Type something...",
        elem_classes=["modern-textbox"],
        container=False
    )
    
    btn = gr.Button("Submit")
    output = gr.Textbox(label="Output", interactive=False)
    
    btn.click(fn=process_text, inputs=textbox, outputs=output)

demo.launch()
```

## 8. Common CSS Properties for Textboxes

Here are common CSS properties you might want to customize:

- `border` - Border style, width, and color
- `border-radius` - Corner rounding
- `padding` - Internal spacing
- `background-color` - Background color
- `font-size` - Text size
- `font-family` - Text font
- `box-shadow` - Shadow effects
- `transition` - Animation transitions
- `outline` - Focus outline
- `height`/`min-height` - Height properties

## 9. Tips for Modern Styling

1. **Use consistent spacing** - Keep padding and margins consistent across components
2. **Choose a color palette** - Stick to 2-3 main colors for a cohesive look
3. **Consider dark mode** - Gradio themes automatically support dark mode
4. **Test on different devices** - Ensure your styling works on mobile and desktop
5. **Keep accessibility in mind** - Ensure sufficient contrast ratios for text
6. **Use transitions** - Smooth transitions improve user experience
7. **Consider loading states** - Style components for loading and error states as well

This comprehensive approach allows you to create modern, attractive textbox components in your Gradio applications.