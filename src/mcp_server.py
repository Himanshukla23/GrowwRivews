"""
FastMCP Server: Google Workspace Tools
Exposes Google Docs and Gmail delivery as MCP-compatible tools.

This server can be:
1. Run standalone: `python src/mcp_server.py` (for AI agent integration)
2. Called directly via the tool functions from main.py

Usage with MCP clients (e.g. Claude Desktop):
    Add to your MCP config:
    {
        "mcpServers": {
            "google_workspace": {
                "command": "python",
                "args": ["src/mcp_server.py"]
            }
        }
    }
"""

import os
import sys

# Ensure project root is on path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

# Initialize the FastMCP server
mcp = FastMCP(
    "GoogleWorkspaceServer",
    description="MCP server for Google Docs and Gmail delivery in the Weekly Product Pulse system.",
)


# ---------------------------------------------------------------------------
# Tool: Google Docs — Append Report
# ---------------------------------------------------------------------------

@mcp.tool()
def append_to_doc(report_text: str, doc_id: str = "") -> str:
    """
    Appends a report to a Google Doc.

    Inserts the report text at the end of the specified Google Doc,
    preceded by a section divider. Preserves all existing content.

    Args:
        report_text: The Markdown report content to append.
        doc_id: Google Doc ID. If empty, uses GOOGLE_DOC_ID from environment.

    Returns:
        The URL of the updated Google Doc, or an error message.
    """
    try:
        from src.phase_5.docs_delivery import append_to_doc as _append
        doc_url = _append(report_text, doc_id=doc_id if doc_id else None)
        return f"Success: Report appended. URL: {doc_url}"
    except Exception as e:
        return f"Error: {str(e)}"


# ---------------------------------------------------------------------------
# Tool: Gmail — Send Summary Email
# ---------------------------------------------------------------------------

@mcp.tool()
def send_summary_email(
    doc_link: str = "",
    product_name: str = "Groww",
    theme_count: int = 0,
    recipient: str = "",
) -> str:
    """
    Sends a summary notification email with a link to the report.

    Sends a professional HTML email to the specified recipient (or the
    default from RECIPIENT_EMAIL env var) containing a link to the
    Google Doc report.

    Args:
        doc_link: URL of the Google Doc containing the full report.
        product_name: Product name for the email subject line.
        theme_count: Number of themes detected (shown in the email body).
        recipient: Email address. If empty, uses RECIPIENT_EMAIL from environment.

    Returns:
        A success or error message.
    """
    try:
        from src.phase_6.gmail_delivery import send_summary_email as _send
        success = _send(
            doc_link=doc_link if doc_link else None,
            product_name=product_name,
            theme_count=theme_count,
            recipient=recipient if recipient else None,
        )
        return "Success: Email sent." if success else "Error: Email sending failed."
    except Exception as e:
        return f"Error: {str(e)}"


# ---------------------------------------------------------------------------
# Entry Point — Run as standalone MCP server
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Starting Google Workspace MCP Server...")
    mcp.run()
