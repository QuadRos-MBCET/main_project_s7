@echo off
title SafeAd AI - Video Content Policy Accuracy Benchmark
echo =====================================================================
echo    SafeAd AI - Video Content Policy Accuracy Benchmark
echo    Dataset: https://github.com/QuadRos-MBCET/safead-dataset-hub
echo =====================================================================
cd /d "%~dp0"
set PYTHONPATH=%CD%;%CD%\joseph_safead_core;%CD%\sooraj_face_age_core\face-age
python tests\evaluate_hub_dataset.py
pause
