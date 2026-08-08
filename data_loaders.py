import os
import cv2
import torch
import numpy as np
from PIL import Image
from torch.utils.data import Dataset
from typing import List, Dict, Any, Tuple

class ImageMemeDataset(Dataset):
    """
    Dataset wrapper for Image-Text Meme Classification datasets (e.g., FHM, HarMeme, MAMI, HatReD).
    Loads images and prepares text instructions for training.
    """
    def __init__(self, data_list: List[Dict[str, Any]], image_dir: str, processor: Any, is_train: bool = True):
        self.data = data_list
        self.image_dir = image_dir
        self.processor = processor
        self.is_train = is_train

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        item = self.data[idx]
        image_path = os.path.join(self.image_dir, item["image_filename"])
        
        # Fallback to a mock image if the file doesn't exist (for dry-run/testing)
        if not os.path.exists(image_path):
            # Create a mock RGB image
            image = Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8))
        else:
            image = Image.open(image_path).convert("RGB")
            
        label = item.get("label", 0)  # 1 for harmful/offensive/unsafe, 0 for safe
        reason = item.get("reason", "No reason provided.")
        text_overlay = item.get("text", "")
        
        # Build conversational structure for fine-tuning
        user_prompt = f"Analyze this meme. Text on meme: '{text_overlay}'. Is this meme harmful/offensive? Provide a yes/no answer and a brief explanation."
        assistant_response = f"Label: {'yes' if label == 1 else 'no'}. Reason: {reason}"
        
        conversation = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": user_prompt}
                ]
            }
        ]
        
        if self.is_train:
            conversation.append({
                "role": "assistant",
                "content": [
                    {"type": "text", "text": assistant_response}
                ]
            })
            
        # Format conversation using the VLM processor
        text_prompt = self.processor.apply_chat_template(conversation, tokenize=False, add_generation_prompt=not self.is_train)
        
        # Prepare model inputs
        inputs = self.processor(
            images=image,
            text=text_prompt,
            return_tensors="pt"
        )
        
        # Remove batch dimension added by processor
        inputs = {k: v.squeeze(0) for k, v in inputs.items()}
        inputs["labels"] = inputs["input_ids"].clone() # SFTTrainer handles masking labels if needed, or custom masking
        
        return inputs


class VideoSafetyDataset(Dataset):
    """
    Dataset wrapper for Video Content Moderation datasets (e.g., Safewatch, KuaiMod, XD-Violence).
    Extracts frames from video files and formats them for the VLM.
    """
    def __init__(self, data_list: List[Dict[str, Any]], video_dir: str, processor: Any, max_frames: int = 8, is_train: bool = True):
        self.data = data_list
        self.video_dir = video_dir
        self.processor = processor
        self.max_frames = max_frames
        self.is_train = is_train

    def __len__(self) -> int:
        return len(self.data)

    def _load_video_frames(self, path: str) -> List[Image.Image]:
        if not os.path.exists(path):
            # Fallback to mock frames for testing
            return [Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)) for _ in range(self.max_frames)]
            
        cap = cv2.VideoCapture(path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            return [Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)) for _ in range(self.max_frames)]
            
        # Sample frames uniformly
        indices = np.linspace(0, total_frames - 1, self.max_frames, dtype=int)
        frames = []
        for idx in range(total_frames):
            ret, frame = cap.read()
            if not ret:
                break
            if idx in indices:
                # BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(Image.fromarray(frame_rgb))
        cap.release()
        
        # Pad with last frame if we couldn't read enough
        while len(frames) < self.max_frames:
            frames.append(frames[-1] if frames else Image.fromarray(np.zeros((224, 224, 3), dtype=np.uint8)))
            
        return frames[:self.max_frames]

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        item = self.data[idx]
        video_path = os.path.join(self.video_dir, item["video_filename"])
        
        frames = self._load_video_frames(video_path)
        
        label = item.get("label", 0)  # 1 for violative/unsafe, 0 for safe
        category = item.get("category", "general safety")
        explanation = item.get("explanation", "The video content is safe and normal.")
        
        user_prompt = f"Watch this video. Does this video contain any safety violations, graphic content, or policy violations? Identify labels and provide an explanation."
        assistant_response = f"Label: {'unsafe' if label == 1 else 'safe'}. Category: {category}. Reason: {explanation}"
        
        conversation = [
            {
                "role": "user",
                "content": [
                    {"type": "video", "video": frames},
                    {"type": "text", "text": user_prompt}
                ]
            }
        ]
        
        if self.is_train:
            conversation.append({
                "role": "assistant",
                "content": [
                    {"type": "text", "text": assistant_response}
                ]
            })
            
        # Format using processor
        text_prompt = self.processor.apply_chat_template(conversation, tokenize=False, add_generation_prompt=not self.is_train)
        
        # Prepare inputs
        inputs = self.processor(
            videos=frames,
            text=text_prompt,
            return_tensors="pt"
        )
        
        inputs = {k: v.squeeze(0) for k, v in inputs.items()}
        inputs["labels"] = inputs["input_ids"].clone()
        
        return inputs


# =====================================================================
# Mock Data Generators (Allows out-of-the-box testing without downloads)
# =====================================================================

def get_mock_meme_data(num_samples: int = 10) -> List[Dict[str, Any]]:
    """Generates mock image-text meme items for testing."""
    return [
        {
            "image_filename": f"meme_{i}.png",
            "text": f"This is some sarcastic overlay text {i}",
            "label": i % 2,
            "reason": f"Mock reason {i} why this meme is {'harmful' if i % 2 == 1 else 'safe'}."
        }
        for i in range(num_samples)
    ]

def get_mock_video_data(num_samples: int = 5) -> List[Dict[str, Any]]:
    """Generates mock video classification items for testing."""
    categories = ["sexual content", "violence", "theft", "safe/normal"]
    return [
        {
            "video_filename": f"video_{i}.mp4",
            "label": 1 if i % 2 == 0 else 0,
            "category": categories[i % len(categories)],
            "explanation": f"Mock explanation for video scene {i}."
        }
        for i in range(num_samples)
    ]
