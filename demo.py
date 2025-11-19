#!/usr/bin/env python3
"""
Virtual MCP Composition Demo

A beautiful, interactive demonstration of Virtual MCP Server's composite tool
capabilities using the Rich library for stunning CLI output.
"""

import asyncio
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Optional

import yaml
from mcp import ClientSession, types
from mcp.client.streamable_http import streamablehttp_client
from rich.console import Console
from rich.json import JSON
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.tree import Tree
from rich import box
from rich.markdown import Markdown

# Configuration
VMCP_BIN = "vmcp"  # Use system-installed vmcp
THV_BIN = "thv"    # Use system-installed thv
CONFIG_FILE = Path("vmcp-config.yaml")
VMCP_URL = "http://127.0.0.1:4483"
VMCP_ENDPOINT = f"{VMCP_URL}/mcp"
HEALTH_ENDPOINT = f"{VMCP_URL}/health"

# Demo settings
AUTO_CONTINUE = os.getenv("AUTO_CONTINUE", "0") == "1"
DEMO_SPEED = os.getenv("DEMO_SPEED", "normal")

# Global state
vmcp_process: Optional[subprocess.Popen] = None
mcp_session: Optional[ClientSession] = None
exit_stack: Optional[AsyncExitStack] = None
console = Console(soft_wrap=True)


async def cleanup_async():
    """Cleanup MCP session and server asynchronously."""
    global vmcp_process, exit_stack

    # Close MCP session first
    if exit_stack:
        try:
            await exit_stack.aclose()
        except Exception:
            pass  # Ignore cleanup errors

    # Then stop vmcp server
    if vmcp_process:
        console.print("\n[yellow]Stopping Virtual MCP Server...[/yellow]")
        vmcp_process.terminate()
        try:
            vmcp_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            vmcp_process.kill()
        console.print("[green]✓ Server stopped[/green]")

def cleanup():
    """Synchronous cleanup wrapper."""
    try:
        asyncio.run(cleanup_async())
    except Exception:
        pass


def wait_for_user():
    """Wait for user to press Enter."""
    if not AUTO_CONTINUE:
        console.print("\n[dim]Press [bold]Enter[/bold] to continue...[/dim]")
        input()
    else:
        time.sleep(1 if DEMO_SPEED == "fast" else 2)


def print_banner(text: str, style: str = "bold magenta"):
    """Print a fancy banner."""
    console.print()
    console.print(Panel(
        Text(text, justify="center", style=style),
        border_style="magenta",
        box=box.DOUBLE,
        padding=(1, 2)
    ))
    console.print()


def print_section(title: str):
    """Print a section header."""
    console.print()
    console.print(f"[bold blue]{'=' * 80}[/bold blue]")
    console.print(f"[bold blue]{title}[/bold blue]")
    console.print(f"[bold blue]{'=' * 80}[/bold blue]")
    console.print()


def print_subsection(title: str):
    """Print a subsection header."""
    console.print()
    console.print(Panel(title, border_style="cyan", padding=(0, 2)))
    console.print()


def check_prerequisites():
    """Check that required binaries and files exist."""
    errors = []

    if not shutil.which(VMCP_BIN):
        errors.append(f"vmcp not found in PATH. Run: task install-vmcp")

    if not shutil.which(THV_BIN):
        errors.append(f"thv not found in PATH. Run: task install")

    if not CONFIG_FILE.exists():
        errors.append(f"Configuration file not found: {CONFIG_FILE}")

    if errors:
        console.print("[bold red]Prerequisites check failed:[/bold red]")
        for error in errors:
            console.print(f"  [red]✗ {error}[/red]")
        sys.exit(1)

    console.print("[green]✓ Prerequisites check passed[/green]")


def step_introduction():
    """Show introduction."""
    console.clear()

    print_banner("🌟 Virtual MCP Composition Demo 🌟")

    console.print("[bold white]Welcome to the Virtual MCP Server Composition Demo![/bold white]\n")

    console.print("[cyan]What is Virtual MCP Composition?[/cyan]")
    console.print("[white]" + "─" * 32 + "[/white]\n")

    console.print("Virtual MCP Server [bold]orchestrates multi-step workflows[/bold] across multiple")
    console.print("backend MCP servers, enabling complex operations in a single tool call.\n")

    features = Table(show_header=False, box=None, padding=(0, 2))
    features.add_column(style="green bold")
    features.add_column()

    features.add_row("✓", "[bold]Parallel Execution[/bold] - Independent steps run simultaneously")
    features.add_row("✓", "[bold]Sequential Dependencies[/bold] - Steps can depend on previous results")
    features.add_row("✓", "[bold]Output Aggregation[/bold] - Custom templates format results")
    features.add_row("✓", "[bold]Parameter Defaults[/bold] - JSON Schema defaults automatically applied")
    features.add_row("✓", "[bold]Workflow Metadata[/bold] - Timing and execution details included")

    console.print(features)
    console.print()

    console.print("[cyan]Today's Demos:[/cyan]")
    console.print("[white]" + "─" * 13 + "[/white]\n")

    demos = Table(show_header=False, box=None, padding=(0, 1))
    demos.add_column(style="magenta bold", width=3)
    demos.add_column(style="bold")
    demos.add_column()

    demos.add_row("1.", "Multi-Source Docs", "Fetch 3 documentation sources in parallel")
    demos.add_row("2.", "GitHub Health Check", "Analyze repository with sequential steps")
    demos.add_row("3.", "Container Investigation", "Query OCI registry for image details")

    console.print(demos)
    console.print()

    console.print("Let's get started! 🚀\n")

    wait_for_user()


def step_show_backends():
    """Show backend MCP servers."""
    console.clear()
    print_section("Step 1: Backend MCP Servers")

    console.print("[cyan]ℹ First, let's see what MCP servers are running...[/cyan]\n")
    time.sleep(0.5)

    console.print(f"[yellow]$ thv list --group default[/yellow]\n")

    try:
        result = subprocess.run(
            [THV_BIN, "list", "--group", "default"],
            capture_output=True,
            text=True,
            check=True
        )
        console.print(result.stdout)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error: {e.stderr}[/red]")
        console.print("[yellow]⚠ Make sure backend servers are running![/yellow]")
        console.print("\n[dim]Start backends with:[/dim]")
        console.print("[dim]  thv run --name fetch --group default mcp/fetch --port 8090[/dim]")
        console.print("[dim]  thv run --name github --group default mcp/github --port 8091[/dim]")
        console.print("[dim]  thv run --name oci-registry --group default mcp/oci-registry --port 8092[/dim]")
        sys.exit(1)

    console.print(Panel(
        "[green]✓ We have 3 backend MCP servers running![/green]",
        border_style="green"
    ))

    console.print("\n[magenta]★ Notice each backend has:[/magenta]")
    console.print("  • Unique URL and port")
    console.print("  • Different tool sets")
    console.print("  • Independent operation")

    wait_for_user()


def step_show_config():
    """Show configuration file."""
    console.clear()
    print_section("Step 2: Composite Tool Configuration")

    console.print("[cyan]ℹ Let's examine the composite tool definitions...[/cyan]\n")
    time.sleep(0.5)

    console.print(f"[yellow]$ cat {CONFIG_FILE}[/yellow]\n")

    with open(CONFIG_FILE) as f:
        config_content = f.read()

    syntax = Syntax(config_content, "yaml", theme="monokai", line_numbers=True, word_wrap=True)
    console.print(syntax)

    console.print(Panel(
        "[cyan]Configuration defines 3 composite tools with output_format templates[/cyan]",
        border_style="cyan"
    ))

    console.print("\n[magenta]★ Key configuration points:[/magenta]")
    console.print("  • [bold]group: default[/bold] - References our ToolHive group")
    console.print("  • [bold]composite_tools[/bold] - Multi-step workflow definitions")
    console.print("  • [bold]output_format[/bold] - Custom output aggregation templates")
    console.print("  • [bold]depends_on[/bold] - Step dependency declarations")

    wait_for_user()


def step_validate_config():
    """Validate configuration."""
    console.clear()
    print_section("Step 3: Configuration Validation")

    console.print("[cyan]ℹ Validating composite tool definitions...[/cyan]\n")
    time.sleep(0.5)

    console.print(f"[yellow]$ vmcp validate --config {CONFIG_FILE}[/yellow]\n")

    try:
        result = subprocess.run(
            [VMCP_BIN, "validate", "--config", str(CONFIG_FILE)],
            capture_output=True,
            text=True,
            check=True
        )
        console.print(result.stdout)
        console.print("\n[green]✓ Configuration is valid![/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]✗ Validation failed:[/red]\n{e.stderr}")
        sys.exit(1)

    wait_for_user()


async def step_start_server():
    """Start Virtual MCP Server and connect MCP client."""
    global vmcp_process, mcp_session, exit_stack

    console.clear()
    print_section("Step 4: Starting Virtual MCP Server & Client Connection")

    console.print("[cyan]ℹ Starting Virtual MCP Server...[/cyan]\n")
    time.sleep(0.5)

    console.print(f"[yellow]$ vmcp serve --config {CONFIG_FILE}[/yellow]\n")

    # Start server in background, logging only to file
    log_file = open("vmcp-server.log", "w")
    vmcp_process = subprocess.Popen(
        [VMCP_BIN, "serve", "--config", str(CONFIG_FILE)],
        stdout=log_file,
        stderr=subprocess.STDOUT,
        text=True
    )

    console.print(f"[cyan]ℹ Server starting (PID: {vmcp_process.pid})...[/cyan]")
    console.print(f"[dim]Logs saved to: vmcp-server.log[/dim]\n")

    # Wait for server to start with spinner
    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Waiting for server to be ready", total=None)

        # Import httpx only for health check
        import httpx

        for i in range(20):
            try:
                response = httpx.get(HEALTH_ENDPOINT, timeout=0.5)
                if response.status_code == 200:
                    progress.update(task, completed=True)
                    break
            except httpx.RequestError:
                pass
            await asyncio.sleep(0.5)
        else:
            console.print("[red]✗ Server failed to start[/red]")
            sys.exit(1)

    console.print("\n[green]✓ Virtual MCP Server is running![/green]\n")

    # Connect MCP client
    console.print("[cyan]ℹ Connecting MCP client to server...[/cyan]\n")

    try:
        exit_stack = AsyncExitStack()

        # Connect to VMCP via Streamable HTTP transport
        # The streamablehttp_client returns (read_stream, write_stream, _)
        read_stream, write_stream, _ = await exit_stack.enter_async_context(
            streamablehttp_client(VMCP_ENDPOINT)
        )

        # Create client session
        mcp_session = await exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )

        # Initialize session
        await mcp_session.initialize()

        console.print("[green]✓ MCP client connected successfully![/green]\n")

    except Exception as e:
        console.print(f"[red]✗ Failed to connect MCP client: {e}[/red]")
        sys.exit(1)

    console.print("[magenta]★ Server endpoints:[/magenta]")
    console.print(f"  • MCP Endpoint: [bold]{VMCP_ENDPOINT}[/bold]")
    console.print(f"  • Health Check: [bold]{HEALTH_ENDPOINT}[/bold]")
    console.print(f"  • MCP Client: [bold]Connected via SSE transport[/bold]")

    wait_for_user()


async def execute_composite_tool(tool_name: str, params: dict) -> dict:
    """Execute a composite tool using the MCP SDK and return the result."""
    global mcp_session

    if not mcp_session:
        raise RuntimeError("MCP session not initialized")

    try:
        # Use the MCP SDK's call_tool method
        result = await mcp_session.call_tool(tool_name, params)

        # Return the CallToolResult object
        # result.content is a list of content blocks
        # result.isError indicates if there was an error
        return {
            "content": result.content,
            "isError": result.isError if hasattr(result, 'isError') else False
        }
    except Exception as e:
        console.print(f"[red]✗ Tool call failed: {e}[/red]")
        raise


def display_workflow_result(result: dict, title: str = "Workflow Result"):
    """Display workflow result with proper formatting and wrapping."""
    if not result or "content" not in result or not result["content"]:
        console.print("[yellow]No result content[/yellow]")
        return

    # MCP SDK returns CallToolResult with content list
    # Use types.TextContent to properly access text
    for content in result["content"]:
        if isinstance(content, types.TextContent):
            # content.text contains the JSON string from output_format
            try:
                parsed_result = json.loads(content.text)
            except json.JSONDecodeError:
                parsed_result = {"raw_output": content.text}

            # Truncate long text fields for demo readability
            truncated_result = truncate_long_fields(parsed_result, max_length=150)

            # Use Rich's JSON renderer for better wrapping and formatting
            panel = Panel(
                JSON.from_data(truncated_result),
                title=f"[bold cyan]{title}[/bold cyan]",
                border_style="cyan",
                expand=False,
                padding=(1, 2)
            )
            console.print(panel)
            break


def truncate_long_fields(data: any, max_length: int = 150) -> any:
    """Recursively truncate long string fields in data structure."""
    if isinstance(data, dict):
        return {k: truncate_long_fields(v, max_length) for k, v in data.items()}
    elif isinstance(data, list):
        return [truncate_long_fields(item, max_length) for item in data]
    elif isinstance(data, str) and len(data) > max_length:
        return data[:max_length] + "... (truncated)"
    else:
        return data


async def step_demo_aggregate_docs():
    """Demo 1: Multi-source documentation aggregator."""
    console.clear()
    print_section("Demo 1: Multi-Source Documentation Aggregator")

    print_subsection("Workflow Overview")

    # Show workflow diagram
    tree = Tree("🎯 [bold]aggregate_docs[/bold]")
    parallel = tree.add("[cyan]Parallel Execution[/cyan]")
    parallel.add("📄 fetch_source_1 → MCP README")
    parallel.add("📄 fetch_source_2 → Basic Spec")
    parallel.add("📄 fetch_source_3 → Transports Doc")
    tree.add("📊 Aggregate with output_format")

    console.print(tree)
    console.print()

    console.print("[magenta]★ This demonstrates:[/magenta]")
    console.print("  • [bold]Parallel execution[/bold] - 3 fetches run simultaneously")
    console.print("  • [bold]Output aggregation[/bold] - Custom template structures results")
    console.print("  • [bold]Workflow timing[/bold] - Duration and metadata included\n")

    wait_for_user()

    console.print("[cyan]Executing composite tool...[/cyan]\n")

    start_time = time.time()

    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Fetching 3 documentation sources", total=100)

        # Execute tool using async call
        result = await execute_composite_tool("aggregate_docs", {})

        progress.update(task, completed=100)

    duration = time.time() - start_time

    console.print(f"\n[green]✓ Workflow completed in {duration:.2f}s[/green]\n")

    # Display result
    print_subsection("Aggregated Result")
    display_workflow_result(result, "Documentation Aggregation")

    wait_for_user()


async def step_demo_analyze_repo():
    """Demo 2: GitHub repository health check."""
    console.clear()
    print_section("Demo 2: GitHub Repository Health Check")

    print_subsection("Workflow Overview")

    # Show workflow diagram
    tree = Tree("🎯 [bold]analyze_repository[/bold]")
    step1 = tree.add("1️⃣ get_repo_info → Fetch repository metadata")
    step2 = step1.add("[dim](depends on step 1)[/dim]")
    step2.add("2️⃣ list_issues → Get recent issues")
    step2.add("3️⃣ list_commits → Get latest commits")
    tree.add("📊 Generate health report")

    console.print(tree)
    console.print()

    console.print("[magenta]★ This demonstrates:[/magenta]")
    console.print("  • [bold]Sequential dependencies[/bold] - Steps wait for previous completion")
    console.print("  • [bold]Parameter defaults[/bold] - Uses default repo if not specified")
    console.print("  • [bold]GitHub MCP integration[/bold] - Multi-step API orchestration\n")

    wait_for_user()

    console.print("[cyan]Executing composite tool...[/cyan]\n")
    console.print("[dim]Using default: modelcontextprotocol/specification[/dim]\n")

    start_time = time.time()

    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing repository", total=100)

        # Execute tool (uses defaults from config)
        result = await execute_composite_tool("analyze_repository", {})

        progress.update(task, completed=100)

    duration = time.time() - start_time

    console.print(f"\n[green]✓ Workflow completed in {duration:.2f}s[/green]\n")

    # Display result
    print_subsection("Repository Health Report")
    display_workflow_result(result, "GitHub Activity Analysis")

    wait_for_user()


async def step_demo_investigate_image():
    """Demo 3: Container image investigation."""
    console.clear()
    print_section("Demo 3: Container Image Investigation")

    print_subsection("Workflow Overview")

    # Show workflow diagram
    tree = Tree("🎯 [bold]investigate_image[/bold]")
    step1 = tree.add("1️⃣ get_image_info → Query registry metadata")
    parallel = step1.add("[cyan]Parallel Execution (after step 1)[/cyan]")
    parallel.add("2️⃣ get_manifest → Fetch image manifest")
    parallel.add("3️⃣ get_config → Fetch image config")
    tree.add("📊 Generate comprehensive report")

    console.print(tree)
    console.print()

    console.print("[magenta]★ This demonstrates:[/magenta]")
    console.print("  • [bold]OCI registry integration[/bold] - Query container registries")
    console.print("  • [bold]Mixed execution[/bold] - Sequential then parallel steps")
    console.print("  • [bold]Real-world use case[/bold] - Debugging container images\n")

    wait_for_user()

    console.print("[cyan]Executing composite tool...[/cyan]\n")
    console.print("[dim]Using default: docker.io/library/alpine:latest[/dim]\n")

    start_time = time.time()

    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Investigating container image", total=100)

        # Execute tool
        result = await execute_composite_tool("investigate_image", {})

        progress.update(task, completed=100)

    duration = time.time() - start_time

    console.print(f"\n[green]✓ Workflow completed in {duration:.2f}s[/green]\n")

    # Display result
    print_subsection("Image Analysis Report")
    display_workflow_result(result, "Container Image Details")

    wait_for_user()


def step_summary():
    """Show demo summary."""
    console.clear()
    print_banner("✅ Demo Complete!", "bold green")

    console.print("[bold white]What We Demonstrated:[/bold white]\n")

    summary_table = Table(show_header=False, box=None, padding=(0, 2))
    summary_table.add_column(style="green bold")
    summary_table.add_column()

    summary_table.add_row("✓", "[bold]Composite Tools[/bold] - Multi-step workflows orchestrated by Virtual MCP")
    summary_table.add_row("✓", "[bold]Parallel Execution[/bold] - Independent steps run simultaneously for performance")
    summary_table.add_row("✓", "[bold]Sequential Dependencies[/bold] - Steps coordinate based on dependencies")
    summary_table.add_row("✓", "[bold]Output Aggregation[/bold] - Custom templates structure complex results")
    summary_table.add_row("✓", "[bold]Multi-Backend Orchestration[/bold] - Seamless coordination across backends")

    console.print(summary_table)
    console.print()

    console.print("[cyan bold]Key Metrics:[/cyan bold]\n")

    metrics = Table(show_header=False, box=None)
    metrics.add_column(style="bold")
    metrics.add_column(justify="right")

    metrics.add_row("Composite tools demonstrated", "3")
    metrics.add_row("Backend servers orchestrated", "3 (fetch + github + oci-registry)")
    metrics.add_row("Total workflow steps executed", "~10")
    metrics.add_row("Parallel steps", "Multiple")

    console.print(metrics)
    console.print()

    console.print("[yellow bold]Why This Matters:[/yellow bold]\n")
    console.print("Traditional MCP clients call individual tools sequentially. Virtual MCP enables:")
    console.print("  • [bold]Agent-friendly operations[/bold] - Complex tasks in single tool calls")
    console.print("  • [bold]Performance[/bold] - Parallel execution when possible")
    console.print("  • [bold]Structured outputs[/bold] - Consistent, parseable results")
    console.print("  • [bold]Cross-backend workflows[/bold] - Orchestrate multiple systems\n")

    console.print("[magenta bold]Try It Yourself:[/magenta bold]\n")
    console.print(f"  1. Connect your MCP client to [bold]{VMCP_ENDPOINT}[/bold]")
    console.print("  2. Call composite tools: [cyan]aggregate_docs[/cyan], [cyan]analyze_repository[/cyan], [cyan]investigate_image[/cyan]")
    console.print("  3. Watch Virtual MCP orchestrate multi-step workflows\n")

    console.print("[white bold]Thank you for watching![/white bold] 🎉\n")


async def async_main():
    """Async main demo flow."""
    global exit_stack

    try:
        # Check prerequisites
        check_prerequisites()

        # Run demo steps
        step_introduction()
        step_show_backends()
        step_show_config()
        step_validate_config()
        await step_start_server()
        await step_demo_aggregate_docs()
        await step_demo_analyze_repo()
        await step_demo_investigate_image()
        step_summary()

        # Ask if user wants to keep server running
        if not AUTO_CONTINUE:
            console.print()
            keep_running = console.input("[cyan bold]Keep Virtual MCP Server running? (y/N): [/cyan bold]")

            if keep_running.lower() != 'y':
                await cleanup_async()
            else:
                console.print("\n[green]✓ Server will continue running[/green]")
                console.print(f"[cyan]ℹ To stop later: kill {vmcp_process.pid}[/cyan]")
                # Close MCP session but keep server running
                if exit_stack:
                    try:
                        await exit_stack.aclose()
                    except Exception:
                        pass
                # Don't cleanup on exit
                signal.signal(signal.SIGINT, signal.SIG_DFL)
                signal.signal(signal.SIGTERM, signal.SIG_DFL)
        else:
            await cleanup_async()

    except Exception as e:
        console.print(f"\n[red bold]Error: {e}[/red bold]")
        await cleanup_async()
        sys.exit(1)


def main():
    """Main entry point."""
    # Setup cleanup handler
    signal.signal(signal.SIGINT, lambda s, f: cleanup() or sys.exit(0))
    signal.signal(signal.SIGTERM, lambda s, f: cleanup() or sys.exit(0))

    try:
        asyncio.run(async_main())
    except Exception as e:
        console.print(f"\n[red bold]Error: {e}[/red bold]")
        cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()
