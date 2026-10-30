import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

os.makedirs('overleaf_figures', exist_ok=True)

def create_tier_processing_diagram(filename, title, subtitle, theme_color, bg_color, input_data, steps, verdict_data):
    fig, ax = plt.subplots(figsize=(12, 4.2), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4.2)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    # Header
    ax.text(6.0, 3.85, title, ha='center', va='center', fontsize=12, fontweight='bold', color='#0F172A')
    ax.text(6.0, 3.55, subtitle, ha='center', va='center', fontsize=8.5, fontstyle='italic', color='#475569')

    # Step 1: Input Asset (Left)
    b1 = patches.FancyBboxPatch((0.4, 0.4), 2.5, 2.8, boxstyle="round,pad=0.08",
                               facecolor='#F1F5F9', edgecolor='#94A3B8', linewidth=1.2)
    ax.add_patch(b1)
    ax.text(1.65, 2.9, '1. Ad Ingestion & OCR', ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1E293B')
    ax.text(1.65, 1.6, input_data, ha='center', va='center', fontsize=7.0, color='#334155', linespacing=1.3)

    # Step 2: Extractor Scores (Middle Left)
    b2 = patches.FancyBboxPatch((3.3, 0.4), 2.6, 2.8, boxstyle="round,pad=0.08",
                               facecolor='#EFF6FF', edgecolor='#3B82F6', linewidth=1.2)
    ax.add_patch(b2)
    ax.text(4.6, 2.9, '2. Multimodal Telemetry', ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1D4ED8')
    ax.text(4.6, 1.6, steps[0], ha='center', va='center', fontsize=7.0, color='#1E293B', linespacing=1.3)

    # Step 3: Piecewise & VLM Fusion (Middle Right)
    b3 = patches.FancyBboxPatch((6.3, 0.4), 2.6, 2.8, boxstyle="round,pad=0.08",
                               facecolor='#FEF3C7', edgecolor='#F59E0B', linewidth=1.2)
    ax.add_patch(b3)
    ax.text(7.6, 2.9, '3. Arbitration & Rules', ha='center', va='center', fontsize=8.5, fontweight='bold', color='#B45309')
    ax.text(7.6, 1.6, steps[1], ha='center', va='center', fontsize=7.0, color='#78350F', linespacing=1.3)

    # Step 4: Final Verdict & Action (Right)
    b4 = patches.FancyBboxPatch((9.3, 0.4), 2.4, 2.8, boxstyle="round,pad=0.08",
                               facecolor=bg_color, edgecolor=theme_color, linewidth=1.8)
    ax.add_patch(b4)
    ax.text(10.5, 2.9, '4. Gating Verdict', ha='center', va='center', fontsize=8.5, fontweight='bold', color=theme_color)
    ax.text(10.5, 1.6, verdict_data, ha='center', va='center', fontsize=7.0, fontweight='bold', color=theme_color, linespacing=1.3)

    # Arrows
    arr = dict(arrowstyle='->', lw=1.2, color='#64748B')
    ax.annotate('', xy=(3.3, 1.8), xytext=(2.9, 1.8), arrowprops=arr)
    ax.annotate('', xy=(6.3, 1.8), xytext=(5.9, 1.8), arrowprops=arr)
    ax.annotate('', xy=(9.3, 1.8), xytext=(8.9, 1.8), arrowprops=arr)

    plt.tight_layout()
    plt.savefig(f'overleaf_figures/{filename}', dpi=300, bbox_inches='tight')
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created {filename}")

# 1. SAFE_FOR_ALL Processing Diagram
create_tier_processing_diagram(
    'proc_safe_for_all.png',
    'Processing Pipeline for Category 1: SAFE_FOR_ALL (Universal Audience)',
    'Zero Hazard Detection, Linear Base Formulation, and Unrestricted Programmatic Delivery Gating',
    '#2563EB', '#EFF6FF',
    "Sample Creative:\nGrocery / Educational Ad\n\nOCR Copy:\n'Fresh Honeycrisp Apples\n$1.99/lb Organic Produce'\n\nVisual Elements:\nFresh produce, domestic packaging\nZero nudity, zero weapons",
    ("Visual Risk (V): 0.01\nAdult / NSFW (N): 0.00\nKinetic Motion (D): 0.00\nOCR Toxicity (O): 0.00\nSpeech Risk (A): 0.00\nAdRisk Scam (M): 0.01\n\nLinear Base:\nSw = 0.55 / 100",
     "Prohibited Aggregator:\nP = 100 * max(D, M_scam) = 1.0\n\nAdult Aggregator:\nQ = max(N, M_adult) = 0.01\n\nRule Trigger:\nP < 15.0 and Q < 0.10\nPiecewise S_risk = 0.55\nQwen3-VL: SAFE_FOR_ALL"),
    "POLICY TIER:\nSAFE_FOR_ALL\n\nRisk Index: 0.55 / 100\n\nDISPATCH ACTION:\nUNRESTRICTED\n\nEligible Viewers:\nAll Audiences\n(Including Children <14)\nZero Biometric Gating"
)

# 2. SAFE_14_PLUS Processing Diagram
create_tier_processing_diagram(
    'proc_safe_14_plus.png',
    'Processing Pipeline for Category 2: SAFE_14_PLUS (Adolescent Tier)',
    'Sensory Rhetoric Analysis, Motion Kinetic Energy, and Child-Exclusion Boundary Enforcement',
    '#059669', '#ECFDF5',
    "Sample Creative:\nYouth Sports / Energy Drink\n\nOCR Copy:\n'Titanium Attack Shaft -\nHigh Impact Power - Max Energy'\n\nVisual Elements:\nCompetitive martial arts / lacrosse\nHigh kinetic energy, no weapons",
    ("Visual Risk (V): 0.15\nAdult / NSFW (N): 0.05\nKinetic Motion (D): 0.28\nOCR Toxicity (O): 0.22\nSpeech Risk (A): 0.00\nAdRisk Stimulant (M): 0.12\n\nLinear Base:\nSw = 14.70 / 100",
     "Prohibited Aggregator:\nP = 28.0 (< 35.0, No weapons)\n\nAdult Aggregator:\nQ = 0.05 (< 0.25, No adult)\n\nRule Trigger:\nUK ASA Rule 15.18 /\nIARC Teen (13+) Alignment\nQwen3-VL: SAFE_14_PLUS"),
    "POLICY TIER:\nSAFE_14_PLUS\n\nRisk Index: 14.70 / 100\n\nDISPATCH ACTION:\nAGE GATED (14+)\n\nEligible Viewers:\nAdolescents (14-17)\nVerified Adults (18+)\nBLOCKED: Children (<14)"
)

# 3. SAFE_18_PLUS Processing Diagram
create_tier_processing_diagram(
    'proc_safe_18_plus.png',
    'Processing Pipeline for Category 3: SAFE_18_PLUS (Lawful Adult Content)',
    'Adult Product Keyword Screening, Non-Linear Risk Escalation, and ArcFace Biometric Gating',
    '#D97706', '#FFFBEB',
    "Sample Creative:\nCraft Brewery / Pub Promotion\n\nOCR Copy:\n'Craft Pale Ale - 5.4% ABV -\nServed Cold at The Old Oak Pub'\n\nVisual Elements:\nBeer glassware, bottles, bar venue\nFalcon NSFW: 0.15 (dining)",
    ("Visual Risk (V): 0.35\nAdult / NSFW (N): 0.15\nKinetic Motion (D): 0.00\nOCR Adult (O): 0.80\nSpeech Risk (A): 0.00\nExplicit Alcohol (M): 0.85\n\nLinear Base:\nSw = 26.25 / 100",
     "Adult Evidence Aggregator:\nQ = max(0.15, 0.85, 0.80) = 0.85\n\nPiecewise Escalation:\nBecause Q >= 0.25:\nS_risk = min(65, 70 * 0.85)\nS_risk = 59.50 / 100\nRule 2 Concordance: S18"),
    "POLICY TIER:\nSAFE_18_PLUS\n\nRisk Index: 59.50 / 100\n\nDISPATCH ACTION:\nMANDATORY GATING\n\nEligible Viewers:\nVerified Adults (>= 18)\nRequires ArcFace Match\nBLOCKED: All Minors (<18)"
)

# 4. UNSAFE_FOR_ALL Processing Diagram
create_tier_processing_diagram(
    'proc_unsafe_for_all.png',
    'Processing Pipeline for Category 4: UNSAFE_FOR_ALL (Universally Prohibited)',
    'Deception Detection, Piecewise Threat Escalation, and Zero-Tolerance Safety Veto Rejection',
    '#DC2626', '#FEF2F2',
    "Sample Creative:\nDeceptive Financial Ponzi Scheme\n\nOCR Copy:\n'Deposit $500 - Get $1000 in\n24 Hours Guaranteed Risk-Free'\n\nVisual Elements:\nBundles of cash, luxury signifiers\nDeceptive marketing patterns",
    ("Visual Risk (V): 0.40\nAdult / NSFW (N): 0.10\nKinetic Motion (D): 0.00\nOCR Scam (O): 0.92\nFTC Deception (M_scam): 0.95\nUnsubstantiated Returns: 0.90\n\nLinear Base:\nSw = 37.30 / 100",
     "Prohibited Aggregator:\nP = 100 * max(0.95, 0.92) = 95.0\n\nEmergency Escalation:\nBecause P >= 50.0:\nS_risk = min(100, max(Sw, 95))\nS_risk = 95.00 / 100\nRule 1 Safety Veto: Triggered"),
    "POLICY TIER:\nUNSAFE_FOR_ALL\n\nRisk Index: 95.00 / 100\n\nDISPATCH ACTION:\nIMMEDIATELY REJECTED\n\nPublication Blocked:\nPermanent Pre-Pub Veto\nZero Delivery to Any User\nAudit Manifest Logged"
)

# Also update overleaf_figures.zip
import zipfile, glob
fig_files = glob.glob('overleaf_figures/*')
with zipfile.ZipFile('overleaf_figures.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    for f in sorted(fig_files):
        zipf.write(f, os.path.basename(f))

print(f"Updated overleaf_figures.zip: {os.path.getsize('overleaf_figures.zip'):,} bytes across {len(fig_files)} figures.")
