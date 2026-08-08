"""
Datasets Module for SAFE-VISION / Multimodal Content Moderation.

This file lists and organizes all open datasets extracted from the research papers
contained in the project. It provides metadata, descriptions, download/access URLs,
and helper loader functions to work with these datasets in Python.

Modality Legend:
- Video: Visual frames only.
- Audio: Acoustic signals only.
- Audio-Visual / Video+Audio: Both visual and acoustic channels.
- Multimodal Meme / Image-Text: Visual memes combined with overlay text.
- Text: Textual datasets.
"""

import os
import urllib.request
from typing import Dict, Any, Optional

# Dict containing metadata for all extracted datasets
DATASETS_METADATA: Dict[str, Dict[str, Any]] = {
    # ==========================================
    # VIDEO / AUDIO / AUDIO-VISUAL DATASETS
    # ==========================================
    "safewatch_bench": {
        "name": "SAFEWATCH-BENCH",
        "has_video": True,
        "has_audio": False, # Primarily focused on visual frames for guardrails
        "modality": "Video",
        "description": "Large-scale video guardrail dataset containing 2M video clips (Real-world and GenAI splits) across 6 unsafe categories.",
        "source_paper": "Safewatch (ICLR 2025)",
        "access_link": "https://github.com/ICLR2025-Safewatch/Safewatch",
        "huggingface_id": None
    },
    "kuaimod": {
        "name": "KuaiMod",
        "has_video": True,
        "has_audio": True,
        "modality": "Audio-Visual (Video + Audio)",
        "description": "Short Video Platform (SVP) content moderation benchmark from Kuaishou, with 24,562 video samples covering 15 categories of violations.",
        "source_paper": "KuaiMod SVP Governance",
        "access_link": "https://github.com/Kuaishou-Research/KuaiMod",
        "huggingface_id": None
    },
    "xd_violence": {
        "name": "XD-Violence",
        "has_video": True,
        "has_audio": True,
        "modality": "Audio-Visual (Video + Audio)",
        "description": "A large-scale video dataset for violence detection in both video and audio streams (explosions, gunshots, screams). Contains 4,754 videos.",
        "source_paper": "XD-Violence (ECCV 2020)",
        "access_link": "https://roc-ng.github.io/XD-Violence/",
        "huggingface_id": "detection-datasets/xd-violence"
    },
    "ucf_crime": {
        "name": "UCF-Crime",
        "has_video": True,
        "has_audio": False, # Mostly silent surveillance footage
        "modality": "Video",
        "description": "Surveillance videos capturing real-world anomalies, crimes, and safety hazards, used for anomaly detection.",
        "source_paper": "Real-world Anomaly Detection in Surveillance Videos (CVPR 2018)",
        "access_link": "https://www.crcv.ucf.edu/research/projects/real-world-anomaly-detection-in-surveillance-videos/",
        "huggingface_id": None
    },
    "fakesv": {
        "name": "FakeSV",
        "has_video": True,
        "has_audio": True,
        "modality": "Audio-Visual + Text",
        "description": "A multimodal benchmark for fake news detection on short videos, including rich social context, visual content, and audio cues.",
        "source_paper": "FakeSV (AAAI 2023 / ACM MM)",
        "access_link": "https://github.com/FakeSV/FakeSV-Benchmark",
        "huggingface_id": None
    },
    "autoshot": {
        "name": "Autoshot",
        "has_video": True,
        "has_audio": False,
        "modality": "Video",
        "description": "A short video dataset specifically compiled for Shot Boundary Detection (SBD) to analyze scene transitions.",
        "source_paper": "Autoshot: A Short Video Dataset",
        "access_link": "https://github.com/AutoShot-SBD/AutoShot",
        "huggingface_id": None
    },
    "vhd11k": {
        "name": "VHD11K",
        "has_video": True,
        "has_audio": False,
        "modality": "Video",
        "description": "Video Harmfulness Recognition dataset comprising 11,000 video samples for toxic and harmful visual content filtering.",
        "source_paper": "Video Harmfulness Recognition Benchmark",
        "access_link": "https://github.com/VHD11K/VHD11K",
        "huggingface_id": None
    },
    "vsd": {
        "name": "Violent Scenes Dataset (VSD)",
        "has_video": True,
        "has_audio": True,
        "modality": "Audio-Visual (Video + Audio)",
        "description": "Dataset containing movie scenes labeled for violence, capturing visual actions and acoustic indices like explosions or screaming.",
        "source_paper": "The Violent Scenes Dataset (VSD)",
        "access_link": "https://www.interdigital.com/research-innovation/technologies/multimedia/vsd-dataset",
        "huggingface_id": None
    },
    "blm_guard": {
        "name": "BLM-Guard Benchmark",
        "has_video": True,
        "has_audio": False,
        "modality": "Video",
        "description": "A real-world commercial short-video ads dataset for ad moderation, structured across seven risk tiers.",
        "source_paper": "BLM-Guard: Safeguarding Vision Curation (AAAI 2026)",
        "access_link": "https://github.com/YangY-PHI/BLM-Guard",
        "huggingface_id": None
    },
    "lspd": {
        "name": "LSPD (Large-scale Pornographic Dataset)",
        "has_video": True,
        "has_audio": False,
        "modality": "Video / Image",
        "description": "Large-scale pornographic dataset for detection, classification, and age-appropriate content management systems.",
        "source_paper": "LSPD: Large-Scale Pornographic Dataset",
        "access_link": "https://github.com/Phan-et-al/LSPD",
        "huggingface_id": None
    },

    # ==========================================
    # MULTIMODAL MEME (IMAGE + TEXT) DATASETS
    # ==========================================
    "facebook_hateful_memes": {
        "name": "Facebook Hateful Memes (FHM)",
        "has_video": False,
        "has_audio": False,
        "modality": "Image-Text Meme",
        "description": "A multimodal dataset consisting of 10,000+ memes, specifically designed to test visual-textual hate speech detection.",
        "source_paper": "The Hateful Memes Challenge (NeurIPS 2020)",
        "access_link": "https://ai.meta.com/tools/hatefulmemes/",
        "huggingface_id": "facebook/hateful_memes"
    },
    "harmeme": {
        "name": "HarMeme",
        "has_video": False,
        "has_audio": False,
        "modality": "Image-Text Meme",
        "description": "A repository of harmful memes (original memes) annotated for severity and harm potential.",
        "source_paper": "HarMeme: Multimodal Harmful Meme Detection",
        "access_link": "https://github.com/LCS2-IIITD/HarMeme",
        "huggingface_id": None
    },
    "mami": {
        "name": "MAMI (Multimodal Abuse Detection)",
        "has_video": False,
        "has_audio": False,
        "modality": "Image-Text Meme",
        "description": "Multimodal Abuse detection against Women on Instagram meme dataset, capturing misogyny.",
        "source_paper": "SemEval-2022 Task 5: Multimodal Misogyny Detection",
        "access_link": "https://competitions.codalab.org/competitions/34175",
        "huggingface_id": "semeval2022_task5"
    },
    "hatred": {
        "name": "HatReD (Hateful meme with Reasons Dataset)",
        "has_video": False,
        "has_audio": False,
        "modality": "Image-Text Meme + Text Reasons",
        "description": "An extension of the Facebook Hateful Memes (FHM) dataset that includes additional human-annotated explanation reasons.",
        "source_paper": "Hateful Memes with Reasons Dataset (NeurIPS/ICLR workshops)",
        "access_link": "https://github.com/HatReD-dataset/HatReD",
        "huggingface_id": None
    },
    "multioff": {
        "name": "MultiOFF",
        "has_video": False,
        "has_audio": False,
        "modality": "Image-Text Meme",
        "description": "Multimodal meme dataset for identifying offensive content on social media.",
        "source_paper": "MultiOFF: Multimodal Meme Dataset",
        "access_link": "https://github.com/smartdata-cs-unibo/MultiOFF",
        "huggingface_id": None
    },

    # ==========================================
    # TEXT-ONLY DATASETS
    # ==========================================
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


def list_datasets() -> None:
    """Prints out all available datasets with their modalities and descriptions."""
    print("=" * 80)
    print(f"{'AVAILABLE DATASETS IN SAFE-VISION':^80}")
    print("=" * 80)
    for key, data in DATASETS_METADATA.items():
        print(f"Key: {key:<20} | Name: {data['name']}")
        print(f"Modality: {data['modality']}")
        print(f"Video Support: {'YES' if data['has_video'] else 'NO'} | Audio Support: {'YES' if data['has_audio'] else 'NO'}")
        print(f"Description: {data['description']}")
        print(f"Access/Link: {data['access_link']}")
        print("-" * 80)


def load_dataset(dataset_key: str) -> Optional[Any]:
    """
    Attempts to import and load the dataset.
    For Hugging Face datasets (e.g., FHM, MAMI, Toxigen), it will try to import and use the 'datasets' library.
    For local or external video/audio datasets, it prints out the download instructions.
    
    Args:
        dataset_key (str): The key representing the dataset in DATASETS_METADATA.
        
    Returns:
        Optional[Any]: The loaded dataset object if using Hugging Face, or None.
    """
    if dataset_key not in DATASETS_METADATA:
        print(f"Error: Dataset '{dataset_key}' is not registered in the system.")
        return None
        
    meta = DATASETS_METADATA[dataset_key]
    print(f"\n[INFO] Loading Dataset: {meta['name']} ({meta['modality']})")
    
    # Audio/Video classification
    is_video = meta["has_video"]
    is_audio = meta["has_audio"]
    
    if is_video and is_audio:
        print(">> Note: This is a combined Audio-Visual dataset containing both video frames and audio files.")
    elif is_video:
        print(">> Note: This is a Video dataset.")
    elif is_audio:
        print(">> Note: This is an Audio dataset.")
    else:
        print(">> Note: This is a Non-AV dataset (Memes, Images, or Text).")
        
    hf_id = meta["huggingface_id"]
    if hf_id:
        try:
            print(f"Attempting to import Hugging Face 'datasets' to fetch: '{hf_id}'...")
            from datasets import load_dataset as hf_load_dataset
            dataset = hf_load_dataset(hf_id)
            print(f"Successfully loaded {meta['name']} via Hugging Face!")
            return dataset
        except ImportError:
            print("Hugging Face 'datasets' library is not installed. To install it, run:")
            print("  pip install datasets")
            print(f"Alternatively, you can manually access the dataset at: {meta['access_link']}")
            return None
        except Exception as e:
            print(f"Failed to fetch dataset from Hugging Face: {e}")
            print(f"Please reference/download manually at: {meta['access_link']}")
            return None
    else:
        print("This dataset is not hosted directly on Hugging Face Datasets or requires manual setup.")
        print(f"Please download/register and access the files from the official URL: {meta['access_link']}")
        return None


if __name__ == "__main__":
    list_datasets()
