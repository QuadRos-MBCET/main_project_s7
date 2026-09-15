import os
import requests
import json
from typing import Dict, Any

DATASETS_METADATA: Dict[str, Dict[str, Any]] = {
    "safewatch_bench": {
        "name": "SAFEWATCH-BENCH",
        "has_video": True,
        "has_audio": False,
        "modality": "Video",
        "description": "Large-scale video guardrail dataset containing 2M video clips (Real-world and GenAI splits) across 6 unsafe categories.",
        "source_paper": "Safewatch (ICLR 2025)",
        "access_link": "https://huggingface.co/datasets/Virtue-AI-HUB/SafeWatch-Bench",
        "huggingface_id": "Virtue-AI-HUB/SafeWatch-Bench"
    },
    "kuaimod": {
        "name": "KuaiMod",
        "has_video": True,
        "has_audio": True,
        "modality": "Audio-Visual (Video + Audio)",
        "description": "Short Video Platform (SVP) content moderation benchmark from Kuaishou, with 24,562 video samples covering 15 categories of violations.",
        "source_paper": "KuaiMod SVP Governance",
        "access_link": "https://kuaimod.github.io/",
        "huggingface_id": None
    },
    "xd_violence": {
        "name": "XD-Violence",
        "has_video": True,
        "has_audio": True,
        "modality": "Audio-Visual (Video + Audio)",
        "description": "A large-scale video dataset for violence detection in both video and audio streams (explosions, gunshots, screams). Contains 4,754 videos.",
        "source_paper": "XD-Violence (ECCV 2020)",
        "access_link": "https://huggingface.co/datasets/jherng/xd-violence",
        "huggingface_id": "jherng/xd-violence"
    },
    "ucf_crime": {
        "name": "UCF-Crime",
        "has_video": True,
        "has_audio": False,
        "modality": "Video",
        "description": "Surveillance videos capturing real-world anomalies, crimes, and safety hazards, used for anomaly detection.",
        "source_paper": "Real-world Anomaly Detection in Surveillance Videos (CVPR 2018)",
        "access_link": "https://github.com/WaqasSultani/AnomalyDetectionCVPR2018",
        "huggingface_id": None
    },
    "fakesv": {
        "name": "FakeSV",
        "has_video": True,
        "has_audio": True,
        "modality": "Audio-Visual + Text",
        "description": "A multimodal benchmark for fake news detection on short videos, including rich social context, visual content, and audio cues.",
        "source_paper": "FakeSV (AAAI 2023 / ACM MM)",
        "access_link": "https://github.com/ICTMCG/FakeSV",
        "huggingface_id": None
    },
    "autoshot": {
        "name": "Autoshot",
        "has_video": True,
        "has_audio": False,
        "modality": "Video",
        "description": "A short video dataset specifically compiled for Shot Boundary Detection (SBD) to analyze scene transitions.",
        "source_paper": "Autoshot: A Short Video Dataset",
        "access_link": "https://github.com/wentaozhu/AutoShot",
        "huggingface_id": None
    },
    "vhd11k": {
        "name": "VHD11K",
        "has_video": True,
        "has_audio": False,
        "modality": "Video",
        "description": "Video Harmfulness Recognition dataset comprising 11,000 video samples for toxic and harmful visual content filtering.",
        "source_paper": "Video Harmfulness Recognition Benchmark",
        "access_link": "https://github.com/nctu-eva-lab/VHD11K",
        "huggingface_id": "denny3388/VHD11K"
    },
    "vsd": {
        "name": "Violent Scenes Dataset (VSD)",
        "has_video": True,
        "has_audio": True,
        "modality": "Audio-Visual (Video + Audio)",
        "description": "Dataset containing movie scenes labeled for violence, capturing visual actions and acoustic indices like explosions or screaming.",
        "source_paper": "The Violent Scenes Dataset (VSD)",
        "access_link": "https://github.com/m-b-m/VSD",
        "huggingface_id": None
    },
    "blm_guard": {
        "name": "BLM-Guard Benchmark",
        "has_video": True,
        "has_audio": False,
        "modality": "Video",
        "description": "A real-world commercial short-video ads dataset for ad moderation, structured across seven risk tiers. (Closed-source, academic access).",
        "source_paper": "BLM-Guard: Safeguarding Vision Curation (AAAI 2026)",
        "access_link": "https://arxiv.org/abs/2602.18193",
        "huggingface_id": None
    },
    "lspd": {
        "name": "LSPD (Large-scale Pornographic Dataset)",
        "has_video": True,
        "has_audio": False,
        "modality": "Video / Image",
        "description": "Large-scale pornographic dataset for detection, classification, and age-appropriate content management systems (Requires author request).",
        "source_paper": "LSPD: Large-Scale Pornographic Dataset",
        "access_link": "https://www.researchgate.net/publication/362688888_LSPD_A_Large-Scale_Pornographic_Dataset_for_Detection_and_Classification",
        "huggingface_id": None
    },
    "facebook_hateful_memes": {
        "name": "Facebook Hateful Memes (FHM)",
        "has_video": False,
        "has_audio": False,
        "modality": "Image-Text Meme",
        "description": "A multimodal dataset consisting of 10,000+ memes, specifically designed to test visual-textual hate speech detection.",
        "source_paper": "The Hateful Memes Challenge (NeurIPS 2020)",
        "access_link": "https://www.drivendata.org/competitions/73/hateful-memes/",
        "huggingface_id": "facebook/hateful_memes"
    },
    "harmeme": {
        "name": "HarMeme",
        "has_video": False,
        "has_audio": False,
        "modality": "Image-Text Meme",
        "description": "A repository of harmful memes (original memes) annotated for severity and harm potential.",
        "source_paper": "HarMeme: Multimodal Harmful Meme Detection",
        "access_link": "https://github.com/di-dimitrov/harmeme",
        "huggingface_id": None
    },
    "mami": {
        "name": "MAMI (Multimodal Abuse Detection)",
        "has_video": False,
        "has_audio": False,
        "modality": "Image-Text Meme",
        "description": "Multimodal Abuse detection against Women on Instagram meme dataset, capturing misogyny.",
        "source_paper": "SemEval-2022 Task 5: Multimodal Misogyny Detection",
        "access_link": "https://github.com/MAMI-SemEval2022/MAMI",
        "huggingface_id": None
    },
    "hatred": {
        "name": "HatReD (Hateful meme with Reasons Dataset)",
        "has_video": False,
        "has_audio": False,
        "modality": "Image-Text Meme + Text Reasons",
        "description": "An extension of the Facebook Hateful Memes (FHM) dataset that includes additional human-annotated explanation reasons.",
        "source_paper": "Hateful Memes with Reasons Dataset (NeurIPS/ICLR workshops)",
        "access_link": "https://github.com/Social-AI-Studio/HatReD",
        "huggingface_id": None
    },
    "multioff": {
        "name": "MultiOFF",
        "has_video": False,
        "has_audio": False,
        "modality": "Image-Text Meme",
        "description": "Multimodal meme dataset for identifying offensive content on social media.",
        "source_paper": "MultiOFF: Multimodal Meme Dataset",
        "access_link": "https://github.com/bharathichezhiyan/Multimodal-Meme-Classification-Identifying-Offensive-Content-in-Image-and-Text",
        "huggingface_id": None
    },
    "toxigen": {
        "name": "Toxigen",
        "has_video": False,
        "has_audio": False,
        "modality": "Text",
        "description": "Large-scale machine-generated dataset for implicit and adversarial hate speech detection.",
        "source_paper": "Toxigen (ACL 2022)",
        "access_link": "https://github.com/microsoft/TOXIGEN",
        "huggingface_id": "microsoft/toxigen"
    }
}

def audit_datasets():
    print("=" * 75)
    print("      SAFEAD AI (SAFE-VISION) DATASET COMPREHENSIVE AUDIT REPORT      ")
    print("=" * 75)
    print(f"Total Configured Datasets: {len(DATASETS_METADATA)}\n")
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    audit_results = []
    
    for idx, (key, meta) in enumerate(DATASETS_METADATA.items(), 1):
        print(f"[{idx}/16] Checking Dataset: {meta['name']} (Key: '{key}')")
        print(f"     Modality   : {meta['modality']} | Source: {meta['source_paper']}")
        print(f"     Description: {meta['description']}")
        
        # Check Access Link HTTP Status
        link_status = "UNKNOWN"
        try:
            r = requests.head(meta["access_link"], headers=headers, timeout=10, allow_redirects=True)
            if r.status_code in [200, 301, 302, 403]:  # 403 means active server blocking head requests
                link_status = f"ONLINE (HTTP {r.status_code})"
            else:
                link_status = f"HTTP Status {r.status_code}"
        except Exception as e:
            link_status = f"Connection Error: {e}"
            
        # Check HuggingFace Status if applicable
        hf_status = "N/A (Closed / External Repo)"
        if meta["huggingface_id"]:
            hf_url = f"https://huggingface.co/datasets/{meta['huggingface_id']}"
            try:
                hr = requests.head(hf_url, headers=headers, timeout=10, allow_redirects=True)
                if hr.status_code in [200, 301, 302, 401, 403]:
                    hf_status = f"EXISTS ON HUB ({meta['huggingface_id']})"
                else:
                    hf_status = f"Hub Error (HTTP {hr.status_code})"
            except Exception:
                hf_status = f"Hub Check Failed ({meta['huggingface_id']})"
                
        print(f"     Access Link Status: {link_status}")
        print(f"     HuggingFace Status : {hf_status}\n")
        
        audit_results.append({
            "key": key,
            "name": meta["name"],
            "modality": meta["modality"],
            "source_paper": meta["source_paper"],
            "link_status": link_status,
            "hf_status": hf_status
        })

    print("=" * 75)
    print("                  AUDIT SUMMARY SUMMARY SUMMARY               ")
    print("=" * 75)
    for res in audit_results:
        print(f"• {res['name']:<35} | {res['modality']:<25} | {res['link_status']}")
    print("=" * 75)

if __name__ == "__main__":
    audit_datasets()
