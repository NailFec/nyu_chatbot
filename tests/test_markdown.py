#!/usr/bin/env python3
"""
Test script for Markdown functionality in the HPC ChatBot
"""

from hpc_chatbot import HPC_ChatBot
import tempfile
import webbrowser

def test_markdown_rendering():
    """Test the markdown rendering functionality"""
    
    # Create chatbot instance
    chatbot = HPC_ChatBot()
    
    # Test markdown content
    test_markdown = """
# GPU Booking Information

Thank you for your interest in our **SK HPC Services**! Here's what we offer:

## Available GPU Models

| GPU Model | Memory | Price/30min | Use Case |
|-----------|--------|-------------|----------|
| RTX-4090 | 24GB | $15.00 | AI Training, Gaming |
| H100 | 80GB | $50.00 | Large Model Training |
| A100 | 40GB | $30.00 | AI/ML Workloads |

## Booking Process

1. **Choose your GPU model** based on your requirements
2. **Select time slot** when you need the GPU
3. **Provide contact information** for booking confirmation
4. **Complete payment** and receive booking confirmation

### Code Example

Here's how you might use our GPU for PyTorch training:

```python
import torch
import torch.nn as nn

# Check if GPU is available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Create a simple model
model = nn.Linear(100, 10).to(device)
data = torch.randn(32, 100).to(device)
output = model(data)
```

### Important Notes

> **Security**: Always keep your booking hash and email safe - you'll need both to cancel bookings.

> **Pricing**: All prices are per 30-minute slots. Extended usage will be charged accordingly.

### Quick Actions

- Book a GPU: `I want to book a RTX-4090 for tomorrow`
- Check availability: `What GPUs are available this week?`
- Get recommendations: `What GPU do you recommend for LLaMA training?`

For support, contact: **nailfec17@gmail.com**

---

*This is an AI-generated response with markdown formatting support.*
    """
    
    # Convert markdown to HTML
    html_content = chatbot.markdown_to_html(test_markdown)
    
    # Create a test HTML file
    test_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Markdown Test - SK HPC Services</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github.min.css">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
                background: #f8f9fa;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            h1, h2, h3 {{ color: #2c3e50; }}
            table {{ 
                border-collapse: collapse; 
                width: 100%; 
                margin: 1em 0;
            }}
            table th, table td {{ 
                border: 1px solid #bdc3c7; 
                padding: 0.5em; 
                text-align: left; 
            }}
            table th {{ 
                background: #3498db; 
                color: white; 
            }}
            table tr:nth-child(even) {{ 
                background: rgba(52, 152, 219, 0.05); 
            }}
            blockquote {{ 
                border-left: 4px solid #3498db; 
                background: rgba(52, 152, 219, 0.1); 
                padding: 0.5em 1em; 
                margin: 1em 0; 
                border-radius: 0 4px 4px 0; 
            }}
            code {{ 
                background: rgba(52, 152, 219, 0.1); 
                padding: 2px 6px; 
                border-radius: 3px; 
                font-family: 'Courier New', Consolas, monospace; 
                color: #e74c3c; 
            }}
            pre {{ 
                background: #2c3e50; 
                color: #ecf0f1; 
                padding: 1em; 
                border-radius: 6px; 
                overflow-x: auto; 
            }}
            pre code {{ 
                background: none; 
                color: inherit; 
                padding: 0; 
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 style="text-align: center; color: #667eea;">SK HPC Services - Markdown Test</h1>
            {html_content}
        </div>
    </body>
    </html>
    """
    
    # Save to temporary file and open
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(test_html)
        temp_file = f.name
    
    print(f"Test HTML file created: {temp_file}")
    print("Opening in browser...")
    webbrowser.open(f'file://{temp_file}')
    
    return True

if __name__ == "__main__":
    print("Testing Markdown functionality...")
    test_markdown_rendering()
    print("Test completed! Check your browser for the rendered output.")
