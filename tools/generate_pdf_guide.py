import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Adds 'Page X of Y' and header/footer to each page."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 11 * 72 - 36, "SafeAd AI — Video Content Policy Benchmark & Platform Execution Guide")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)

        # Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 54, 36, page_str)
        self.drawString(54, 36, "Confidential — SafeAd AI / MBCET S7 Project")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 48, 8.5 * 72 - 54, 48)

        self.restoreState()

def build_pdf(filename="SafeAd_AI_Execution_Guide.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    c_primary = colors.HexColor("#1e1b4b")
    c_secondary = colors.HexColor("#312e81")
    c_accent = colors.HexColor("#2563eb")
    c_dark = colors.HexColor("#0f172a")
    c_muted = colors.HexColor("#475569")
    c_light = colors.HexColor("#f8fafc")
    c_border = colors.HexColor("#e2e8f0")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=c_primary,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_accent,
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=c_secondary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_dark,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_dark,
        spaceAfter=6
    )

    body_bold = ParagraphStyle(
        'Body_Bold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f1f5f9"),
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=c_dark
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell,
        fontName='Helvetica-Bold'
    )

    table_cell_header = ParagraphStyle(
        'TableHeader',
        parent=table_cell,
        fontName='Helvetica-Bold',
        textColor=colors.white
    )

    story = []

    # Title Banner Box
    title_box_data = [[
        Paragraph("<b>🛡️ SafeAd AI — Execution & Benchmark Guide</b>", title_style),
    ], [
        Paragraph("Command Prompt (CMD) Commands, One-Click Scripts, & Video Content Policy Accuracy", subtitle_style)
    ], [
        Paragraph("<b>Repository:</b> QuadRos-MBCET/main_project_s7 &nbsp;|&nbsp; <b>Dataset Hub:</b> safead-dataset-hub &nbsp;|&nbsp; <b>OS:</b> Windows", body_style)
    ]]
    t_title = Table(title_box_data, colWidths=[504])
    t_title.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('PADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,2), (-1,2), 10),
    ]))
    story.append(t_title)
    story.append(Spacer(1, 14))

    # SECTION 1: ONE-CLICK EXECUTION
    story.append(Paragraph("1. One-Click Batch Scripts (.bat)", h1_style))
    story.append(Paragraph(
        "For instant execution without opening PowerShell or typing long commands, two automated Windows Batch files have been created in the project root directory (<code>c:\\Users\\hello\\Videos\\sourav\\</code>). You can double-click them in Windows Explorer or run them from CMD:",
        body_style
    ))

    bat_table_data = [
        [Paragraph("Script File", table_cell_header), Paragraph("Purpose & Execution Behavior", table_cell_header)],
        [
            Paragraph("<b>run_video_policy_benchmark.bat</b>", table_cell_bold),
            Paragraph("Executes the complete 80-video content policy benchmark against the <code>safead-dataset-hub</code>. Sets paths and prints full accuracy metrics, category breakdown, and confusion matrix.", table_cell)
        ],
        [
            Paragraph("<b>start_safead_platform.bat</b>", table_cell_bold),
            Paragraph("Launches all 3 core services simultaneously in 3 independent CMD windows with health timing:<br/>• SafeAd Backend API (Port 8002)<br/>• Face-Age API (Port 8001)<br/>• Streamlit Unified Web App (Port 8501)", table_cell)
        ]
    ]
    t_bat = Table(bat_table_data, colWidths=[180, 324])
    t_bat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_bat)
    story.append(Spacer(1, 14))

    # SECTION 2: COMMAND PROMPT (CMD) COMMANDS
    story.append(Paragraph("2. Windows Command Prompt (CMD) Execution Guide", h1_style))
    story.append(Paragraph("Open standard Windows Command Prompt (<code>cmd.exe</code>) and use the exact commands below:", body_style))

    story.append(Paragraph("A. Run the 80-Video Content Policy Accuracy Benchmark", h2_style))
    story.append(Paragraph("This evaluates all 80 videos from the <code>safead-dataset-hub</code> across all 4 policy categories:", body_style))
    story.append(Paragraph(
        "cd /d c:\\Users\\hello\\Videos\\sourav<br/>"
        "set PYTHONPATH=c:\\Users\\hello\\Videos\\sourav;c:\\Users\\hello\\Videos\\sourav\\joseph_safead_core<br/>"
        "python tests\\evaluate_hub_dataset.py",
        code_style
    ))

    story.append(Paragraph("B. Start the Complete 3-Service Platform via CMD", h2_style))
    story.append(Paragraph("Open 3 separate CMD windows (or use <code>start_safead_platform.bat</code>):", body_style))

    story.append(Paragraph("<b>Window 1 — SafeAd Backend API (Port 8002):</b>", body_style))
    story.append(Paragraph(
        "cd /d c:\\Users\\hello\\Videos\\sourav<br/>"
        "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8002",
        code_style
    ))

    story.append(Paragraph("<b>Window 2 — Face-Age Estimation API (Port 8001):</b>", body_style))
    story.append(Paragraph(
        "cd /d c:\\Users\\hello\\Videos\\sourav<br/>"
        "set PYTHONPATH=c:\\Users\\hello\\Videos\\sourav;c:\\Users\\hello\\Videos\\sourav\\sooraj_face_age_core\\face-age<br/>"
        "python sooraj_face_age_core\\face-age\\face_age_api.py",
        code_style
    ))

    story.append(Paragraph("<b>Window 3 — Streamlit Web Application (Port 8501):</b>", body_style))
    story.append(Paragraph(
        "cd /d c:\\Users\\hello\\Videos\\sourav<br/>"
        "set PYTHONPATH=c:\\Users\\hello\\Videos\\sourav<br/>"
        "streamlit run frontend/app.py --server.port 8501",
        code_style
    ))

    story.append(Paragraph("C. PowerShell Equivalents (One-Liners)", h2_style))
    story.append(Paragraph(
        "cd c:\\Users\\hello\\Videos\\sourav<br/>"
        "$env:PYTHONPATH='c:\\Users\\hello\\Videos\\sourav;c:\\Users\\hello\\Videos\\sourav\\joseph_safead_core'<br/>"
        "python tests/evaluate_hub_dataset.py",
        code_style
    ))

    story.append(PageBreak())

    # SECTION 3: VIDEO CONTENT POLICY BENCHMARK RESULTS
    story.append(Paragraph("3. Video Content Policy Accuracy Benchmark Results", h1_style))
    story.append(Paragraph(
        "The model was evaluated against all 80 authentic video advertisements from <b><code>https://github.com/QuadRos-MBCET/safead-dataset-hub</code></b>. Below is the empirical performance summary:",
        body_style
    ))

    # Category Accuracy Table
    cat_table_data = [
        [Paragraph("Policy Category", table_cell_header), Paragraph("Total Videos", table_cell_header), Paragraph("Correct", table_cell_header), Paragraph("Empirical Accuracy", table_cell_header), Paragraph("Target Action", table_cell_header)],
        [Paragraph("<b>SAFE_18_PLUS</b>", table_cell), Paragraph("25", table_cell), Paragraph("23", table_cell), Paragraph("<b>92.00%</b>", table_cell), Paragraph("RESTRICT (Adult 18+)", table_cell)],
        [Paragraph("<b>SAFE_FOR_ALL</b>", table_cell), Paragraph("25", table_cell), Paragraph("22", table_cell), Paragraph("<b>88.00%</b>", table_cell), Paragraph("APPROVE (Universal)", table_cell)],
        [Paragraph("<b>UNSAFE_FOR_ALL</b>", table_cell), Paragraph("5", table_cell), Paragraph("4", table_cell), Paragraph("<b>80.00%</b>", table_cell), Paragraph("REJECT (Prohibited)", table_cell)],
        [Paragraph("<b>SAFE_14_PLUS</b>", table_cell), Paragraph("25", table_cell), Paragraph("15", table_cell), Paragraph("<b>60.00%</b>", table_cell), Paragraph("RESTRICT (Teens 14+)", table_cell)],
        [Paragraph("<b>OVERALL MULTICLASS</b>", table_cell_bold), Paragraph("<b>80</b>", table_cell_bold), Paragraph("<b>64</b>", table_cell_bold), Paragraph("<b>80.00%</b>", table_cell_bold), Paragraph("<b>4-Tier Policy</b>", table_cell_bold)]
    ]
    t_cat = Table(cat_table_data, colWidths=[120, 70, 60, 114, 140])
    t_cat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, c_light]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#e0e7ff")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_cat)
    story.append(Spacer(1, 10))

    # Confusion Matrix Table
    story.append(Paragraph("Multiclass Confusion Matrix (Actual vs Predicted)", h2_style))
    cm_data = [
        [Paragraph("Actual \\ Predicted", table_cell_header), Paragraph("SAFE_FOR_ALL", table_cell_header), Paragraph("SAFE_14_PLUS", table_cell_header), Paragraph("SAFE_18_PLUS", table_cell_header), Paragraph("UNSAFE_FOR_ALL", table_cell_header), Paragraph("Total", table_cell_header)],
        [Paragraph("<b>SAFE_FOR_ALL</b>", table_cell), Paragraph("<b>22</b>", table_cell_bold), Paragraph("1", table_cell), Paragraph("2", table_cell), Paragraph("0", table_cell), Paragraph("25", table_cell)],
        [Paragraph("<b>SAFE_14_PLUS</b>", table_cell), Paragraph("4", table_cell), Paragraph("<b>15</b>", table_cell_bold), Paragraph("4", table_cell), Paragraph("2", table_cell), Paragraph("25", table_cell)],
        [Paragraph("<b>SAFE_18_PLUS</b>", table_cell), Paragraph("0", table_cell), Paragraph("0", table_cell), Paragraph("<b>23</b>", table_cell_bold), Paragraph("2", table_cell), Paragraph("25", table_cell)],
        [Paragraph("<b>UNSAFE_FOR_ALL</b>", table_cell), Paragraph("1", table_cell), Paragraph("0", table_cell), Paragraph("0", table_cell), Paragraph("<b>4</b>", table_cell_bold), Paragraph("5", table_cell)],
        [Paragraph("<b>Total Predicted</b>", table_cell_bold), Paragraph("27", table_cell_bold), Paragraph("16", table_cell_bold), Paragraph("29", table_cell_bold), Paragraph("8", table_cell_bold), Paragraph("<b>80</b>", table_cell_bold)]
    ]
    t_cm = Table(cm_data, colWidths=[120, 80, 80, 80, 80, 64])
    t_cm.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#334155")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, c_light]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#f1f5f9")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_cm)
    story.append(Spacer(1, 10))

    # Binary Metrics Box
    story.append(Paragraph("Core Scientific Performance Metrics (Youth Protection Guardrail)", h2_style))
    metrics_data = [
        [Paragraph("<b>Harmful Ad Interception Recall:</b>", table_cell), Paragraph("<b>96.67%</b> (29 / 30 harmful/adult ads successfully intercepted)", table_cell)],
        [Paragraph("<b>False Acceptance Rate (FAR):</b>", table_cell), Paragraph("<b>3.33%</b> (Only 1 adult ad erroneously passed into youth tiers)", table_cell)],
        [Paragraph("<b>Youth-Safe Content Precision:</b>", table_cell), Paragraph("<b>97.67%</b> (Extremely high purity of youth-approved feed)", table_cell)],
        [Paragraph("<b>False Rejection Rate (FRR):</b>", table_cell), Paragraph("<b>16.00%</b> (Conservative over-flagging on borderline keywords)", table_cell)],
        [Paragraph("<b>Average Video Latency:</b>", table_cell), Paragraph("<b>58.9 ms</b> per video (Ultra-fast real-time inference)", table_cell)],
    ]
    t_m = Table(metrics_data, colWidths=[200, 304])
    t_m.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_m)
    story.append(Spacer(1, 14))

    # SECTION 4: PLATFORM WORKSPACES
    story.append(Paragraph("4. Platform Workspaces & User Flows", h1_style))
    
    flow_data = [
        [Paragraph("Workspace / Role", table_cell_header), Paragraph("Key Features & Verification Steps", table_cell_header)],
        [
            Paragraph("<b>User Workspace</b><br/>(Sooraj Biometrics + Instakill)", table_cell_bold),
            Paragraph("1. Upload official College ID card (PNG/JPG/PDF).<br/>2. Auto-DOB extraction with EXIF rotation handling.<br/>3. Start Live Camera feed at locked 30 FPS ArcFace.<br/>4. Click <b>'Freeze Current Frame'</b> to cross-match.<br/>5. On match (&ge;65%), login with username & password to enter Instakill social feed curated to verified age bracket.", table_cell)
        ],
        [
            Paragraph("<b>Brand Owner Workspace</b><br/>(Ad Campaign Submission)", table_cell_bold),
            Paragraph("1. Input creative title and ad caption.<br/>2. Upload video (.mp4) or image ad creative.<br/>3. Click <b>'Analyze Advertisement'</b>.<br/>4. Real-time keyframe sampling, OCR, NLP, and policy badge (SAFE FOR ALL, 14+, 18+, or REJECT).", table_cell)
        ],
        [
            Paragraph("<b>Admin Workspace</b><br/>(Human-in-the-Loop Review)", table_cell_bold),
            Paragraph("1. Inspect ads flagged for human moderator audit.<br/>2. View visual safety, OCR, and AI CoT explanation.<br/>3. Issue Override: Approve, Restrict, or Reject.", table_cell)
        ]
    ]
    t_flow = Table(flow_data, colWidths=[150, 354])
    t_flow.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_flow)
    story.append(Spacer(1, 14))

    # SECTION 5: TECHNICAL FIXES
    story.append(Paragraph("5. Technical Fixes & Reliability Safeguards", h1_style))
    story.append(Paragraph("The following production fixes have been implemented in the codebase:", body_style))
    story.append(Paragraph("• <b>Eliminated 0xC0000005 Windows Crash:</b> Disabled PyTorch MKL-DNN convolutions (<code>torch.backends.mkldnn.enabled = False</code>) to prevent native memory access violations during EasyOCR and ArcFace CPU forward passes.", body_style))
    story.append(Paragraph("• <b>Port Conflict Resolution:</b> Shifted SafeAd Backend from port 8000 to port 8002 to permanently avoid Windows ephemeral socket collisions with language servers.", body_style))
    story.append(Paragraph("• <b>Camera Session Persistence:</b> Streamlit session state preserves the <code>Realtime30FPSVisionEngine</code> so uploading or replacing ID cards does not crash the DirectShow camera hardware thread.", body_style))
    story.append(Paragraph("• <b>Mobile EXIF Transpose:</b> Applied <code>ImageOps.exif_transpose</code> so vertical mobile phone photos of college ID cards are automatically rotated upright before OCR.", body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated: {os.path.abspath(filename)}")

if __name__ == "__main__":
    build_pdf()
