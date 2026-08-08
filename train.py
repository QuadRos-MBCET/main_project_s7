import os
import argparse
import yaml
import torch
from transformers import (
    Qwen2VLForConditionalGeneration, 
    AutoProcessor,
    TrainingArguments,
    Trainer
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from data_loaders import ImageMemeDataset, VideoSafetyDataset, get_mock_meme_data, get_mock_video_data

def parse_args():
    parser = argparse.ArgumentParser(description="MLLM Fine-Tuning Pipeline for SAFE-VISION")
    parser.add_argument("--config", type=str, default="train_config.yaml", help="Path to config file")
    parser.add_argument("--dry_run", action="store_true", help="Run 1 step with mock data to test pipeline compilation")
    return parser.parse_args()

class VLMDataCollator:
    """
    Custom Data Collator to handle pad-token alignment for MLLM inputs,
    especially pixel values, grid templates, and label mask padding.
    """
    def __init__(self, processor):
        self.processor = processor

    def __call__(self, features):
        # features is a list of dicts returned from Dataset.__getitem__
        # Combine input_ids, labels, attention_masks, etc.
        first = features[0]
        batch = {}
        
        for k, v in first.items():
            if k not in ["input_ids", "labels", "attention_mask"]:
                # Pixel values, grid templates, frame features, etc.
                # Stack them or pad them based on dimensions
                if isinstance(v, torch.Tensor):
                    batch[k] = torch.stack([f[k] for f in features])
                else:
                    batch[k] = [f[k] for f in features]
                    
        # Token fields need padding
        input_ids = [f["input_ids"] for f in features]
        labels = [f["labels"] for f in features]
        
        # Use processor tokenizer pad method
        padded_inputs = self.processor.tokenizer.pad(
            {"input_ids": input_ids},
            padding=True,
            return_tensors="pt"
        )
        padded_labels = self.processor.tokenizer.pad(
            {"input_ids": labels},
            padding=True,
            return_tensors="pt"
        )
        
        batch["input_ids"] = padded_inputs["input_ids"]
        batch["attention_mask"] = padded_inputs["attention_mask"]
        
        # In labels, replace pad token ID with -100 so it's ignored in loss calculation
        batch["labels"] = padded_labels["input_ids"].clone()
        batch["labels"][batch["labels"] == self.processor.tokenizer.pad_token_id] = -100
        
        return batch

def main():
    args = parse_args()
    
    # Load configuration
    if os.path.exists(args.config):
        with open(args.config, "r") as f:
            config = yaml.safe_load(f)
    else:
        print(f"Warning: Configuration file '{args.config}' not found. Using default parameters.")
        config = {}
        
    # Get hyperparameters with defaults
    model_id = config.get("model_id", "Qwen/Qwen2-VL-7B-Instruct")
    dataset_type = config.get("dataset_type", "meme")  # "meme" or "video"
    output_dir = config.get("output_dir", "./results")
    epochs = config.get("epochs", 3)
    batch_size = config.get("batch_size", 2)
    lr = float(config.get("lr", 2e-5))
    lora_r = config.get("lora_r", 16)
    lora_alpha = config.get("lora_alpha", 32)
    lora_dropout = config.get("lora_dropout", 0.05)
    use_quantization = config.get("use_quantization", True)
    
    # Adjust config for dry-run
    if args.dry_run:
        print("\n=== RUNNING IN DRY RUN MODE ===")
        epochs = 1
        batch_size = 2
        # Use a smaller 2B parameter version of Qwen2-VL for fast local compilation checks
        model_id = "Qwen/Qwen2-VL-2B-Instruct" 
        
    print(f"Loading VLM Processor for: {model_id}...")
    processor = AutoProcessor.from_pretrained(model_id)
    
    # 4-bit Quantization Config (QLoRA)
    quantization_config = None
    if use_quantization and torch.cuda.is_available():
        from transformers import BitsAndBytesConfig
        print("Configuring QLoRA 4-bit Quantization...")
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True
        )

    print(f"Loading Base VLM Model: {model_id}...")
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        model_id,
        quantization_config=quantization_config,
        device_map="auto" if torch.cuda.is_available() else None,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32
    )
    
    if use_quantization and torch.cuda.is_available():
        model = prepare_model_for_kbit_training(model)
        
    # Configure LoRA adapter targeting language and vision modules
    print("Wrapping model with LoRA / PEFT...")
    peft_config = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"], # Targets standard projection layers
        lora_dropout=lora_dropout,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()
    
    # Prepare datasets
    print(f"Preparing datasets (Type: {dataset_type})...")
    if args.dry_run:
        # Load mock data for quick compilation verification
        if dataset_type == "meme":
            raw_data = get_mock_meme_data(num_samples=4)
            train_dataset = ImageMemeDataset(raw_data, image_dir=".", processor=processor, is_train=True)
        else:
            raw_data = get_mock_video_data(num_samples=4)
            train_dataset = VideoSafetyDataset(raw_data, video_dir=".", processor=processor, is_train=True)
    else:
        # User production datasets loading
        # To be loaded from actual data structures once downloaded
        # Example setup (placeholder):
        data_dir = config.get("data_dir", "./data")
        raw_train_data = [] # Fetch from CSV or JSON metadata file
        
        if dataset_type == "meme":
            train_dataset = ImageMemeDataset(raw_train_data, image_dir=data_dir, processor=processor, is_train=True)
        else:
            train_dataset = VideoSafetyDataset(raw_train_data, video_dir=data_dir, processor=processor, is_train=True)
            
    collator = VLMDataCollator(processor)
    
    # Setup training arguments
    print("Initializing Trainer...")
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=4 if not args.dry_run else 1,
        learning_rate=lr,
        logging_steps=1 if args.dry_run else 10,
        save_steps=100,
        fp16=not torch.cuda.is_bf16_supported() and torch.cuda.is_available(),
        bf16=torch.cuda.is_bf16_supported() and torch.cuda.is_available(),
        optim="adamw_torch" if not torch.cuda.is_available() else "paged_adamw_8bit",
        gradient_checkpointing=True,
        max_steps=1 if args.dry_run else -1, # Run 1 training step in dry-run mode
        remove_unused_columns=False # Crucial for custom VLM collation
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        data_collator=collator
    )
    
    print("Starting training run...")
    trainer.train()
    print("Training run completed successfully.")
    
    # Save fine-tuned adapter weights
    adapter_output_dir = os.path.join(output_dir, "lora_adapter")
    print(f"Saving fine-tuned LoRA weights to: {adapter_output_dir}...")
    model.save_pretrained(adapter_output_dir)
    print("Save complete.")

if __name__ == "__main__":
    main()
