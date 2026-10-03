"""Utility script to convert report/report.md into a high-quality academic PDF:
report/CSE307_Term_Paper_202414064.pdf
Uses headless Google Chrome for reliable, cross-platform PDF rendering.
"""
import os
import subprocess
import markdown


def markdown_to_pdf(
    md_path: str = "report/report.md",
    pdf_path: str = "report/CSE307_Term_Paper_202414064.pdf",
    chrome_path: str = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
) -> bool:
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Convert Markdown to HTML with table and code extensions
    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code"]
    )

    # Convert relative image paths for HTML rendering
    # in report.md it is ../results/before_after_shift.png
    # from report directory, it's ../results/before_after_shift.png
    # In the HTML file saved in report/, this relative path works directly!

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>CSE-307 Term Paper - Mahin Ar Rahman (202414064)</title>
<style>
    @page {{
        size: A4;
        margin: 16mm 18mm 16mm 18mm;
    }}
    body {{
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
        font-size: 9.8pt;
        line-height: 1.38;
        color: #1a1a1a;
        margin: 0;
        padding: 0;
    }}
    h1 {{
        font-size: 15.5pt;
        font-weight: 700;
        margin: 0 0 6px 0;
        color: #0f2d59;
        text-align: center;
    }}
    h2 {{
        font-size: 11.5pt;
        font-weight: 700;
        margin: 12px 0 4px 0;
        color: #0f2d59;
        border-bottom: 1.5px solid #d0d7de;
        padding-bottom: 2px;
        page-break-after: avoid;
    }}
    h3 {{
        font-size: 10.2pt;
        font-weight: 600;
        margin: 8px 0 2px 0;
        color: #24292f;
        page-break-after: avoid;
    }}
    p {{
        margin: 0 0 6px 0;
        text-align: justify;
    }}
    ul, ol {{
        margin: 0 0 6px 0;
        padding-left: 20px;
    }}
    li {{
        margin-bottom: 2px;
    }}
    hr {{
        border: none;
        border-top: 1px solid #e1e4e8;
        margin: 8px 0;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 8px 0 10px 0;
        font-size: 8.8pt;
        page-break-inside: avoid;
    }}
    th, td {{
        border: 1px solid #d0d7de;
        padding: 4px 7px;
        text-align: center;
    }}
    th {{
        background-color: #f2f5f8;
        font-weight: 600;
        color: #24292f;
    }}
    tr:nth-child(even) {{
        background-color: #fcfdfe;
    }}
    img {{
        display: block;
        max-width: 78%;
        max-height: 220px;
        margin: 8px auto;
        border: 1px solid #d0d7de;
        border-radius: 4px;
        page-break-inside: avoid;
    }}
    code {{
        font-family: Consolas, 'Courier New', monospace;
        background-color: #f6f8fa;
        padding: 1px 3px;
        border-radius: 3px;
        font-size: 9pt;
    }}
    .metadata {{
        text-align: center;
        font-size: 9.5pt;
        color: #444;
        margin-bottom: 12px;
    }}
</style>
</head>
<body>
{html_body}
</body>
</html>
"""

    temp_html = os.path.join(os.path.dirname(md_path), "temp_report.html")
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    abs_html = os.path.abspath(temp_html)
    abs_pdf = os.path.abspath(pdf_path)

    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={abs_pdf}",
        f"file:///{abs_html.replace(os.sep, '/')}"
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"[SUCCESS] PDF generated successfully: {pdf_path}")
        success = True
    except Exception as e:
        print(f"[ERROR] Failed to generate PDF: {e}")
        success = False
    finally:
        if os.path.exists(temp_html):
            os.remove(temp_html)

    return success


if __name__ == "__main__":
    markdown_to_pdf()
