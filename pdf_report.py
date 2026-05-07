from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import datetime
import os

def generate_report(alerts_data, shap_image_path=None, output_path="IDS_IoT_Report.pdf"):
    """
    alerts_data : liste de dicts avec keys:
        timestamp, attack_count, total_packets, attack_rate, severity
    shap_image_path : chemin vers shap_plot.png (optionnel)
    output_path : nom du fichier PDF
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    elements = []

    # ── Styles custom ──────────────────────────────────────────
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=10,
        alignment=TA_CENTER
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#e94560'),
        spaceAfter=5,
        alignment=TA_CENTER
    )
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#16213e'),
        spaceBefore=15,
        spaceAfter=8,
        borderPad=5
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=5
    )

    # ── Header ─────────────────────────────────────────────────
    elements.append(Paragraph("🛡️ IDS-IoT — Rapport d'Incidents", title_style))
    elements.append(Paragraph("Système Intelligent de Détection d'Intrusions IoT", subtitle_style))
    elements.append(Paragraph(
        f"Généré le : {datetime.datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}",
        ParagraphStyle('date', parent=styles['Normal'], fontSize=9,
                      textColor=colors.grey, alignment=TA_CENTER)
    ))
    elements.append(Spacer(1, 0.5*cm))

    # ── Ligne séparatrice ───────────────────────────────────────
    elements.append(Table(
        [['']],
        colWidths=[17*cm],
        style=TableStyle([('LINEABOVE', (0,0), (-1,-1), 2, colors.HexColor('#e94560'))])
    ))
    elements.append(Spacer(1, 0.3*cm))

    # ── Résumé exécutif ─────────────────────────────────────────
    elements.append(Paragraph("1. Résumé Exécutif", section_style))

    total_attacks = sum(a['attack_count'] for a in alerts_data)
    total_packets = sum(a['total_packets'] for a in alerts_data)
    high_count = sum(1 for a in alerts_data if a['severity'] == 'HIGH')
    avg_rate = round(sum(a['attack_rate'] for a in alerts_data) / len(alerts_data), 1) if alerts_data else 0

    summary_data = [
        ['Métrique', 'Valeur'],
        ['Nombre total d\'alertes', str(len(alerts_data))],
        ['Total paquets analysés', str(total_packets)],
        ['Total attaques détectées', str(total_attacks)],
        ['Alertes HIGH severity', str(high_count)],
        ['Taux d\'attaque moyen', f'{avg_rate}%'],
    ]

    summary_table = Table(summary_data, colWidths=[9*cm, 8*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#16213e')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 11),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 10),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8f9fa'), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#fff5f5'), colors.white]),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.5*cm))

    # ── Détail des alertes ──────────────────────────────────────
    elements.append(Paragraph("2. Détail des Alertes", section_style))

    alert_data = [['Timestamp', 'Attaques', 'Paquets', 'Taux', 'Sévérité']]
    for a in alerts_data:
        severity_color = '#f85149' if a['severity'] == 'HIGH' else '#d29922'
        alert_data.append([
            str(a['timestamp']),
            str(a['attack_count']),
            str(a['total_packets']),
            f"{a['attack_rate']}%",
            a['severity']
        ])

    alert_table = Table(alert_data, colWidths=[5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
    alert_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#16213e')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#fff5f5'), colors.white]),
    ]))
    elements.append(alert_table)
    elements.append(Spacer(1, 0.5*cm))

    # ── SHAP Plot ───────────────────────────────────────────────
    if shap_image_path and os.path.exists(shap_image_path):
        elements.append(Paragraph("3. Analyse SHAP — Features Déterminantes", section_style))
        elements.append(Paragraph(
            "Le graphique suivant montre les 10 features réseau ayant le plus contribué "
            "à la détection des attaques :",
            normal_style
        ))
        elements.append(Spacer(1, 0.3*cm))
        img = Image(shap_image_path, width=15*cm, height=9*cm)
        elements.append(img)
        elements.append(Spacer(1, 0.3*cm))

    # ── Conclusion ──────────────────────────────────────────────
    elements.append(Paragraph("4. Conclusion", section_style))
    elements.append(Paragraph(
        f"Durant la période analysée, le système IDS-IoT a détecté <b>{len(alerts_data)} alertes</b> "
        f"avec un taux d'attaque moyen de <b>{avg_rate}%</b>. "
        f"Les features réseau les plus discriminantes sont principalement liées au jitter "
        f"inter-hôtes (HH_jit) et aux statistiques de trafic port-à-port (HpHp), "
        f"caractéristiques typiques des attaques botnet et DoS sur réseaux IoT.",
        normal_style
    ))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(
        "— Rapport généré automatiquement par IDS-IoT System | EMSI Casablanca 2026",
        ParagraphStyle('footer', parent=styles['Normal'], fontSize=8,
                      textColor=colors.grey, alignment=TA_CENTER)
    ))

    # ── Build PDF ───────────────────────────────────────────────
    doc.build(elements)
    print(f"✅ PDF généré : {output_path}")
    return output_path


if __name__ == "__main__":
    # Test avec données fictives
    test_alerts = [
        {'timestamp': '2026-05-08 00:01:38', 'attack_count': 927, 'total_packets': 1041, 'attack_rate': 89.0, 'severity': 'HIGH'},
        {'timestamp': '2026-05-08 00:05:58', 'attack_count': 931, 'total_packets': 1038, 'attack_rate': 89.7, 'severity': 'HIGH'},
        {'timestamp': '2026-05-08 00:11:22', 'attack_count': 0,   'total_packets': 48,   'attack_rate': 0.0,  'severity': 'LOW'},
    ]

    generate_report(
        alerts_data=test_alerts,
        shap_image_path="shap_plot.png",
        output_path="IDS_IoT_Report.pdf"
    )