# SafeAd AI - API Documentation

## Base URL
Default local development base URL: `http://localhost:8000/api/v1`

---

## Endpoints Summary

| Endpoint | Method | Description | Access |
| :--- | :--- | :--- | :--- |
| `/advertisements/analyze` | `POST` | Upload media & perform full multimodal SafeAd moderation. | Public / Client |
| `/moderate` | `POST` | Perform quick payload analysis on text or image URLs. | Public / Client |
| `/admin/pending` | `POST` | Retrieve queue of ads requiring Human-in-the-Loop review. | Admin / Moderator |
| `/admin/override` | `POST` | Manually override safety classification & risk decision. | Admin / Moderator |
| `/health` | `GET` | Health check endpoint returning API operational status. | Public |

---

## 1. Upload & Analyze Advertisement

### Endpoint
`POST /api/v1/advertisements/analyze`

### Content Type
`multipart/form-data`

### Request Parameters

| Field Name | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `title` | string | Yes | Title of the advertisement. |
| `description` | string | No | Full advertisement copy or caption text. |
| `user_dob` | string | No | User date of birth (`YYYY-MM-DD`) for age verification. |
| `file` | UploadFile | No | Media file (JPEG, PNG, MP4, AVI, MOV). |
| `face_file` | UploadFile | No | Optional user face photo for age-confidence estimation. |

### Sample Response (`200 OK`)
```json
{
  "id": 42,
  "title": "Crypto Money Doubler Special",
  "classification": "UNSAFE_FOR_ALL",
  "publication_action": "REJECT",
  "risk_score": 95.0,
  "confidence": 0.92,
  "requires_human_review": false,
  "explanation": "High ad risk detected: Deceptive marketing / scam terms found in text copy: 'double your money', '100% guaranteed return'.",
  "assessment_matrix": {
    "visual_score": 0.05,
    "violence_score": 0.0,
    "ocr_text": "DOUBLE YOUR INVESTMENTS IN 24 HOURS GUARANTEED",
    "audio_transcript": "Sign up today and get double your deposit guaranteed",
    "text_safety_score": 0.85,
    "ad_risk_score": 95.0,
    "ad_risk_flags": [
      "DECEPTIVE_GUARANTEE: Found 'guaranteed return'",
      "SCAM_PROMISE: Found 'double your money'"
    ]
  },
  "user_age_analytics": {
    "chronological_age": 24,
    "estimated_age": 25,
    "age_difference": 1,
    "age_confidence": 0.98
  }
}
```

---

## 2. Quick Moderate Payload

### Endpoint
`POST /api/v1/moderate`

### Content Type
`application/json`

### Request Payload
```json
{
  "text": "Organic apples on sale for $2 a pound",
  "user_dob": "2000-05-15"
}
```

### Sample Response (`200 OK`)
```json
{
  "classification": "SAFE_FOR_ALL",
  "publication_action": "APPROVE",
  "risk_score": 5.0,
  "confidence": 0.95,
  "requires_human_review": false,
  "explanation": "No safety violations or ad risks detected across modalities."
}
```

---

## 3. Get Pending Human-in-the-Loop Queue

### Endpoint
`POST /api/v1/admin/pending` (or `GET /api/v1/admin/pending`)

### Query / Body Parameters
* `limit` (int, default=50): Number of pending records to return.

### Sample Response (`200 OK`)
```json
{
  "count": 1,
  "items": [
    {
      "id": 18,
      "title": "Crypto Trading Bot",
      "risk_score": 52.0,
      "confidence": 0.58,
      "requires_human_review": true,
      "classification": "REQUIRES_HUMAN_REVIEW",
      "reason": "Borderline risk score (52.0) and low confidence (0.58) across OCR and text copy."
    }
  ]
}
```

---

## 4. Admin Override Decision

### Endpoint
`POST /api/v1/admin/override`

### Request Payload (`application/json`)
```json
{
  "advertisement_id": 18,
  "classification": "SAFE_18_PLUS",
  "publication_action": "AGE_RESTRICT",
  "moderator_notes": "Reviewed by Moderator #4: Certified trading app, approved for 18+ audience."
}
```

### Sample Response (`200 OK`)
```json
{
  "status": "success",
  "advertisement_id": 18,
  "new_classification": "SAFE_18_PLUS",
  "publication_action": "AGE_RESTRICT",
  "message": "Moderation status updated successfully by human review."
}
```

---

## 5. Health Check Endpoint

### Endpoint
`GET /api/v1/health`

### Sample Response (`200 OK`)
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "models_loaded": {
    "vision": true,
    "videomae": true,
    "ocr": true,
    "whisper": true,
    "ad_risk": true
  }
}
```
