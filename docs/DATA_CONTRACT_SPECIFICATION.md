# SAFE-VISION — Dataset Expansion Data Contract Specification

**Document Version**: 1.0.0  
**Target Repository**: `QuadRos-MBCET/safead-dataset-hub`  
**Governing Standard**: SafeAd AI Multimodal Trust & Safety Framework  
**Scope**: Requirements for Phase 5B / Final Benchmark Dataset Expansion  

---

## 1. Executive Summary

This data contract defines the mandatory schema, quality standards, provenance attributes, and anti-leakage constraints for expanding the `safead-dataset-hub` repository.

> [!IMPORTANT]
> **Strict Isolation & Zero-Leakage Rules**:
> 1. Dataset improvements must be executed exclusively within the `safead-dataset-hub` repository. Do NOT modify the application codebase (`main_project_s7`) to match dataset peculiarities.
> 2. The frozen benchmark (`splits/repaired_benchmark/`) must remain **unaltered** until a newly versioned split (e.g. `splits/v2.0_clean_benchmark/`) is published with complete provenance.
> 3. Zero Answer Leakage: Media files must never contain synthetic review cards, bounding box overlays, decision headers (e.g. "REJECT - UNSAFE FOR ALL"), or ground-truth classification labels embedded inside visual pixels or audio tracks.

---

## 2. Mandatory Catalog Schema (`catalog.csv`)

Every candidate media entry in the dataset hub must include the following 18 columns:

| Column Name | Data Type | Constraint / Allowed Values | Description |
| :--- | :--- | :--- | :--- |
| `sample_id` | String | `^SAFEAD_(SFA\|S14P\|S18P\|UFA)_(IMG\|VID)_[0-9]{3,}$` | Unique identifier incorporating category code, modality, and sequential ID. |
| `file_path` | String | POSIX relative path | Path relative to repository root (e.g., `custom_ads/safe_for_all/images/SAFEAD_SFA_IMG_001.jpg`). |
| `storage_uri` | String | URI string | Remote permanent archival URI (e.g., Hugging Face dataset URI or Git LFS path). |
| `media_type` | Enum | `image`, `video` | Primary media modality. |
| `safead_label` | Enum | `SAFE_FOR_ALL`, `SAFE_14_PLUS`, `SAFE_18_PLUS`, `UNSAFE_FOR_ALL` | Ground-truth policy classification under the 4-tier moderation framework. |
| `label_reason` | String | Non-empty text | Detailed policy justification explaining why the advertisement belongs to this tier. |
| `source_name` | String | Non-empty text | Origin repository or archive (e.g., `Internet Archive Commercials`, `Wikimedia Commons`). |
| `source_url` | String | Valid URL | Permanent source link or accession URL for copyright verification. |
| `original_source_label` | String | Text | Original label/category from the source archive before SafeAd normalization. |
| `collection_date` | Date | `YYYY-MM-DD` | Date when the creative was harvested and archived. |
| `license_status` | Enum | `Public Domain`, `CC-BY-4.0`, `CC-BY-SA-4.0`, `Fair Use (Research Only)` | Legal distribution license. Proprietary active commercial assets must be strictly research-exempt. |
| `sha256` | String | `^[a-f0-9]{64}$` | Lowercase hexadecimal SHA-256 hash computed over the raw media file bytes. |
| `annotation_status` | Enum | `raw_collected`, `annotated`, `peer_reviewed`, `adjudicated` | Verification state of human annotation. |
| `review_status` | Enum | `verified_authentic_creative`, `quarantined_synthetic_overlay` | Confirmation that media contains no artificial banners or review borders. |
| `resolution` | String | `^[0-9]+x[0-9]+$` | Media dimensions in pixels (e.g. `1920x1080`). Must not be synthetic `800x520`. |
| `file_size_kb` | Float | `> 0.0` | Exact file size on disk in kilobytes. |
| `duration_seconds` | Float | `>= 0.0` | Media duration in seconds (must be `0.0` for images, `> 0.0` for videos). |
| `has_audio` | Boolean | `True`, `False` | Presence of active audio track (must be `False` for images). |
| `ocr_ground_truth_text` | String | Text | Verbatim textual transcript of all visible in-scene typography. No labels or rationale! |
| `ocr_text_type` | Enum | `in_scene_creative`, `overlay_caption`, `typography_only`, `no_text` | Typographic style of embedded ad copy. |

---

## 3. Stratified Dataset Balance & Modern Prohibited Expansion Targets

To resolve the extreme prohibited class scarcity discovered in Phase 4 ($N=10$ clean prohibited development samples, dominated by 19th-century patent medicine print clippings), the dataset developer must deliver:

```
+---------------------------------------------------------------------------------------------------+
| CATEGORY          | CURRENT CLEAN DEV | TARGET DEV ADDITIONS | TARGET DOMAIN CREATIVE FORMATS     |
+---------------------------------------------------------------------------------------------------+
| SAFE_FOR_ALL      | 56 img / 19 vid   | Maintain current     | Standard FMCG, electronics, travel |
| SAFE_14_PLUS      | 56 img / 19 vid   | Maintain current     | PG-13 movies, video games, fitness |
| SAFE_18_PLUS      | 15 img / 19 vid   | +15 modern digital   | Regulated craft beer, wine, vape   |
| UNSAFE_FOR_ALL    | 7 img / 3 vid     | +35 modern digital   | Crypto schemes, phishing, quackery |
+---------------------------------------------------------------------------------------------------+
```

### High-Priority Prohibited Categories to Harvest
1. **Deceptive Financial Yield Schemes**:
   - Modern social media sponsored display ads promoting "guaranteed $500/day automated trading algorithms" or "zero-risk crypto staking loops".
2. **Advance-Fee & Phishing Displays**:
   - Web banner ads promising unclaimed government grants, gift card giveaways, or lottery winnings requiring administrative handling fees.
3. **Deceptive Medical & Miracle Health Products**:
   - Digital sponsored advertorials promoting "miracle unapproved diabetes cures", "secret herbal weight loss gummies", or "pain-elimination patches with fake doctor endorsements".
4. **Violent Combat & Weapon Retailing**:
   - Advertisements selling prohibited tactical combat knives, illegal switchblades, or promoting graphic physical street brawl pay-per-view broadcasts.

---

## 4. Verification & Ingestion Protocol

When the expanded dataset is ready:
1. **Hash Verification**: A validation script will verify `sha256(media_file) == catalog.csv["sha256"]` for every entry.
2. **Resolution & Aspect Ratio Audit**: Confirm zero `800x520` synthetic card templates remain.
3. **Zero-Leakage OCR Audit**: Run regex scans across `ocr_ground_truth_text` to verify zero instances of `UNSAFE_FOR_ALL`, `REJECT`, `PROHIBITED`, `SAFE_18_PLUS`, etc.
4. **Deterministic Split Release**: Publish under a dedicated version directory:
   `splits/v2.0_clean_benchmark/development_set.csv` and `splits/v2.0_clean_benchmark/test_held_out.csv`
   with frozen 70/30 train/test split hashes.
