# DC Consulting: Asset and Implementation Plan

## 1. Executive Summary & Asset Architecture
Per user directive, all vector illustrations were superseded by real, photographic, high-fidelity editorial imagery to align with DC Consulting's institutional B2B identity. 

Thirteen original editorial photos (`Gemini_Generated_Image.jpeg` through `Gemini_Generated_Image-13.jpeg`) plus the custom hero slate background (`hero_background.png`) were reviewed, renamed semantically, converted into modern responsive formats (AVIF, WebP, progressive JPEG at 480w, 800w, 1200w, 1400w), and integrated into the static multi-page website across all 6 core pages.

---

## 2. Master Asset Inventory & Renaming Map

| Original File | Semantic Name | Dimensions | Primary Page / Section | Subject & Contextual Caption |
|---|---|---|---|---|
| `hero_background.png` | `hero-slate-{800,1240}.{webp,jpg}` | 1240×700 | **Home**: Hero Background | Dark natural slate texture with custom navy contrast gradient overlay (>7:1 text contrast). |
| `Gemini_Generated_Image.jpeg` | `commodity-gems-display` | 1400×788 | **Home**: Commodity Card<br>**Commodities**: Gemstones | Rough parcels and faceted certified gemstones with gemmological loupe.<br>*"Rough parcels and cut stones under insured vault-to-vault transport."* |
| `Gemini_Generated_Image-2.jpeg` | `logistics-intermodal-hub` | 1400×788 | **Services**: Stage 4 Logistics | Intermodal freight logistics hub coordinating container trucks, rail and air cargo.<br>*"Stage 4: Vessel chartering, containerized freight and secured vault-to-vault air transport."* |
| `Gemini_Generated_Image-3.jpeg` | `compliance-documentation-desk` | 1400×788 | **Services**: Stage 3 Docs<br>**Compliance**: The Document Set | Official export documentation desk with wax seal, stamp, and bound dossiers.<br>*"Full dossier verification: origin certificates, export clearances and bankable LC documents."* |
| `Gemini_Generated_Image-4.jpeg` | `processing-facility-plant` | 1400×788 | **Services**: Stage 2 Process<br>**Commodities**: Other Materials | Industrial minerals processing facility with conveyor systems and refining reactors.<br>*"Stage 2: Milling, chemical beneficiation and grade alignment to buyer specification."* |
| `Gemini_Generated_Image-5.jpeg` | `inspection-geological-assay` | 1400×788 | **Compliance**: Three Checkpoints | Geological surveyor conducting on-site ore assay with magnifying loupe and specimens.<br>*"Independent surveyor access at origin, loading port and destination discharge."* |
| `Gemini_Generated_Image-6.jpeg` | `commodity-rare-earths-specimen` | 1400×788 | **Home**: Commodity Card<br>**Commodities**: Rare Earths | Mineral specimen under precision laboratory lighting with specialist gloved hands.<br>*"Separated oxides and mineral concentrates verified by buyer-appointed ICP-MS assay."* |
| `Gemini_Generated_Image-7.jpeg` | `leadership-director-portrait` | 1200×900 | **About**: Message from Leadership | Executive Managing Director portrait in modern architectural boardroom.<br>*"Executive Leadership: Managing Director & Head of Physical Execution."* |
| `Gemini_Generated_Image-8.jpeg` | `global-trade-routes-office` | 1400×788 | **Home**: Hero Process Card<br>**About**: Where We Fit | Executive boardroom overlooking illuminated global supply trade route mapping.<br>*"Global trade routes: linking origin concessions directly to corporate buyer discharge ports."* |
| `Gemini_Generated_Image-9.jpeg` | `logistics-charter-operations` | 1400×788 | **Contact**: Aside Operations | Marine cargo superintendent coordinating bulk vessel charter and loading operations.<br>*"Active mandate supervision: direct coordination from origin to discharge."* |
| `Gemini_Generated_Image-10.jpeg` | `corporate-mandate-execution` | 1400×788 | **About**: Who We Are | Executive reviewing physical procurement agreements under confidentiality terms.<br>*"Physical execution bound by written non-circumvention agreements."* |
| `Gemini_Generated_Image-11.jpeg` | `commodity-crude-oil-refinery` | 1400×788 | **Home**: Commodity Card<br>**Commodities**: Crude Oil | Coastal refinery and marine terminal storage tanks with terminal lifting notebook.<br>*"Terminal lifting, shore tank and vessel surveyor inspection for crude and refined distillates."* |
| `Gemini_Generated_Image-12.jpeg` | `sourcing-gemstone-tender` | 1400×788 | **Services**: Stage 1 Sourcing | Origin allocation and tender parcel documentation for mineral and gem contracts.<br>*"Stage 1: Concession title verification, origin allocation and parcel inspection."* |
| `Gemini_Generated_Image-13.jpeg` | `port-container-terminal` | 1400×788 | **Home**: Engagement Runs | Deep-sea container terminal with gantry cranes handling strategic export cargo.<br>*"From origin extraction to international port delivery."* |

---

## 3. Technical Implementation & Styling Standards

1. **Responsive Picture Elements (`editorial_picture` helper)**:
   - Evaluates multi-source responsive formats: AVIF (primary), WebP (secondary), progressive JPEG (fallback).
   - Responsive `srcset` across 480w, 800w, 1200w, and 1400w variants using `sizes="(min-width: 900px) ...px, 100vw"`.
   - Explicit `width` and `height` attributes to prevent Cumulative Layout Shift (CLS).
   - Default `loading="lazy"` and `decoding="async"` (above-the-fold hero elements eager).

2. **CSS Media Frame Design (`src/css/styles.css`)**:
   - `.media-frame`: Soft 1px border (`var(--line)`), rounded corners (`var(--radius)`), subtle drop shadow (`var(--shadow)`), and smooth hover highlight (`var(--bronze-line)`).
   - `.editorial-img`: Aspect ratio locked to `16/9` (or `4/3` for portraits), `object-fit: cover`.
   - `.media-caption`: Muted editorial caption strip below image (`var(--paper)` background with 1px top border) contextualizing the visual with page text.
   - `.commodity-grid`: 2-column split layout for commodity detail sections (1.15fr facts / 0.85fr visual frame).
   - `.service-split`: 2-column responsive layout pairing stage descriptions with full-width editorial frames.

3. **Performance & Asset Footprint**:
   - Automated conversion via `tools/optimize_editorial.py` with Pillow.
   - Total payload per page reduced significantly with AVIF/WebP while retaining crisp editorial fidelity.
