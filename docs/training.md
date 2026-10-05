# Training
Use `python -m ml.training.train_unet --config ml/configs/unet_baseline.yaml` for segmentation training. Roof baseline: `python -m ml.training.train_roof --input-csv ... --output artifacts/roof_rf.joblib`. Only real labelled data/checkpoints should be registered.
