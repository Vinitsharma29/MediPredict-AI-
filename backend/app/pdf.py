from __future__ import annotations

from io import BytesIO
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


def build_pdf(patient: dict[str, Any], prediction: dict[str, Any]) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    y = height - 2 * cm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, y, "MediPredict AI - Clinical Risk Report")

    y -= 1.2 * cm
    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, y, f"Patient: {patient.get('name','')} | Age: {patient.get('age','')} | Gender: {patient.get('gender','')}")

    y -= 0.9 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "AI Prediction")

    y -= 0.6 * cm
    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, y, f"Disease: {prediction.get('disease')} | Risk: {prediction.get('risk_level')} | Probability: {prediction.get('probability'):.1%}")

    y -= 0.9 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Top Risk Drivers (Explainable AI)")

    y -= 0.6 * cm
    c.setFont("Helvetica", 10)
    tops = (prediction.get("feature_importance") or {}).get("top") or []
    for item in tops[:10]:
        c.drawString(2 * cm, y, f"- {item.get('feature')}: value={item.get('value')}, impact={item.get('shap'):+.3f}")
        y -= 0.45 * cm
        if y < 2.5 * cm:
            c.showPage()
            y = height - 2 * cm
            c.setFont("Helvetica", 10)

    y -= 0.4 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Recommendations")
    y -= 0.6 * cm
    c.setFont("Helvetica", 10)
    rec = prediction.get("recommendations") or {}
    for label, values in (
        ("Suggested tests", rec.get("suggested_tests") or []),
        ("Suggested specialists", rec.get("suggested_specialists") or []),
        ("Lifestyle tips", rec.get("lifestyle_tips") or []),
    ):
        c.drawString(2 * cm, y, f"{label}:")
        y -= 0.45 * cm
        for v in values[:10]:
            c.drawString(2.5 * cm, y, f"• {v}")
            y -= 0.4 * cm
            if y < 2.5 * cm:
                c.showPage()
                y = height - 2 * cm
                c.setFont("Helvetica", 10)

    y -= 0.2 * cm
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(2 * cm, y, rec.get("disclaimer") or "")

    c.showPage()
    c.save()
<<<<<<< HEAD
    return buf.getvalue()
=======
    return buf.getvalue()
>>>>>>> 37f8f4a638f6f6a45437c6c153e45685cab00099
