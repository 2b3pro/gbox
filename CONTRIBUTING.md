# Contributing Tools to gbox

Adding new capabilities to `gbox` is straightforward. The project uses a modular architecture where tools are defined in specialized modules and registered in a central aggregator.

## The Tool Registry

There isn't a complex internal registry; instead, `gbox` looks at the `tools` list and `tool_sets` dictionary defined in `preset.py`. 

1.  **Individual Tools**: Functions defined in the `tools/` directory.
2.  **Aggregation**: `preset.py` imports these functions and adds them to a master `tools` list.
3.  **Sets**: `preset.py` groups tools into logical categories (like `fs`, `web`, `sys`) used by the `--tools` flag.

---

## How to Add a New Tool

### 1. Create the Tool Function
Create your tool in an existing module in `tools/` (e.g., `tools/utils.py`) or create a new file if it's a new category.

**Requirements:**
- **Type Hints**: You MUST include type hints for all arguments and the return type.
- **Google-Style Docstrings**: The first line should be a clear description. Parameters should be documented in an `Args:` section. This is how the model "understands" your tool.

```python
# tools/my_new_module.py

def calculate_power(base: float, exponent: float) -> str:
    """Calculates the power of a number.
    
    Args:
        base: The number to be raised.
        exponent: The power to raise the base to.
    """
    try:
        result = base ** exponent
        return f"{base} to the power of {exponent} is {result}"
    except Exception as e:
        return f"Error: {e}"

tools = [calculate_power]
```

### 2. Register the Module (if new)
If you created a new file, ensure you export a `tools` list at the bottom of that file (as shown above).

### 3. Update `preset.py`
Add your new module or function to `preset.py` so `gbox` can find it.

```python
# preset.py
from tools import my_new_module

# ...

# Add to the global tools list
tools = (
    # ... other tools
    my_new_module.tools
)

# (Optional) Add to a tool set
tool_sets = {
    "math": [my_new_module.calculate_power],
    # ...
}
```

### 4. Categorize (Optional)
If your tool is complex and requires significant "reasoning" or "cognition," add its function name to the `HIGH_COGNITION_TOOLS` set at the top of the `gbox` script. This will trigger the smart recommendation for users to use the `--high` (4B) model.

---

## Best Practices
- **Error Handling**: Always return errors as strings starting with `"Error: "`. This allows the LLM to understand what went wrong and potentially retry.
- **Statelessness**: Tools should generally be stateless. If you need persistence, use a local file or a database tool.
- **Safety**: Tools that execute code or modify the filesystem should be written defensively.
- **Mac-Native**: Since this is optimized for macOS edge computing, feel free to leverage built-in utilities like `sips`, `osascript`, or `screencapture`.
