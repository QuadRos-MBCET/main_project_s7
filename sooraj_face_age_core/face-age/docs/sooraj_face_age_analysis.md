# Face Age Analysis

## Current Face Detection Approach
The project directory was empty, so there was no existing implementation. 

## Proposed Replacement/Improvement
We implemented a robust pipeline using:
- **MTCNN** (via `facenet-pytorch`) for face detection and cropping.
- **ViT Age Classifier** (`nateraw/vit-age-classifier`) via Hugging Face `transformers` for estimating age buckets.

## Files Added
- `ai/face_age/__init__.py`
- `ai/face_age/face_detector.py`
- `ai/face_age/age_estimator.py`
- `ai/face_age/face_age_pipeline.py`
- `ai/face_age/model_manager.py`
- `ai/face_age/utils.py`
- `configs/face_age_config.yaml`
- `tests/test_face_age.py`
- `notebooks/sooraj_face_age_colab.ipynb`
- `docs/sooraj_face_age_analysis.md`

## Model Selection for Age Estimation
Selected `nateraw/vit-age-classifier` because:
- It returns distinct age buckets along with confidence scores.
- It is well documented and compatible with Colab's Free Tier.
- It relies on Hugging Face transformers which are easy to load and test.

## Colab Compatibility Considerations
The pipeline checks for CUDA availability using `torch.cuda.is_available()`. In a free Colab notebook, if GPU is available, it mounts models on the GPU, otherwise falls back to CPU. Memory is actively managed by deleting references and calling `gc.collect()` and `torch.cuda.empty_cache()` at the end of the analysis pipeline.
