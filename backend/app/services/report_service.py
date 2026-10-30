import io
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


class ReportService:
    @classmethod
    def generate_pdf_report(cls, session_data: Dict[str, Any]) -> bytes:
        """Generates an elegant, executive-ready PDF report of an interview session."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
        )

        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1e1b4b"),
            fontName="Helvetica-Bold",
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#475569"),
        )
        section_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#4338ca"),
            fontName="Helvetica-Bold",
            spaceBefore=12,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#334155"),
        )
        bold_body = ParagraphStyle(
            "BoldBody",
            parent=body_style,
            fontName="Helvetica-Bold",
        )

        elements = []

        # Header
        elements.append(Paragraph("Resume2Interview AI — Official Evaluation Report", title_style))
        elements.append(Paragraph(f"Target Role: {session_data.get('target_role', 'Software Engineer')} | Session ID: #{session_data.get('id', 'N/A')}", subtitle_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#6366f1"), spaceAfter=15))

        # Overall Summary Box
        score = session_data.get("overall_score") or 0.0
        readiness = session_data.get("readiness_score") or score
        status = session_data.get("status", "completed").capitalize()

        summary_data = [
            [
                Paragraph("<b>Overall Interview Score:</b>", body_style),
                Paragraph(f"<b><font size='14' color='#4338ca'>{score:.1f} / 100</font></b>", body_style),
                Paragraph("<b>Status:</b>", body_style),
                Paragraph(f"<b>{status}</b>", body_style),
            ],
            [
                Paragraph("<b>Estimated Readiness Index:</b>", body_style),
                Paragraph(f"<b><font size='12' color='#10b981'>{readiness:.1f}%</font></b>", body_style),
                Paragraph("<b>Total Questions:</b>", body_style),
                Paragraph(f"{len(session_data.get('questions', []))}", body_style),
            ]
        ]
        summary_table = Table(summary_data, colWidths=[1.8 * inch, 1.6 * inch, 1.4 * inch, 1.6 * inch])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 15))

        # Questions & Detailed Evaluations
        elements.append(Paragraph("Question-by-Question Evaluation & Rubric Breakdown", section_style))
        elements.append(Spacer(1, 6))

        for idx, q in enumerate(session_data.get("questions", []), 1):
            q_text = q.get("question_text", "")
            cat = q.get("category", "General").capitalize()
            diff = q.get("difficulty", "Intermediate").capitalize()
            ans_obj = q.get("answer") or {}
            ans_text = ans_obj.get("answer_text", "No answer recorded.")
            eval_obj = ans_obj.get("evaluation") or {}
            q_score = eval_obj.get("overall_score", 0.0)

            elements.append(Paragraph(f"<b>Q{idx} ({cat} • {diff}):</b> {q_text}", bold_body))
            elements.append(Spacer(1, 4))
            elements.append(Paragraph(f"<i>Candidate Answer:</i> {ans_text}", body_style))
            elements.append(Spacer(1, 4))

            if eval_obj:
                score_line = (
                    f"<b>Score: {q_score:.1f}/100</b> | "
                    f"Relevance: {eval_obj.get('relevance_score', 0):.0f}% | "
                    f"Technical: {eval_obj.get('technical_score', 0):.0f}% | "
                    f"Completeness: {eval_obj.get('completeness_score', 0):.0f}% | "
                    f"Clarity: {eval_obj.get('clarity_score', 0):.0f}%"
                )
                elements.append(Paragraph(score_line, ParagraphStyle("Rubric", parent=body_style, textColor=colors.HexColor("#4f46e5"))))
                elements.append(Spacer(1, 3))
                critique = eval_obj.get("feedback_critique", "")
                elements.append(Paragraph(f"<b>Feedback:</b> {critique}", body_style))
                elements.append(Spacer(1, 3))
                model_ans = eval_obj.get("model_answer", "")
                if model_ans:
                    elements.append(Paragraph(f"<b>Exemplary Answer:</b> {model_ans}", ParagraphStyle("Model", parent=body_style, textColor=colors.HexColor("#047857"))))

            elements.append(Spacer(1, 10))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceAfter=10))

        # Disclaimer Footer
        elements.append(Spacer(1, 10))
        disclaimer_text = (
            "<b>Disclaimer:</b> This diagnostic report is generated by Resume2Interview AI for educational and interview preparation "
            "purposes. Scores are rubric-based estimates and do not constitute an official employment decision or hiring guarantee."
        )
        elements.append(Paragraph(disclaimer_text, ParagraphStyle("Disc", parent=body_style, fontSize=8, leading=11, textColor=colors.HexColor("#94a3b8"))))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
