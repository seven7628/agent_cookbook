from mcp.server.fastmcp import FastMCP

app = FastMCP("Math")

@app.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
@app.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers."""
    return a - b
@app.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b
@app.tool()
def divide(a: int, b: int) -> int:
    """Divide two numbers."""
    return a / b


if __name__ == "__main__":
    app.run(transport="stdio")