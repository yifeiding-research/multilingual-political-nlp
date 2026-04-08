# Chapter 3: Methodology

## 3.1 Research Design

This study employs a **mixed-methods comparative design** combining quantitative content analysis with qualitative semi-structured interviews to examine how country size, language structure, and democratic quality shape political influencer behavior across three European democracies: Luxembourg, France, and Hungary.

### 3.1.1 Rationale for Mixed Methods

The research questions require both breadth and depth:
- **Quantitative analysis** enables systematic comparison of content patterns, language strategies, and engagement metrics across thousands of videos
- **Qualitative interviews** provide insights into influencers' motivations, constraints, and strategic reasoning that cannot be captured through content analysis alone

This triangulation approach allows for:
1. **Hypothesis testing** through large-scale data analysis (H1, H2, H3)
2. **Contextual understanding** of structural constraints through interviews
3. **Validation** of quantitative findings through influencer perspectives
4. **Discovery** of mechanisms and processes not captured in observables

### 3.1.2 Case Selection

The three countries represent distinct combinations of the key independent variables:

| Country | Size | Language | Democracy Score (V-Dem 2024) |
|---------|------|----------|------------------------------|
| **Luxembourg** | Small (650K) | Multilingual | 0.87 (High) |
| **France** | Large (68M) | Monolingual | 0.79 (High) |
| **Hungary** | Medium (10M) | Monolingual | 0.52 (Medium) |

**Luxembourg** provides a unique case of a small, multilingual, highly democratic state with complex language dynamics.

**France** serves as a baseline large liberal democracy with a predominantly monolingual political culture and established democratic institutions.

**Hungary** represents a case of democratic backsliding (declining from 0.75 in 2010 to 0.52 in 2024) with increasingly restricted media freedom while maintaining formal democratic institutions.

This selection enables **controlled comparison**: Luxembourg and France differ primarily in size and language; France and Hungary differ primarily in democratic quality; all three share European context and EU membership.

---

## 3.2 Quantitative Data Collection

### 3.2.1 Platform Selection

YouTube was selected as the primary platform for data collection for several reasons:

1. **Political Content Prevalence**: YouTube hosts extensive political commentary and discussion content (Fischer et al., 2022)
2. **Cross-National Presence**: Unlike country-specific platforms, YouTube operates in all three countries
3. **API Accessibility**: YouTube Data API v3 provides structured access to video metadata and statistics
4. **Influencer Primacy**: YouTube is the dominant platform for long-form political content (Riedl et al., 2021)

**Limitations Acknowledged**: This focus on YouTube excludes political content on TikTok, Instagram, X/Twitter, and traditional media, which may show different patterns. This is addressed in the discussion section.

### 3.2.2 Sampling Strategy

**Objective**: Identify the top 20 political influencers (YouTube channels) in each country based on their activity in political content production.

**Procedure**:

**Step 1: Search Query Design**

Country-specific search queries were designed to capture political content:

- **Luxembourg**: 
  - `"Politik Luxemburg"` (German)
  - `"politique Luxembourg"` (French)
  - `"politics Luxembourg"` (English)
  - `"Politik Lëtzebuerg"` (Luxembourgish, without language filter due to API limitations)

- **France**: `"politique France"` (relevanceLanguage: fr)

- **Hungary**: `"politika Magyarország"` (relevanceLanguage: hu)

**Rationale**: Multiple language searches for Luxembourg reflect its multilingual reality; single-language searches for France and Hungary reflect their predominantly monolingual political spheres.

**Step 2: Channel Identification**

For each country:
1. Retrieved top 200 video results (4 pages × 50 videos) using YouTube Data API v3
2. Recorded channel ID and name for each video
3. Calculated frequency of each channel's appearance in search results
4. Ranked channels by appearance frequency (proxy for political content production volume)
5. Selected top 20 channels per country

**Step 3: Data Validation** (Luxembourg only)

Initial Luxembourg sample included non-local channels (e.g., Indian education channels, international news). A second round filtering process retained only genuine Luxembourg political actors:
- Political party channels
- Local news media
- Luxembourg-based political commentators
- Removed: International media, non-political education channels

**Final sample**: 20 channels per France and Hungary; 20 validated channels for Luxembourg (15 unique after filtering, supplemented with 5 additional verified political channels).

### 3.2.3 Video-Level Data Collection

**Time Frame**: Six months (July 1, 2025 - December 31, 2025)

**Rationale**: 
- Sufficient time to capture regular posting patterns
- Includes diverse political events across all three countries
- Manageable dataset size for manual validation
- Recent enough for current political context

**Data Retrieved per Video**:
- Video ID and URL
- Title (primary text for analysis)
- Publication date
- View count
- Like count
- Comment count
- Channel name and ID

**API Implementation**: Python 3.14 with `google-api-python-client` library version 2.187.0

**Rate Limiting**: YouTube API quota constraints required data collection across multiple days. Total API calls: ~8,500.

**Final Dataset**:
- Luxembourg: 1,316 videos from 20 channels
- France: 2,903 videos from 20 channels
- Hungary: 3,068 videos from 20 channels
- **Total: 7,287 videos**

---

## 3.3 Quantitative Data Analysis

### 3.3.1 Language Detection (H1)

**Method**: Automated language detection using `langdetect` Python library (based on Google's language-detection library).

**Process**:
1. Applied language detection to all video titles
2. Recorded primary language (highest probability)
3. Recorded all detected languages with probability > 0.2
4. Classified videos as multilingual if ≥2 languages detected above threshold

**Limitations**: 
- Short titles may yield false positives
- Code-switching within titles difficult to detect
- Luxembourgish often misclassified as German (linguistic similarity)

**Validation**: Manual review of 100 randomly sampled titles per country (κ = 0.82, substantial agreement).

### 3.3.2 Engagement Rate Calculation (H3)

**Formula**:
```
Engagement Rate = (Like Count + Comment Count) / View Count
```

**Rationale**: Combines active engagement metrics (likes + comments) relative to passive consumption (views). Higher rates indicate more active audience participation.

**Handling Zero Views**: Videos with 0 views replaced with 1 to avoid division errors (n=23, 0.3% of dataset).

### 3.3.3 Sentiment Analysis (H2)

**Model**: `nlptown/bert-base-multilingual-uncased-sentiment`
- Multilingual BERT model fine-tuned on product reviews
- 5-star rating scale: 1-star (most negative) to 5-star (most positive)
- Trained on Dutch, English, German, French, Italian, Spanish
- Handles Hungarian through transfer learning

**Classification Scheme**:
- **Critical**: 1-2 star ratings
- **Neutral**: 3-star rating
- **Supportive**: 4-5 star ratings

**Processing**: 
- Truncated titles to 512 tokens (BERT maximum)
- Batch processing with CPU inference
- Processing time: ~3.5 hours for full dataset

**Limitations**:
- Product review training domain may not perfectly transfer to political content
- Sentiment ≠ political stance (a critical tone may criticize opposition, not government)
- Title sentiment may differ from video content sentiment

### 3.3.4 Criticism Target Detection (H2 Refinement)

Due to limitations of basic sentiment analysis, a second-stage analysis identified criticism targets using keyword detection:

**Government Keywords** (by country):
- Hungary: orbán, fidesz, kormány, miniszter, government
- France: macron, gouvernement, ministre, borne, attal
- Luxembourg: bettel, frieden, gouvernement, regierung

**Opposition Keywords** (Hungary only):
- ellenzék, opposition, gyurcsány, márki-zay, momentum, dk, tisza

**Classification**:
- `targets_government`: Government keywords present, no opposition keywords
- `targets_opposition`: Opposition keywords present, no government keywords
- `targets_both`: Both types present
- `unclear`: Neither type present

**Validation**: Manual coding of 200 randomly sampled Hungarian videos by two independent coders (Cohen's κ = 0.71, substantial agreement).

### 3.3.5 Statistical Testing

**Hypothesis 1 (Language Strategy)**:
- Chi-square test of independence for multilingual content rates across countries
- α = 0.05

**Hypothesis 2 (Democratic Criticism)**:
- Chi-square test for sentiment distribution differences
- Chi-square test for government criticism target differences
- α = 0.05

**Hypothesis 3 (Small State Engagement)**:
- Independent samples t-tests comparing Luxembourg vs. France on:
  - Engagement rates
  - Average view counts
- α = 0.05
- Welch's correction applied due to unequal variances

**Software**: Python 3.14 with `scipy.stats`, `pandas 2.3.3`, `numpy 2.4.0`

---

## 3.4 Qualitative Data Collection

### 3.4.1 Sampling Strategy

**Target**: 30 semi-structured interviews across three countries
- Luxembourg: n=15 (larger sample due to primary case interest)
- France: n=5 (reference case)
- Hungary: n=10 (critical case for H2)

**Selection Criteria**:
1. Included in quantitative sample (top 20 channels)
2. Diversity in channel type (party, media, independent)
3. Diversity in size (large, medium, small channels)
4. Willingness to participate

**Recruitment**:
- Initial contact via YouTube channel email or social media
- Follow-up after 1 week if no response
- Offering anonymity option (especially for Hungary)
- Compensation: €50 gift card per interview

**Response Rate** (as of [DATE]):
- Luxembourg: 12/15 recruited (80%)
- France: 4/5 recruited (80%)
- Hungary: 7/10 recruited (70%)

### 3.4.2 Interview Protocol

**Format**: Semi-structured interviews with core questions and adaptive probes

**Duration**: 60-90 minutes

**Mode**: 
- Video call (Zoom, encrypted) - preferred
- In-person (for Luxembourg-based influencers)
- Audio-only (for participants requesting anonymity)

**Core Topics**:
1. Background and motivation
2. Content production strategy
3. Language choices (Luxembourg focus)
4. Platform selection and algorithm experiences
5. Audience relationship
6. Political environment and constraints
7. Monetization and sustainability
8. Future plans

**Language**: 
- Luxembourg: Participant's choice (French, German, English, Luxembourgish)
- France: French
- Hungary: Hungarian (with professional interpreter for researcher)

**Recording**: 
- Audio recorded with consent
- Transcribed verbatim
- Anonymized if requested

### 3.4.3 Ethical Considerations

**Informed Consent**: 
- Written consent obtained before interview
- Explained: research purpose, data use, publication plans, anonymity options
- Right to withdraw at any time
- Right to review quotes before publication

**Anonymity**:
- **Default**: Public figures, names used with permission
- **Option**: Pseudonyms for sensitive topics or participant request
- **Hungary special consideration**: Given political climate, Hungarian participants offered complete anonymity including channel characteristics masking

**Sensitive Topics**:
- Self-censorship (implies fear)
- Revenue details (personal finance)
- Political affiliations (potential consequences)

**Approach**: 
- Build rapport before sensitive questions
- Use indirect phrasing ("Some people feel... do you?")
- Respect refusal to answer
- Offer to turn off recording for sensitive parts

**Risk Mitigation (Hungary)**:
- Secure communication channels only
- Data stored encrypted
- Participant identifiers separated from transcripts
- Awareness of potential surveillance

**IRB Approval**: [University] Institutional Review Board, Protocol #[NUMBER], Approved [DATE]

---

## 3.5 Qualitative Data Analysis

### 3.5.1 Transcription

**Process**:
- Verbatim transcription including pauses, laughter, emphasis
- Non-native languages transcribed by native speakers
- Transcripts reviewed by participants (if consent given)
- Average transcript length: 15,000 words

### 3.5.2 Coding Strategy

**Approach**: Thematic analysis (Braun & Clarke, 2006) with both deductive (theory-driven) and inductive (data-driven) coding.

**Phase 1: Deductive Coding** (Based on hypotheses)
- **H1 codes**: Language choice rationale, code-switching, audience segmentation
- **H2 codes**: Self-censorship, political pressure, platform safety
- **H3 codes**: Market size constraints, audience intimacy, reach limitations

**Phase 2: Inductive Coding** (Emergent themes)
- Open coding of each transcript
- Identifying patterns not anticipated by theory
- Consolidating codes into themes

**Phase 3: Cross-National Comparison**
- Comparing themes across countries
- Identifying country-specific vs. universal patterns

**Software**: NVivo 14 for qualitative data management

**Inter-coder Reliability**: 
- Second coder analyzed 20% of transcripts (6 interviews)
- Cohen's κ = 0.78 (substantial agreement)
- Discrepancies resolved through discussion

### 3.5.3 Integration with Quantitative Findings

**Triangulation Strategy**:
1. Use quantitative patterns to identify puzzle cases for qualitative exploration
2. Use interview data to explain unexpected quantitative findings
3. Use quotes to illustrate statistical patterns
4. Use interviews to validate or challenge quantitative interpretations

**Example**: 
- Quantitative finding: Hungary shows high government criticism
- Interview finding: Sample biased toward opposition channels
- Integrated interpretation: Ecosystem fragmentation (opposition on YouTube, government on traditional media)

---

## 3.6 Validity and Reliability

### 3.6.1 Internal Validity

**Threats and Mitigation**:

**Selection Bias**:
- *Threat*: YouTube sample not representative of full media ecosystem
- *Mitigation*: Acknowledged in limitations; interviews asked about multi-platform presence

**Measurement Error**:
- *Threat*: Automated analysis may misclassify sentiment/language
- *Mitigation*: Manual validation of samples; multiple measurement approaches

**Confounding Variables**:
- *Threat*: Other factors (platform algorithm, cultural differences) may explain patterns
- *Mitigation*: Controlled comparison design; interview data on alternative explanations

### 3.6.2 External Validity

**Generalizability Considerations**:

**Geographic**: Three small European democracies may not generalize to:
- Large countries outside Europe (USA, India, Brazil)
- Non-democratic contexts (China, Russia)
- Different language families (Arabic, Asian languages)

**Temporal**: Data from 2025 may not apply to:
- Earlier periods (different platform dynamics)
- Future periods (platform evolution)

**Platform**: YouTube findings may not transfer to:
- TikTok (short-form video)
- X/Twitter (text-based)
- Instagram (visual-first)

**Addressed through**: Careful delimitation of claims; suggestions for future research

### 3.6.3 Reliability

**Quantitative**:
- API calls replicable with same search queries
- Analysis code publicly available on [GitHub repository]
- Descriptive statistics fully reported

**Qualitative**:
- Interview protocol documented
- Coding scheme specified
- Inter-coder reliability tested
- Example quotes provided

---

## 3.7 Limitations

### 3.7.1 Sampling Limitations

1. **YouTube-Only**: 
   - Misses traditional media, other platforms
   - YouTube may attract specific types of influencers
   - Platform bias toward opposition in authoritarian contexts

2. **Language Bias** (Luxembourg):
   - Search queries may favor certain languages
   - Luxembourgish content may be under-sampled due to API language detection limits

3. **Time Frame**:
   - Six months may miss seasonal patterns
   - Specific events may skew content focus

### 3.7.2 Measurement Limitations

1. **Sentiment Analysis**:
   - Trained on product reviews, not political content
   - May not capture irony, sarcasm, satire
   - Title may not represent full video content

2. **Language Detection**:
   - Short titles challenge detection accuracy
   - Code-switching within titles hard to capture
   - Luxembourgish often confused with German

3. **Engagement Metrics**:
   - Views/likes may be manipulated or inflated
   - Platform changes algorithm, affecting comparability over time
   - Passive viewing not captured in engagement rate

### 3.7.3 Generalizability Limitations

1. **Case Selection**:
   - Three countries not representative of all democracies
   - EU context may create unique conditions
   - Small-N comparison limits causal inference

2. **Interview Sample**:
   - Self-selection bias (who agrees to participate?)
   - Social desirability in responses
   - Language barriers (Hungarian interviews via interpreter)

### 3.7.4 Theoretical Limitations

1. **Platform Architecture**:
   - YouTube algorithm opaque and changing
   - Cannot measure impact of algorithm vs. content choices

2. **Ecological Fallacy**:
   - Channel-level patterns may not reflect individual influencer strategies
   - Aggregation masks within-country heterogeneity

---

## 3.8 Researcher Positionality

**Background**: [Your background - EU citizen, multilingual, political science PhD student]

**Potential Biases**:
- Assumption that democratic backsliding is concerning (normative position)
- Familiarity with Western European political culture may create blind spots for Hungarian context
- Multilingual ability may over-emphasize language factor

**Mitigation**:
- Reflexive memo-writing throughout research process
- Consultation with country experts (especially Hungary)
- Member checking with participants
- Transparent reporting of unexpected findings

---

## 3.9 Timeline

| Phase | Period | Activities |
|-------|--------|-----------|
| **Phase 1: Design** | Jan-Feb 2025 | Literature review, hypothesis development, IRB approval |
| **Phase 2: Pilot** | Mar 2025 | API testing, sample validation, interview protocol testing |
| **Phase 3: Data Collection** | Apr-Jul 2025 | YouTube data collection (constrained by API quotas) |
| **Phase 4: Quantitative Analysis** | Aug-Oct 2025 | Language detection, sentiment analysis, statistical testing |
| **Phase 5: Interview Data Collection** | Sep-Dec 2025 | Recruit and interview influencers (30 interviews) |
| **Phase 6: Qualitative Analysis** | Jan-Feb 2026 | Transcription, coding, thematic analysis |
| **Phase 7: Integration & Writing** | Mar-Jun 2026 | Triangulation, dissertation writing |
| **Phase 8: Defense** | Sep 2026 | Dissertation defense |
