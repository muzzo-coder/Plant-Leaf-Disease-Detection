# LeafAI API Specification

## `POST /api/predict`
Accepts a plant leaf image, evaluates it using the core TensorFlow model, and returns a detailed agricultural diagnosis referencing our extensive Knowledge Base.

**Content-Type:** `multipart/form-data`

### Request Body
| Key | Type | Description |
|-----|------|-------------|
| `image` (or `file`) | **File** | The image file containing the leaf. Valid formats: `png`, `jpg`, `jpeg`. Max size: 16 MB. |

---

### Responses

#### 🟢 Success (200 OK)
When a valid plant leaf is confidently predicted:
```json
{
  "success": true,
  "is_plant": true,
  "confidence": 0.985,
  "image_url": "/static/upload/unique_id_image.jpg",
  "result": {
    "name": "Target Spot",
    "description": "Produces dark brown necrotic lesions on leaves...",
    "causes": "Caused by the fungus Corynespora cassiicola...",
    "organic_treatment": "Remove heavily diseased leaves...",
    "chemical_treatment": "Protect crops with broad-spectrum fungicides...",
    "prevention_steps": "Provide excellent canopy airflow...",
    "care_tips": "Prune suckers and lower branches...",
    "severity": "High"
  }
}
```

#### 🟡 Uncertain / Non-Plant (200 OK)
When the model's highest probability falls below the confidence threshold (`< 0.45`):
```json
{
  "success": true,
  "is_plant": false,
  "confidence": 0.35,
  "message": "Unable to confidently detect disease. Please upload a clearer, closer image of the plant leaf."
}
```

#### 🔴 Client Errors (400 / 413)
Validation errors:
```json
{
  "success": false,
  "error": "Invalid file format. Only JPG, JPEG, and PNG are allowed."
}
```

#### ⚫ Server Error (500 / 503)
Infrastructure issues (e.g., model failed to load):
```json
{
  "success": false,
  "error": "ML Service unavailable."
}
```
