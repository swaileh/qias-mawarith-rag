# Islamic Inheritance (الميراث) - Fiqh Rules Flowchart

**Mawarith Calculator v2.0** | Visual Decision Trees & Flowcharts

## Main Calculation Pipeline

```mermaid
flowchart TD
    A[Start: Input Heirs] --> B[Validate Input]
    B --> C[Derive Facts]
    C --> D[Apply Disqualifications]
    D --> E[Apply Hajb - Blocking]
    E --> F[Allocate Fard - Fixed Shares]
    F --> G{Sum of Fard > 1?}
    G -->|Yes| H[Apply Awl]
    G -->|No| I[Allocate Asabah - Residuary]
    H --> I
    I --> J{Remainder > 0?}
    J -->|Yes, No Asabah| K[Apply Radd]
    J -->|No| L[Tashih - Base Calculation]
    K --> L
    L --> M[Final Distribution]
```

---

## Spouse Share Decision

```mermaid
flowchart TD
    A[Spouse Present?] -->|Husband| B{Has Descendants?}
    A -->|Wife/Wives| C{Has Descendants?}
    B -->|Yes| D["زوج = 1/4"]
    B -->|No| E["زوج = 1/2"]
    C -->|Yes| F["زوجة = 1/8 shared"]
    C -->|No| G["زوجة = 1/4 shared"]
```

---

## Mother's Share Decision

```mermaid
flowchart TD
    A["أم Present?"] --> B{Has Descendants?}
    B -->|Yes| C["أم = 1/6"]
    B -->|No| D{Siblings >= 2?}
    D -->|Yes| C
    D -->|No| E{الغراوين Case?}
    E -->|Yes| F["أم = 1/3 of Remainder"]
    E -->|No| G["أم = 1/3"]
    
    style C fill:#f9f,stroke:#333
    style F fill:#ff9,stroke:#333
    style G fill:#9f9,stroke:#333
```

---

## Father's Share Decision

```mermaid
flowchart TD
    A["أب Present?"] --> B{Has Male Descendants?}
    B -->|Yes| C["أب = 1/6 فرض"]
    B -->|No| D{Has Female Descendants?}
    D -->|Yes| E["أب = 1/6 + عصبة"]
    D -->|No| F["أب = عصبة فقط"]
    
    style C fill:#f9f,stroke:#333
    style E fill:#ff9,stroke:#333
    style F fill:#9f9,stroke:#333
```

---

## Daughter(s) Share Decision

```mermaid
flowchart TD
    A["بنت Present?"] --> B{Has Son?}
    B -->|Yes| C["بنت = عصبة بالغير 2:1"]
    B -->|No| D{Count = 1?}
    D -->|Yes| E["بنت = 1/2"]
    D -->|No, 2+| F["بنات = 2/3 shared"]
    
    style C fill:#9ff,stroke:#333
    style E fill:#f9f,stroke:#333
    style F fill:#f9f,stroke:#333
```

---

## Son's Daughter Share Decision

```mermaid
flowchart TD
    A["بنت ابن Present?"] --> B{Has Son?}
    B -->|Yes| C[BLOCKED]
    B -->|No| D{Daughters >= 2?}
    D -->|Yes| C
    D -->|No| E{Daughters = 1?}
    E -->|Yes| F["بنت ابن = 1/6 تكملة"]
    E -->|No| G{Count = 1?}
    G -->|Yes| H["بنت ابن = 1/2"]
    G -->|No| I["بنات ابن = 2/3"]
    
    style C fill:#f00,stroke:#333,color:#fff
    style F fill:#ff9,stroke:#333
```

---

## Full Sister Share Decision

```mermaid
flowchart TD
    A["أخت شقيقة Present?"] --> B{Has Full Brother?}
    B -->|Yes| C["عصبة بالغير 2:1"]
    B -->|No| D{Has Female Descendants?}
    D -->|Yes| E["عصبة مع الغير"]
    D -->|No| F{Has Grandfather?}
    F -->|Yes| G{Has Paternal Siblings?}
    G -->|No| H["معاقسمة مع الجد"]
    G -->|Yes| I["فرض Only"]
    F -->|No| J{Count = 1?}
    J -->|Yes| K["أخت = 1/2"]
    J -->|No| L["أخوات = 2/3"]
    I --> J
    
    style C fill:#9ff,stroke:#333
    style E fill:#9ff,stroke:#333
    style H fill:#ff9,stroke:#333
```

---

## Grandfather Best of Three (أحظ الثلاث)

```mermaid
flowchart TD
    A["أب الأب with Siblings"] --> B[Calculate Options]
    B --> C["Option 1: 1/6 of Estate"]
    B --> D["Option 2: 1/3 of Remainder"]
    B --> E["Option 3: Muqasama"]
    
    C --> F[Compare All Options]
    D --> F
    E --> F
    
    F --> G["Select MAX for Grandfather"]
    
    subgraph Muqasama Calculation
    E --> E1["GF = 2 shares"]
    E1 --> E2["Male Siblings = 2 each"]
    E2 --> E3["Female Siblings = 1 each"]
    E3 --> E4["GF Share = 2 / Total"]
    end
```

---

## Blocking Rules (الحجب) Hierarchy

```mermaid
flowchart TD
    subgraph "Descendants Block"
        SON["ابن"] --> GS["ابن ابن"]
        SON --> GD["بنت ابن"]
        SON --> SIBS["All Siblings"]
    end
    
    subgraph "Father Blocks"
        FATHER["أب"] --> GF["أب الأب"]
        FATHER --> SIBS
        FATHER --> UNCLES["All Uncles"]
    end
    
    subgraph "Siblings Block Each Other"
        FB["أخ شقيق"] --> PB["أخ لأب"]
        FB --> PS["أخت لأب"]
        FS2["2+ أخت شقيقة"] --> PS
    end
    
    subgraph "Grandmother Blocking"
        MOTHER["أم"] --> ALL_GM["All Grandmothers"]
        GM2["Level 2 GM"] --> GM3["Level 3 GM"]
    end
    
    style SON fill:#f66,stroke:#333
    style FATHER fill:#f66,stroke:#333
    style MOTHER fill:#f66,stroke:#333
```

---

## Awl (العول) Cases

```mermaid
flowchart LR
    subgraph "Base 6 Awl"
        A6[Base 6] --> A7["→ 7"]
        A6 --> A8["→ 8"]
        A6 --> A9["→ 9"]
        A6 --> A10["→ 10"]
    end
    
    subgraph "Base 12 Awl"
        A12[Base 12] --> A13["→ 13"]
        A12 --> A15["→ 15"]
        A12 --> A17["→ 17"]
    end
    
    subgraph "Base 24 Awl"
        A24[Base 24] --> A27["→ 27"]
    end
```

---

## Residuary (عصبة) Priority Chain

```mermaid
flowchart LR
    A["ابن"] --> B["ابن ابن"]
    B --> C["ابن ابن ابن"]
    C --> D["أب"]
    D --> E["أب الأب"]
    E --> F["أخ شقيق"]
    F --> G["أخ لأب"]
    G --> H["ابن أخ شقيق"]
    H --> I["ابن أخ لأب"]
    I --> J["عم شقيق"]
    J --> K["عم لأب"]
    K --> L["ابن عم شقيق"]
    L --> M["ابن عم لأب"]
    
    style A fill:#9f9,stroke:#333
    style D fill:#9f9,stroke:#333
    style F fill:#9f9,stroke:#333
```

---

## Complete Inheritance Decision Tree

```mermaid
flowchart TD
    START[Estate] --> DEBTS[Deduct Debts & Funeral]
    DEBTS --> WASIYYAH[Deduct Wasiyyah ≤ 1/3]
    WASIYYAH --> NET[Net Estate]
    
    NET --> SPOUSE{Spouse?}
    SPOUSE -->|Yes| SPOUSE_SHARE[Assign Spouse Share]
    SPOUSE -->|No| PARENTS
    SPOUSE_SHARE --> PARENTS
    
    PARENTS{Parents?} -->|Father| FATHER_SHARE[Father Share]
    PARENTS -->|Mother| MOTHER_SHARE[Mother Share]
    PARENTS -->|Both| BOTH_PARENT[Both Shares]
    PARENTS -->|None| DESCENDANTS
    
    FATHER_SHARE --> DESCENDANTS
    MOTHER_SHARE --> DESCENDANTS
    BOTH_PARENT --> DESCENDANTS
    
    DESCENDANTS{Descendants?} -->|Sons| SON_SHARE[Sons Get Residue 2:1]
    DESCENDANTS -->|Daughters Only| DAUGHTER_SHARE[Daughters Fard]
    DESCENDANTS -->|None| SIBLINGS
    
    SON_SHARE --> DONE
    DAUGHTER_SHARE --> SIBLINGS
    
    SIBLINGS{Siblings?} -->|Full| FULL_SIB[Full Sibling Share]
    SIBLINGS -->|Paternal| PAT_SIB[Paternal Sibling Share]
    SIBLINGS -->|Maternal| MAT_SIB[Maternal 1/6 or 1/3]
    SIBLINGS -->|None| EXTENDED
    
    FULL_SIB --> EXTENDED
    PAT_SIB --> EXTENDED
    MAT_SIB --> EXTENDED
    
    EXTENDED{Extended Family?} -->|Uncles/Cousins| UNCLE_SHARE[Residuary Chain]
    EXTENDED -->|None| BAYT_MAL[Bayt al-Mal]
    
    UNCLE_SHARE --> DONE[Calculate Tashih]
    BAYT_MAL --> DONE
```

---

## Legend

| Color | Meaning |
|-------|---------|
| 🟩 Green | Residuary (عصبة) |
| 🟪 Pink | Fixed Share (فرض) |
| 🟨 Yellow | Special Case |
| 🟥 Red | Blocked (محجوب) |
| 🟦 Cyan | Asabah bi-ghayr |
