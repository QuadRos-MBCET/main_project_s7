"""
Academic Diagram Generator: UML & Data Flow Diagrams (DFDs)
SAFE-VISION (SafeAd AI) Trust and Safety Framework
Standard IEEE / Computer Science Academic Notations
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle

# Styling constants
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

COLOR_NAVY = '#1E3A8A'
COLOR_NAVY_LIGHT = '#EFF6FF'
COLOR_BORDER_BLUE = '#3B82F6'

COLOR_SLATE = '#334155'
COLOR_SLATE_LIGHT = '#F8FAFC'
COLOR_BORDER_SLATE = '#94A3B8'

COLOR_TEAL = '#0F766E'
COLOR_TEAL_LIGHT = '#F0FDFA'
COLOR_BORDER_TEAL = '#14B8A6'

COLOR_AMBER = '#B45309'
COLOR_AMBER_LIGHT = '#FFFBEB'
COLOR_BORDER_AMBER = '#F59E0B'

COLOR_RED = '#B91C1C'
COLOR_RED_LIGHT = '#FEF2F2'
COLOR_BORDER_RED = '#EF4444'

TEXT_DARK = '#0F172A'
TEXT_MUTED = '#475569'

def draw_arrow(ax, x1, y1, x2, y2, label="", color='#475569', lw=1.2, label_color=TEXT_MUTED, label_size=7.5, rad=0.0):
    """Draw clean directed arrow with connectionstyle."""
    conn = f"arc3,rad={rad}" if rad != 0.0 else "arc3,rad=0.0"
    arrow = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>',
                            connectionstyle=conn,
                            mutation_scale=12, color=color, linewidth=lw)
    ax.add_patch(arrow)
    if label:
        mx, my = (x1 + x2) * 0.5, (y1 + y2) * 0.5
        ax.text(mx, my + 0.12, label, ha='center', va='bottom',
                fontsize=label_size, color=label_color,
                bbox=dict(boxstyle='square,pad=0.1', facecolor='#FFFFFF', edgecolor='none', alpha=0.9))

# ==============================================================================
# 1. DATA FLOW DIAGRAM LEVEL 0 (CONTEXT DIAGRAM)
# ==============================================================================
def create_dfd_level_0(out_dir):
    fig, ax = plt.subplots(figsize=(14, 8.5), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8.5)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    # Header
    ax.text(7.0, 8.0, 'Data Flow Diagram (Level 0): SafeAd AI Context Diagram',
            ha='center', va='center', fontsize=13, fontweight='bold', color=COLOR_NAVY)

    # External Entity 1: Advertiser (Left)
    ent1 = FancyBboxPatch((0.6, 3.4), 2.4, 1.8, boxstyle="square,pad=0.1",
                          facecolor=COLOR_SLATE_LIGHT, edgecolor=COLOR_SLATE, linewidth=1.5)
    ax.add_patch(ent1)
    ax.text(1.8, 4.5, 'ADVERTISER', ha='center', va='center', fontsize=10, fontweight='bold', color=COLOR_NAVY)
    ax.text(1.8, 3.9, 'Commercial Client\nCampaign Creator', ha='center', va='center', fontsize=7.5, color=TEXT_MUTED)

    # External Entity 2: Social User / Viewer (Right)
    ent2 = FancyBboxPatch((11.0, 3.4), 2.4, 1.8, boxstyle="square,pad=0.1",
                          facecolor=COLOR_SLATE_LIGHT, edgecolor=COLOR_SLATE, linewidth=1.5)
    ax.add_patch(ent2)
    ax.text(12.2, 4.5, 'SOCIAL USER', ha='center', va='center', fontsize=10, fontweight='bold', color=COLOR_NAVY)
    ax.text(12.2, 3.9, 'Audience / Viewer\nBiometric Client', ha='center', va='center', fontsize=7.5, color=TEXT_MUTED)

    # External Entity 3: Platform Admin / Compliance Auditor (Top)
    ent3 = FancyBboxPatch((5.4, 6.0), 3.2, 1.6, boxstyle="square,pad=0.1",
                          facecolor=COLOR_SLATE_LIGHT, edgecolor=COLOR_SLATE, linewidth=1.5)
    ax.add_patch(ent3)
    ax.text(7.0, 7.0, 'PLATFORM AUDITOR', ha='center', va='center', fontsize=10, fontweight='bold', color=COLOR_NAVY)
    ax.text(7.0, 6.4, 'Compliance Officer\nPolicy Governance', ha='center', va='center', fontsize=7.5, color=TEXT_MUTED)

    # Central System Process (Circle / Ellipse representation for DFD)
    proc_circle = patches.Ellipse((7.0, 3.6), 4.2, 2.6,
                                  facecolor=COLOR_NAVY_LIGHT, edgecolor=COLOR_BORDER_BLUE, linewidth=2.0)
    ax.add_patch(proc_circle)
    ax.text(7.0, 4.1, '0', ha='center', va='center', fontsize=12, fontweight='bold', color=COLOR_NAVY)
    ax.plot([5.3, 8.7], [3.85, 3.85], color=COLOR_BORDER_BLUE, linewidth=1.0)
    ax.text(7.0, 3.35, 'SafeAd AI System\nMultimodal Moderation &\nBiometric Age Assurance',
            ha='center', va='center', fontsize=9.0, fontweight='bold', color=TEXT_DARK)

    # Data flows between Advertiser and System
    draw_arrow(ax, 3.0, 4.5, 4.9, 4.1, label='Ad Creative & Metadata', rad=0.08)
    draw_arrow(ax, 4.9, 3.2, 3.0, 3.6, label='Moderation Verdict & Risk', rad=0.08)

    # Data flows between Social User and System
    draw_arrow(ax, 11.0, 4.4, 9.1, 4.0, label='Webcam Live & ID Card', rad=-0.08)
    draw_arrow(ax, 9.1, 3.2, 11.0, 3.6, label='Age-Appropriate Feed', rad=-0.08)

    # Data flows between Platform Admin and System
    draw_arrow(ax, 6.5, 6.0, 6.5, 4.9, label='Policy Rules')
    draw_arrow(ax, 7.5, 4.9, 7.5, 6.0, label='Audit Logs & Queue')

    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, 'dfd_level_0.png'), dpi=300, bbox_inches='tight')
    fig.savefig(os.path.join(out_dir, 'dfd_level_0.svg'), bbox_inches='tight')
    plt.close(fig)
    print("Exported dfd_level_0.png & .svg")

# ==============================================================================
# 2. DATA FLOW DIAGRAM LEVEL 1 (PROCESS DECOMPOSITION)
# ==============================================================================
def create_dfd_level_1(out_dir):
    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    # Title
    ax.text(8.0, 9.5, 'Data Flow Diagram (Level 1): Detailed Process Flow & Data Stores',
            ha='center', va='center', fontsize=13, fontweight='bold', color=COLOR_NAVY)

    # Data Store helper (parallel lines)
    def draw_datastore(x, y, w, h, id_str, name):
        ax.plot([x, x+w], [y+h, y+h], color=COLOR_SLATE, lw=1.5)
        ax.plot([x, x+w], [y, y], color=COLOR_SLATE, lw=1.5)
        ax.fill_between([x, x+w], y, y+h, color='#F8FAFC')
        ax.plot([x+0.6, x+0.6], [y, y+h], color=COLOR_SLATE, lw=1.0)
        ax.text(x+0.3, y+h*0.5, id_str, ha='center', va='center', fontsize=8, fontweight='bold', color=COLOR_SLATE)
        ax.text(x+0.6+(w-0.6)*0.5, y+h*0.5, name, ha='center', va='center', fontsize=8, fontweight='bold', color=TEXT_DARK)

    # DFD Process helper (rounded rectangle / oval)
    def draw_process(x, y, w, h, num, name, sub=""):
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15",
                              facecolor=COLOR_NAVY_LIGHT, edgecolor=COLOR_BORDER_BLUE, lw=1.5)
        ax.add_patch(rect)
        ax.text(x+w*0.5, y+h*0.75, f"({num}) {name}", ha='center', va='center',
                fontsize=8.5, fontweight='bold', color=COLOR_NAVY)
        if sub:
            ax.text(x+w*0.5, y+h*0.35, sub, ha='center', va='center', fontsize=7.2, color=TEXT_MUTED)

    # External Entities
    # Advertiser (Left)
    ax.add_patch(Rectangle((0.4, 7.0), 2.2, 1.4, facecolor=COLOR_SLATE_LIGHT, edgecolor=COLOR_SLATE, lw=1.2))
    ax.text(1.5, 7.9, 'ADVERTISER', ha='center', va='center', fontsize=9, fontweight='bold', color=COLOR_NAVY)
    ax.text(1.5, 7.4, 'Campaign Submission', ha='center', va='center', fontsize=7.5, color=TEXT_MUTED)

    # Platform Auditor (Top Right)
    ax.add_patch(Rectangle((13.4, 7.4), 2.2, 1.4, facecolor=COLOR_SLATE_LIGHT, edgecolor=COLOR_SLATE, lw=1.2))
    ax.text(14.5, 8.3, 'AUDITOR', ha='center', va='center', fontsize=9, fontweight='bold', color=COLOR_NAVY)
    ax.text(14.5, 7.8, 'Compliance Admin', ha='center', va='center', fontsize=7.5, color=TEXT_MUTED)

    # Social User (Bottom Left)
    ax.add_patch(Rectangle((0.4, 1.6), 2.2, 1.4, facecolor=COLOR_SLATE_LIGHT, edgecolor=COLOR_SLATE, lw=1.2))
    ax.text(1.5, 2.5, 'SOCIAL USER', ha='center', va='center', fontsize=9, fontweight='bold', color=COLOR_NAVY)
    ax.text(1.5, 2.0, 'Ad Feed Client', ha='center', va='center', fontsize=7.5, color=TEXT_MUTED)

    # Processes
    draw_process(3.4, 7.0, 2.6, 1.4, "1.0", "Media Preprocessing", "Keyframes & Audio Resample")
    draw_process(6.8, 7.0, 2.6, 1.4, "2.0", "Feature Extraction", "OCR, Whisper, VideoMAE, NSFW")
    draw_process(10.2, 7.0, 2.6, 1.4, "3.0", "Policy Arbitration", "Strategy D Fusion & Veto")

    draw_process(3.4, 1.6, 2.6, 1.4, "4.0", "Biometric Verification", "MTCNN, ArcFace & MiniFASNet")
    draw_process(6.8, 1.6, 2.6, 1.4, "5.0", "Demographic Assurance", "ViT Age & ID OCR DOB")
    draw_process(10.2, 1.6, 2.6, 1.4, "6.0", "Delivery Dispatching", "Age-Aware Policy Gating")

    # Data Stores (Middle Band)
    draw_datastore(4.0, 4.5, 3.4, 0.9, "D1", "Ads & Metadata DB")
    draw_datastore(8.4, 4.5, 3.4, 0.9, "D2", "Policy Rules Index")
    draw_datastore(12.4, 4.5, 3.2, 0.9, "D3", "Immutable Audit Store")

    # Data flow connections
    draw_arrow(ax, 2.6, 7.7, 3.4, 7.7, label='Raw Ad Media')
    draw_arrow(ax, 6.0, 7.7, 6.8, 7.7, label='Keyframes')
    draw_arrow(ax, 9.4, 7.7, 10.2, 7.7, label='Detector Vectors')

    draw_arrow(ax, 11.5, 7.0, 11.5, 5.4, label='Verdict')
    draw_arrow(ax, 11.5, 5.4, 12.4, 5.0, label='Log Record')
    draw_arrow(ax, 14.0, 5.4, 14.5, 7.4, label='Review Queue')

    draw_arrow(ax, 5.7, 7.0, 5.7, 5.4, label='Store Media')
    draw_arrow(ax, 10.1, 5.4, 10.5, 7.0, label='Rules')

    draw_arrow(ax, 2.6, 2.3, 3.4, 2.3, label='Webcam/ID')
    draw_arrow(ax, 6.0, 2.3, 6.8, 2.3, label='Face Crop')
    draw_arrow(ax, 9.4, 2.3, 10.2, 2.3, label='Age Bracket')

    # Moderation decision to Delivery Dispatching
    draw_arrow(ax, 11.5, 7.0, 11.5, 3.0, label='Statutory Classification', color=COLOR_RED, lw=1.4, label_color=COLOR_RED)
    draw_arrow(ax, 11.5, 1.6, 2.6, 1.8, label='Filtered Ad Delivery', rad=-0.12)

    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, 'dfd_level_1.png'), dpi=300, bbox_inches='tight')
    fig.savefig(os.path.join(out_dir, 'dfd_level_1.svg'), bbox_inches='tight')
    plt.close(fig)
    print("Exported dfd_level_1.png & .svg")

# ==============================================================================
# 3. UML CLASS DIAGRAM
# ==============================================================================
def create_class_diagram(out_dir):
    fig, ax = plt.subplots(figsize=(16, 9.5), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9.5)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    # Header
    ax.text(8.0, 9.15, 'UML Class Diagram: SafeAd AI Object-Oriented Architecture',
            ha='center', va='center', fontsize=13, fontweight='bold', color=COLOR_NAVY)

    def draw_uml_class(x, y, w, h, name, attrs, methods):
        # Class Box
        rect = Rectangle((x, y), w, h, facecolor='#FFFFFF', edgecolor=COLOR_SLATE, lw=1.2)
        ax.add_patch(rect)
        # Header banner
        header_h = 0.55
        h_rect = Rectangle((x, y+h-header_h), w, header_h, facecolor=COLOR_NAVY_LIGHT, edgecolor=COLOR_SLATE, lw=1.0)
        ax.add_patch(h_rect)
        ax.text(x+w*0.5, y+h-header_h*0.5, name, ha='center', va='center',
                fontsize=8.5, fontweight='bold', color=COLOR_NAVY)

        # Attributes section
        attr_y = y + h - header_h - 0.25
        for a in attrs:
            ax.text(x+0.15, attr_y, a, ha='left', va='center', fontsize=7.0, color=TEXT_DARK)
            attr_y -= 0.22

        # Divider line
        div_y = y + h - header_h - len(attrs)*0.22 - 0.15
        ax.plot([x, x+w], [div_y, div_y], color=COLOR_SLATE, lw=0.8)

        # Methods section
        meth_y = div_y - 0.2
        for m in methods:
            ax.text(x+0.15, meth_y, m, ha='left', va='center', fontsize=7.0, color=TEXT_DARK)
            meth_y -= 0.22

    # Class 1: AdAsset
    draw_uml_class(0.6, 5.4, 3.2, 3.2, "AdAsset",
                   attrs=["- ad_id: str", "- media_path: str", "- is_video: bool", "- keyframes: List[Image]", "- text_ocr: str", "- audio_pcm: ndarray"],
                   methods=["+ extract_keyframes()", "+ run_clahe_ocr()", "+ transcribe_audio()", "+ get_duration(): float"])

    # Class 2: DetectorEngine
    draw_uml_class(4.6, 5.4, 3.4, 3.2, "DetectorEngine",
                   attrs=["- nsfw_model: FalconViT", "- motion_model: VideoMAE", "- ocr_model: EasyOCR", "- asr_model: Whisper", "- nlp_model: DeBERTa"],
                   methods=["+ infer_visual_safety()", "+ infer_video_kinetics()", "+ infer_speech_toxicity()", "+ extract_33d_vector(): ndarray"])

    # Class 3: RandomForestFusion
    draw_uml_class(9.0, 5.4, 3.2, 3.2, "RandomForestFusion",
                   attrs=["- rf_estimator: RandomForest", "- n_trees: int = 100", "- max_depth: int = 4", "- class_weights: str = 'balanced'"],
                   methods=["+ predict_proba(x): ndarray", "+ predict_class(x): str", "+ compute_entropy(): float", "+ check_uncertainty(): bool"])

    # Class 4: Qwen3VLService
    draw_uml_class(12.6, 5.4, 3.0, 3.2, "Qwen3VLService",
                   attrs=["- model_id: str", "- device: str = 'cuda:0'", "- prompt_template: str", "- max_tokens: int = 512"],
                   methods=["+ format_prompt(): str", "+ generate_cot_reasoning()", "+ parse_structured_json()", "+ extract_policy_label()"])

    # Class 5: StrategyDFusion
    draw_uml_class(4.6, 1.2, 3.4, 3.4, "StrategyDFusion",
                   attrs=["- veto_threshold: float = 0.40", "- adult_threshold: float = 0.60", "- margin_threshold: float = 0.10"],
                   methods=["+ rule1_safety_veto(): bool", "+ rule2_adult_tier(): bool", "+ rule3_human_abstention(): bool", "+ execute_fusion(): Decision"])

    # Class 6: BiometricVerifier
    draw_uml_class(9.0, 1.2, 3.2, 3.4, "BiometricVerifier",
                   attrs=["- arcface_model: InsightFace", "- liveness_model: MiniFASNet", "- fft_threshold: float = 0.42", "- sim_threshold: float = 0.45"],
                   methods=["+ compute_fft_moire(): float", "+ predict_liveness(): bool", "+ extract_embedding(): ndarray", "+ match_faces(): float"])

    # Class 7: DeliveryDispatcher
    draw_uml_class(12.6, 1.2, 3.0, 3.4, "DeliveryDispatcher",
                   attrs=["- tier_precedence: Dict", "- verified_age_group: str", "- active_policy: str"],
                   methods=["+ evaluate_delivery(): Action", "+ quarantine_asset()", "+ suppress_for_minors()", "+ serialize_audit_record()"])

    # UML Relationships (Arrows)
    draw_arrow(ax, 3.8, 7.0, 4.6, 7.0, label='feeds')
    draw_arrow(ax, 8.0, 7.0, 9.0, 7.0, label='33-dim vector')
    draw_arrow(ax, 8.0, 6.2, 12.6, 6.2, label='media context')
    draw_arrow(ax, 10.6, 5.4, 6.3, 4.6, label='rf_probs')
    draw_arrow(ax, 14.1, 5.4, 8.0, 4.6, label='vlm_decision')
    draw_arrow(ax, 8.0, 2.9, 9.0, 2.9, label='verifies')
    draw_arrow(ax, 12.2, 2.9, 12.6, 2.9, label='age bracket')
    draw_arrow(ax, 6.3, 1.2, 12.6, 1.8, label='statutory verdict', rad=-0.2)

    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, 'class_diagram.png'), dpi=300, bbox_inches='tight')
    fig.savefig(os.path.join(out_dir, 'class_diagram.svg'), bbox_inches='tight')
    plt.close(fig)
    print("Exported class_diagram.png & .svg")

# ==============================================================================
# 4. UML USE CASE DIAGRAM
# ==============================================================================
def create_use_case_diagram(out_dir):
    fig, ax = plt.subplots(figsize=(15, 9), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 9)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    # Header
    ax.text(7.5, 8.5, 'UML Use Case Diagram: SafeAd AI Platform Actor Interactions',
            ha='center', va='center', fontsize=13, fontweight='bold', color=COLOR_NAVY)

    # System Boundary Rectangle
    boundary = FancyBboxPatch((3.5, 0.8), 8.0, 7.2, boxstyle="square,pad=0.15",
                              facecolor='#F8FAFC', edgecolor=COLOR_SLATE, lw=1.5)
    ax.add_patch(boundary)
    ax.text(7.5, 7.7, 'SafeAd AI System Boundary', ha='center', va='center',
            fontsize=10, fontweight='bold', color=COLOR_NAVY)

    # Actor drawing helper (standard stick figure representation)
    def draw_actor(x, y, name, sub=""):
        # Head
        ax.add_patch(Circle((x, y+0.45), 0.18, facecolor='#FFFFFF', edgecolor=COLOR_NAVY, lw=1.5))
        # Body
        ax.plot([x, x], [y+0.27, y-0.2], color=COLOR_NAVY, lw=1.5)
        # Arms
        ax.plot([x-0.25, x+0.25], [y+0.12, y+0.12], color=COLOR_NAVY, lw=1.5)
        # Legs
        ax.plot([x, x-0.2], [y-0.2, y-0.6], color=COLOR_NAVY, lw=1.5)
        ax.plot([x, x+0.2], [y-0.2, y-0.6], color=COLOR_NAVY, lw=1.5)
        # Label
        ax.text(x, y-0.85, name, ha='center', va='top', fontsize=9, fontweight='bold', color=COLOR_NAVY)
        if sub:
            ax.text(x, y-1.08, sub, ha='center', va='top', fontsize=7.2, color=TEXT_MUTED)

    # Use Case Ellipse helper
    def draw_use_case(x, y, w, h, text):
        ellipse = patches.Ellipse((x, y), w, h, facecolor='#FFFFFF', edgecolor=COLOR_BORDER_BLUE, lw=1.2)
        ax.add_patch(ellipse)
        ax.text(x, y, text, ha='center', va='center', fontsize=8.0, fontweight='bold', color=TEXT_DARK)

    # Draw Actors
    draw_actor(1.8, 6.2, "Advertiser", "Campaign Submitter")
    draw_actor(1.8, 2.8, "Social User", "Audience Viewer")
    draw_actor(13.2, 4.5, "Compliance Admin", "Platform Auditor")

    # Draw Use Cases inside boundary
    draw_use_case(7.5, 7.0, 3.8, 0.9, "UC1: Submit Campaign Media")
    draw_use_case(7.5, 5.8, 4.2, 0.9, "UC2: Pre-Pub Moderation Scan")
    draw_use_case(7.5, 4.6, 4.2, 0.9, "UC3: Multi-Evidence PAD & Liveness")
    draw_use_case(7.5, 3.4, 4.2, 0.9, "UC4: Biometric Age Verification")
    draw_use_case(7.5, 2.2, 4.0, 0.9, "UC5: Age-Gated Ad Feed Filtering")
    draw_use_case(7.5, 1.1, 4.2, 0.85, "UC6: Audit Rationale & Override")

    # Connectors: Advertiser
    ax.plot([2.2, 5.6], [6.2, 7.0], color=COLOR_SLATE, lw=1.2)
    ax.plot([2.2, 5.4], [6.2, 5.8], color=COLOR_SLATE, lw=1.2)

    # Connectors: Social User
    ax.plot([2.2, 5.4], [2.8, 4.6], color=COLOR_SLATE, lw=1.2)
    ax.plot([2.2, 5.4], [2.8, 3.4], color=COLOR_SLATE, lw=1.2)
    ax.plot([2.2, 5.5], [2.8, 2.2], color=COLOR_SLATE, lw=1.2)

    # Connectors: Platform Auditor
    ax.plot([12.8, 9.6], [4.5, 5.8], color=COLOR_SLATE, lw=1.2)
    ax.plot([12.8, 9.6], [4.5, 1.1], color=COLOR_SLATE, lw=1.2)

    # Include relationships between use cases
    draw_arrow(ax, 7.5, 6.55, 7.5, 6.25, label='<<include>>', color=COLOR_BORDER_SLATE, lw=1.0)
    draw_arrow(ax, 7.5, 4.15, 7.5, 3.85, label='<<include>>', color=COLOR_BORDER_SLATE, lw=1.0)
    draw_arrow(ax, 7.5, 2.95, 7.5, 2.65, label='<<triggers>>', color=COLOR_BORDER_SLATE, lw=1.0)

    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, 'use_case_diagram.png'), dpi=300, bbox_inches='tight')
    fig.savefig(os.path.join(out_dir, 'use_case_diagram.svg'), bbox_inches='tight')
    plt.close(fig)
    print("Exported use_case_diagram.png & .svg")

def main():
    uml_dir = os.path.join('report_assets_final', 'uml_dfd')
    os.makedirs(uml_dir, exist_ok=True)

    create_dfd_level_0(uml_dir)
    create_dfd_level_1(uml_dir)
    create_class_diagram(uml_dir)
    create_use_case_diagram(uml_dir)

if __name__ == '__main__':
    main()
