# 🧠 ML Model Improvement Pipeline

To elevate this application to an industry-grade agronomy platform, a structured Machine Learning pipeline is required. The current prototype relies on an initial static Keras model. Moving to a sustainable format involves the following pipeline strategy:

## Phase 1: Data Acquisition & Synthetic Augmentation
1. **Multi-Crop Sourcing**: Gather datasets beyond Tomatoes (e.g., Potatoes, Corn, Apple, Grape) from curated sources like PlantVillage and Kaggle.
2. **Augmentation Pipeline (`tf.image` / `Albumentations`)**:
   - Apply random rotations (±45°).
   - Horizontal and Vertical flipping.
   - Contrast/Brightness random jitters to simulate different times of day/weather.
   - **CutMix / MixUp integration** to avoid over-confident predictions on specific leaf textures.

## Phase 2: Architecture Upgrade (Transfer Learning)
1. Drop the custom Sequential CNN.
2. Initialize **`EfficientNetB0`** or **`MobileNetV3`** pre-trained on ImageNet.
   - *Why:* These networks are optimized for mobile environments where memory footprint matters, offering 95%+ top-1 accuracy without the 100MB+ overhead of older structures like VGG16.
3. Pop the top variable layer, freeze base layers, and apply Global Average Pooling followed by a Dense classification head (Softmax/Sigmoid).

## Phase 3: Out-of-Distribution (OOD) Handling
1. **"Not a Leaf" Class**: Intentionally train the model on a repository of random background images (hands, soil, sky, tools) mapped to a distinct "Background/Noise" class.
2. **Confidence Thresholding API**: Currently mocked in `services/prediction_service.py`. A dynamic thresholding algorithm should be validated through an F1-score evaluation against a holdout dataset.

## Phase 4: CI/CD for Model Weights
1. Transition from committing `model.h5` into Git towards utilizing an S3 Bucket or MLFlow tracking server.
2. Run nightly automated regression tests in GitHub Actions verifying that the latest weights do not introduce catastrophic forgetting of early disease markers.
