# SafeAd AI: System Design Diagrams

This document compiles the architectural flow, class structures, UML use cases, and Data Flow Diagrams (DFDs) for the **SafeAd AI** content safety engine.

---

## 👥 SafeAd AI UML Use Case Diagram

![SafeAd AI Use Case Diagram](./safead_use_case_diagram_1786244555881.jpg)

### Interactive Mermaid Use Case representation:

```mermaid
usecaseDiagram
    actor Advertiser as "Advertiser"
    actor SocialUser as "Social User"
    actor Admin as "Platform Admin"
    
    rectangle "SafeAd AI System Boundary" {
        usecase UC1 as "Submit Ad Campaign"
        usecase UC2 as "Pre-Pub Risk Scan"
        usecase UC3 as "Perform Age Estimation"
        usecase UC4 as "Filter Age-Restricted Ads"
        usecase UC5 as "Review CoT Audit Logs"
    }
    
    Advertiser --> UC1
    
    SocialUser --> UC4
    
    Admin --> UC2
    Admin --> UC4
    Admin --> UC5
    
    %% Relationships between internal use cases
    UC2 ..> UC3 : <<include>>
    UC3 ..> UC4 : <<triggers>>
```

---

## 🔄 Data Flow Diagram (DFD Level 0 - Context Diagram)

DFD Level 0 models the overall boundary of the system as a single process and its interactions with external entities:

![SafeAd AI DFD Level 0 Context Diagram](./safead_dfd_level_0_1786245777157.jpg)

### Interactive Mermaid DFD Level 0 Flow:

```mermaid
graph LR
    Advertiser["Advertiser (External Entity)"]
    SocialUser["Social User (External Entity)"]
    Admin["Platform Admin (External Entity)"]
    
    System("(1.0) SafeAd AI System")
    
    Advertiser -- "Submit Ad (Keyframes, OCR, Audio)" --> System
    System -- "Moderation Status & Rationale" --> Advertiser
    
    SocialUser -- "View Ad Request" --> System
    System -- "Filtered, Age-Appropriate Ads" --> SocialUser
    
    Admin -- "Upload Policy Rules" --> System
    System -- "Chain-of-Thought Audit Logs" --> Admin
```

---

## 🔄 Data Flow Diagram (DFD Level 1 - Detailed Process Flow)

DFD Level 1 breaks down the SafeAd AI System process block into sub-processes, data stores, and internal data routes:

![SafeAd AI DFD Level 1 Process Diagram](./safead_dfd_level_1_1786245794530.jpg)

### Interactive Mermaid DFD Level 1 Flow:

```mermaid
graph TD
    Advertiser["Advertiser"]
    SocialUser["Social User"]
    Admin["Platform Admin"]
    
    P1["(1.1) Preprocess Ad Input"]
    P2["(1.2) Estimate Target Age"]
    P3["(1.3) Query FAISS Index"]
    P4["(1.4) VLM Moderation Engine"]
    
    D1[("D1: Ads & Metadata Database")]
    D2[("D2: Policy Rules Index")]
    D3[("D3: CoT Audit Logs Store")]
    
    Advertiser -- "Ad Campaign Data" --> P1
    P1 -- "Keyframes, OCR & Transcripts" --> D1
    P1 -- "Face & OCR Text Features" --> P2
    P1 -- "Preprocessed Multimodal Vectors" --> P4
    
    SocialUser -- "Request Ad View" --> P2
    P2 -- "Verified User Age Group" --> P4
    
    Admin -- "Policy Rule Entries" --> D2
    D2 -- "Similar Policy Exemplars" --> P3
    P3 -- "Retrieved Policy Context" --> P4
    
    P4 -- "Moderation Flag & Decision" --> D1
    P4 -- "Chain-of-Thought Rationale Logs" --> D3
    
    D1 -- "Ad Review Status" --> Advertiser
    D1 -- "Approved Age-Appropriate Ads" --> SocialUser
    D3 -- "Review Audit Logs" --> Admin
```

---

## 🏛️ UML Class Diagram

```mermaid
classDiagram
    direction TB
    
    class AdItemInput {
        +String adID
        +List~Image~ keyframes
        +String textOCR
        +String audioTranscript
        +preprocess() void
    }

    class AgeEstimationEngine {
        +CNNModel faceNet
        +BERTModel textNLP
        +estimateUserAge() AgeBracket
        +verifyAccess() boolean
    }

    class FAISSVectorIndex {
        +IndexFlatIP index
        +searchExemplars() List~Case~
    }

    class AdModerationEngine {
        +MLLM vlmModel
        +List~Rule~ policyRules
        +analyzeAd() Result
        +generateCoTRationale() String
    }

    AdItemInput --> AdModerationEngine : feeds preprocessed inputs
    AdItemInput --> AgeEstimationEngine : sends face & text features
    AgeEstimationEngine --> AdModerationEngine : provides verified age brackets
    FAISSVectorIndex --> AdModerationEngine : retrieves contextual exemplars
```
