#!/usr/bin/env python3
"""
JARVIS Voice-Note to Invoice Engine — As Featured in the Iron Man JARVIS Demo.
Parses natural conversational voice notes or text prompts and automatically generates
publication-ready PDF & HTML invoices with line-item breakdowns, tax calculations, and branding.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
sys.path.insert(0, str(JARVIS_DIR / "core"))
INVOICE_DIR = JARVIS_DIR / "invoices"
INVOICE_DIR.mkdir(parents=True, exist_ok=True)

OPENROUTER_API_KEY = os.environ.get(
    "OPENROUTER_API_KEY",
    "REDACTED_API_KEY"
)


class JarvisInvoiceEngine:
    def __init__(self, company_name: str = "JARVIS AI Automations", currency: str = "$"):
        self.company_name = company_name
        self.currency = currency

    def parse_invoice_prompt(self, prompt: str) -> Dict[str, Any]:
        """Use LLM reasoning to parse unstructured voice note / prompt into structured invoice JSON."""
        system_prompt = (
            "You are JARVIS Financial Operations AI. Extract structured invoice data from the user's conversational voice note or text.\n"
            "CRITICAL: Always extract explicit dollar amounts from the prompt and assign them to the item's 'rate' and 'amount' fields (e.g., '$5,000' -> 5000.0).\n"
            "Return ONLY valid JSON matching this schema:\n"
            "{\n"
            '  "invoice_number": "INV-YYYYMMDD-001",\n'
            '  "client_name": "string",\n'
            '  "client_email": "string or empty",\n'
            '  "issue_date": "YYYY-MM-DD",\n'
            '  "due_date": "YYYY-MM-DD",\n'
            '  "items": [\n'
            '    {\n'
            '      "description": "Item description",\n'
            '      "quantity": 1,\n'
            '      "rate": 5000.00,\n'
            '      "amount": 5000.00\n'
            '    }\n'
            '  ],\n'
            '  "subtotal": 5000.00,\n'
            '  "tax_percent": 0.0,\n'
            '  "tax_amount": 0.0,\n'
            '  "total_amount": 5000.00,\n'
            '  "notes": "Payment terms and thank you message"\n'
            "}"
        )

        today_str = datetime.date.today().isoformat()
        inv_id = f"INV-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            }
            body = {
                "model": "google/gemma-4-26b-a4b-it:free",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Today is {today_str}. Default Invoice ID is {inv_id}.\nParse this invoice request: '{prompt}'"}
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }

            req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                
                # Extract JSON
                if "{" in content and "}" in content:
                    json_str = content[content.find("{"):content.rfind("}")+1]
                    parsed = json.loads(json_str)
                    return self._normalize_invoice(parsed, inv_id, today_str, prompt)
        except Exception as e:
            print(f"[!] Online parser error: {e}. Using regex fallback.")

        return self._regex_fallback_parser(prompt, inv_id, today_str)

    def _normalize_invoice(self, data: Dict[str, Any], default_id: str, today_str: str, original_prompt: str = "") -> Dict[str, Any]:
        data.setdefault("invoice_number", default_id)
        data.setdefault("issue_date", today_str)
        data.setdefault("client_name", "Valued Client")
        data.setdefault("client_email", "")
        
        # Calculate totals
        items = data.get("items", [])
        if not items:
            items = [{"description": "Professional Consulting & AI Automation", "quantity": 1, "rate": 500.0, "amount": 500.0}]
            data["items"] = items

        # Fallback price extraction if 0 or default
        prompt_amounts = re.findall(r"(?:\$|USD\s*)(\d[\d,]*(?:\.\d{2})?)", original_prompt)
        if not prompt_amounts:
            prompt_amounts = re.findall(r"\b(\d{2,}[\d,]*(?:\.\d{2})?)\b", original_prompt)
        extracted_amount = float(prompt_amounts[0].replace(",", "")) if prompt_amounts else None

        for it in items:
            q = float(it.get("quantity", 1))
            r = float(it.get("rate", 0))
            a = float(it.get("amount", 0))
            
            if extracted_amount is not None and len(items) == 1:
                r = extracted_amount
                a = r * q
            elif r == 0 and a == 0:
                r = extracted_amount if extracted_amount is not None else 500.0
                a = r * q
            elif a == 0:
                a = r * q
            it["rate"] = r
            it["amount"] = a

        subtotal = sum(float(it.get("amount", 0)) for it in items)
        tax_pct = float(data.get("tax_percent", 0.0))
        tax_amt = round(subtotal * (tax_pct / 100.0), 2)
        total = round(subtotal + tax_amt, 2)

        data["subtotal"] = subtotal
        data["tax_amount"] = tax_amt
        data["total_amount"] = total
        data.setdefault("notes", "Thank you for your business! Payment is due within 14 days.")
        return data

    def _regex_fallback_parser(self, prompt: str, inv_id: str, today_str: str) -> Dict[str, Any]:
        prompt_amounts = re.findall(r"(?:\$|USD\s*)(\d[\d,]*(?:\.\d{2})?)", prompt)
        if not prompt_amounts:
            prompt_amounts = re.findall(r"\b(\d{2,}[\d,]*(?:\.\d{2})?)\b", prompt)
        amount = float(prompt_amounts[0].replace(",", "")) if prompt_amounts else 500.0

        client = "Valued Client"
        client_match = re.search(r"(?:bill|invoice|to)\s+([^,$0-9]+?)(?:\s+(?:for|\$|due|amount|\bnet\b)|\s*,|\.|$)", prompt, re.IGNORECASE)
        if client_match:
            client = client_match.group(1).strip()

        desc = "AI Automation & Consulting Services"
        desc_match = re.search(r"(?:for)\s+([^,]+?)(?:\s+(?:due|\bnet\b|\$)|,|$)", prompt, re.IGNORECASE)
        if desc_match:
            desc = desc_match.group(1).strip()

        due = (datetime.date.today() + datetime.timedelta(days=14)).isoformat()

        return {
            "invoice_number": inv_id,
            "client_name": client,
            "client_email": "",
            "issue_date": today_str,
            "due_date": due,
            "items": [
                {
                    "description": desc,
                    "quantity": 1,
                    "rate": amount,
                    "amount": amount
                }
            ],
            "subtotal": amount,
            "tax_percent": 0.0,
            "tax_amount": 0.0,
            "total_amount": amount,
            "notes": "Generated by JARVIS Autonomous Assistant. Net 14 payment terms."
        }

    def generate_pdf(self, invoice_data: Dict[str, Any], filename: Optional[str] = None) -> Path:
        """Generate a sleek, modern, professional PDF invoice via reportlab."""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

        if not filename:
            safe_client = re.sub(r"[^a-zA-Z0-9_-]", "_", invoice_data.get("client_name", "client"))
            filename = f"Invoice_{invoice_data['invoice_number']}_{safe_client}.pdf"

        pdf_path = INVOICE_DIR / filename
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "InvoiceTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=28,
            textColor=colors.HexColor("#0f172a")
        )
        subtitle_style = ParagraphStyle(
            "InvoiceSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            textColor=colors.HexColor("#64748b")
        )
        header_bold = ParagraphStyle(
            "HeaderBold",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=colors.HexColor("#0f172a")
        )
        cell_style = ParagraphStyle(
            "CellNormal",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            textColor=colors.HexColor("#334155")
        )

        elements = []

        # 1. Header Banner
        header_data = [
            [
                Paragraph(f"<b>{self.company_name}</b><br/><font color='#64748b'>Autonomous AI Operations & Creative Engine</font>", title_style),
                Paragraph(f"<b>INVOICE</b><br/><font color='#0284c7'>#{invoice_data['invoice_number']}</font>", ParagraphStyle("RightTitle", parent=title_style, alignment=2))
            ]
        ]
        t_header = Table(header_data, colWidths=[3.8 * inch, 3.4 * inch])
        t_header.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        elements.append(t_header)
        elements.append(Spacer(1, 15))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0"), spaceAfter=15))

        # 2. Billed To & Invoice Metadata
        meta_data = [
            [
                Paragraph(f"<b>BILLED TO:</b><br/><b>{invoice_data.get('client_name', 'Valued Client')}</b><br/>{invoice_data.get('client_email', '')}", cell_style),
                Paragraph(f"<b>Invoice Date:</b> {invoice_data.get('issue_date', '')}<br/><b>Due Date:</b> {invoice_data.get('due_date', '')}<br/><b>Status:</b> <font color='#16a34a'><b>DUE UPON RECEIPT</b></font>", cell_style)
            ]
        ]
        t_meta = Table(meta_data, colWidths=[3.8 * inch, 3.4 * inch])
        t_meta.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(t_meta)
        elements.append(Spacer(1, 20))

        # 3. Itemized Table
        table_rows = [
            [
                Paragraph("<b>DESCRIPTION</b>", header_bold),
                Paragraph("<b>QTY</b>", ParagraphStyle("HRight", parent=header_bold, alignment=2)),
                Paragraph("<b>RATE</b>", ParagraphStyle("HRight", parent=header_bold, alignment=2)),
                Paragraph("<b>AMOUNT</b>", ParagraphStyle("HRight", parent=header_bold, alignment=2)),
            ]
        ]

        for it in invoice_data.get("items", []):
            desc = it.get("description", "Service")
            qty = it.get("quantity", 1)
            rate = float(it.get("rate", 0))
            amount = float(it.get("amount", rate * qty))
            table_rows.append([
                Paragraph(desc, cell_style),
                Paragraph(str(qty), ParagraphStyle("CRight", parent=cell_style, alignment=2)),
                Paragraph(f"{self.currency}{rate:,.2f}", ParagraphStyle("CRight", parent=cell_style, alignment=2)),
                Paragraph(f"<b>{self.currency}{amount:,.2f}</b>", ParagraphStyle("CRight", parent=cell_style, alignment=2)),
            ])

        # Subtotal, Tax, Total Rows
        table_rows.append([
            "", "", Paragraph("<b>Subtotal:</b>", ParagraphStyle("Right", parent=cell_style, alignment=2)),
            Paragraph(f"{self.currency}{invoice_data.get('subtotal', 0):,.2f}", ParagraphStyle("Right", parent=cell_style, alignment=2))
        ])
        if invoice_data.get("tax_amount", 0) > 0:
            table_rows.append([
                "", "", Paragraph(f"<b>Tax ({invoice_data.get('tax_percent', 0)}%):</b>", ParagraphStyle("Right", parent=cell_style, alignment=2)),
                Paragraph(f"{self.currency}{invoice_data.get('tax_amount', 0):,.2f}", ParagraphStyle("Right", parent=cell_style, alignment=2))
            ])
        table_rows.append([
            "", "", Paragraph("<b>TOTAL DUE:</b>", ParagraphStyle("TotalDue", parent=header_bold, fontSize=12, alignment=2, textColor=colors.HexColor("#0284c7"))),
            Paragraph(f"<b>{self.currency}{invoice_data.get('total_amount', 0):,.2f}</b>", ParagraphStyle("TotalAmt", parent=header_bold, fontSize=12, alignment=2, textColor=colors.HexColor("#0284c7")))
        ])

        t_items = Table(table_rows, colWidths=[4.2 * inch, 0.8 * inch, 1.1 * inch, 1.1 * inch])
        t_items.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -4), 0.5, colors.HexColor("#cbd5e1")),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor("#0284c7")),
            ('LINEBELOW', (2, -1), (3, -1), 1.5, colors.HexColor("#0284c7")),
        ]))
        elements.append(t_items)
        elements.append(Spacer(1, 25))

        # 4. Payment Notes
        notes_text = f"<b>Notes & Payment Instructions:</b><br/>{invoice_data.get('notes', '')}"
        elements.append(Paragraph(notes_text, subtitle_style))

        doc.build(elements)
        return pdf_path

    def generate_html(self, invoice_data: Dict[str, Any], filename: Optional[str] = None) -> Path:
        """Generate interactive HTML invoice."""
        if not filename:
            safe_client = re.sub(r"[^a-zA-Z0-9_-]", "_", invoice_data.get("client_name", "client"))
            filename = f"Invoice_{invoice_data['invoice_number']}_{safe_client}.html"

        html_path = INVOICE_DIR / filename
        
        items_html = ""
        for it in invoice_data.get("items", []):
            items_html += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #334155;">{it.get('description', '')}</td>
                <td style="padding: 12px; text-align: center; border-bottom: 1px solid #334155;">{it.get('quantity', 1)}</td>
                <td style="padding: 12px; text-align: right; border-bottom: 1px solid #334155;">{self.currency}{it.get('rate', 0):,.2f}</td>
                <td style="padding: 12px; text-align: right; font-weight: bold; border-bottom: 1px solid #334155;">{self.currency}{it.get('amount', 0):,.2f}</td>
            </tr>
            """

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Invoice {invoice_data['invoice_number']} - {invoice_data['client_name']}</title>
    <style>
        body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 40px 20px; }}
        .invoice-card {{ max-width: 800px; margin: auto; background: #1e293b; border-radius: 16px; border: 1px solid #334155; padding: 40px; box-shadow: 0 20px 40px rgba(0,0,0,0.5); }}
        .header {{ display: flex; justify-content: space-between; border-bottom: 1px solid #334155; padding-bottom: 24px; }}
        .brand h1 {{ margin: 0; color: #38bdf8; font-size: 28px; }}
        .meta {{ display: flex; justify-content: space-between; margin-top: 24px; background: #0f172a; padding: 20px; border-radius: 12px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 30px; }}
        th {{ background: #0f172a; color: #38bdf8; padding: 12px; text-align: left; }}
        .totals {{ margin-top: 24px; text-align: right; font-size: 18px; }}
        .total-highlight {{ color: #38bdf8; font-size: 24px; font-weight: bold; }}
        .btn {{ display: inline-block; background: #0284c7; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 20px; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="invoice-card">
        <div class="header">
            <div class="brand">
                <h1>{self.company_name}</h1>
                <p style="color: #94a3b8; margin: 4px 0 0 0;">Autonomous AI Operations & Growth Engineering</p>
            </div>
            <div style="text-align: right;">
                <h2 style="margin: 0; color: #38bdf8;">INVOICE</h2>
                <p style="color: #94a3b8; margin: 4px 0 0 0;">#{invoice_data['invoice_number']}</p>
            </div>
        </div>

        <div class="meta">
            <div>
                <p style="color: #94a3b8; margin: 0 0 4px 0; font-size: 12px;">BILLED TO</p>
                <h3 style="margin: 0;">{invoice_data['client_name']}</h3>
                <p style="color: #94a3b8; margin: 4px 0 0 0;">{invoice_data['client_email']}</p>
            </div>
            <div style="text-align: right;">
                <p style="color: #94a3b8; margin: 0; font-size: 14px;"><strong>Issue Date:</strong> {invoice_data['issue_date']}</p>
                <p style="color: #94a3b8; margin: 4px 0 0 0; font-size: 14px;"><strong>Due Date:</strong> {invoice_data['due_date']}</p>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>DESCRIPTION</th>
                    <th style="text-align: center;">QTY</th>
                    <th style="text-align: right;">RATE</th>
                    <th style="text-align: right;">AMOUNT</th>
                </tr>
            </thead>
            <tbody>
                {items_html}
            </tbody>
        </table>

        <div class="totals">
            <p style="margin: 4px 0; color: #94a3b8;">Subtotal: {self.currency}{invoice_data['subtotal']:,.2f}</p>
            <p style="margin: 4px 0; color: #94a3b8;">Tax: {self.currency}{invoice_data['tax_amount']:,.2f}</p>
            <p class="total-highlight">TOTAL DUE: {self.currency}{invoice_data['total_amount']:,.2f}</p>
        </div>

        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #334155; color: #94a3b8; font-size: 13px;">
            <p><strong>Payment Terms:</strong> {invoice_data['notes']}</p>
        </div>

        <div style="text-align: center;">
            <button class="btn" onclick="window.print()">Print / Export PDF</button>
        </div>
    </div>
</body>
</html>
"""
        html_path.write_text(html_content, encoding="utf-8")
        return html_path

    def process_voice_note_to_invoice(self, voice_prompt: str) -> Dict[str, Any]:
        """Complete workflow: Conversational note -> Structured JSON -> PDF -> HTML."""
        from jarvis_voice import get_voice
        voice = get_voice()

        voice.speak("Processing your invoice details, sir.")
        data = self.parse_invoice_prompt(voice_prompt)

        pdf_path = self.generate_pdf(data)
        html_path = self.generate_html(data)

        msg = f"Invoice generated for {data['client_name']} totaling {self.currency}{data['total_amount']:,.2f}."
        voice.speak(msg)
        print(f"[+] Invoice PDF: {pdf_path}")
        print(f"[+] Invoice HTML: {html_path}")

        return {
            "invoice_data": data,
            "pdf_path": str(pdf_path),
            "html_path": str(html_path)
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JARVIS Voice-Note to Invoice Generator")
    parser.add_argument("--prompt", type=str, default="Bill Stark Enterprises $3,500 for autonomous AI copilot installation and system hardening, due in 14 days")
    args = parser.parse_args()

    engine = JarvisInvoiceEngine()
    res = engine.process_voice_note_to_invoice(args.prompt)
    print(json.dumps(res["invoice_data"], indent=2))
