# The ML / Data Science / AI Resume — Complete Reference

A practitioner-grade guide for **ML Engineer, Data Scientist, Research Scientist, and AI Engineer** roles. Sourced from university career centers (MIT, Harvard), Laszlo Bock / Google's published guidance, the Tech Interview Handbook, and ML-specific career resources. Every URL is in **Sources** at the end.

> Line-width rules live in `SKILL.md` (LINE-WIDTH BUDGET). TL;DR: cventry bullets render in `\small`, target **115–120 characters** per bullet (hard ceiling ~123 before it wraps).

---

## 0. The non-negotiables (quick checklist)
- [ ] One page (students / <~8 yrs exp).
- [ ] **Every bullet = exactly one line.** No wrap, no 2-word orphan line, no big end-of-line gap.
- [ ] Every bullet leads with a strong **action verb** and carries a **number**.
- [ ] XYZ formula: *Accomplished X, measured by Y, by doing Z.*
- [ ] Reverse-chronological in every section.
- [ ] **No personal pronouns** ("Led team of 8," not "I led…"). Phrases, not sentences.
- [ ] Consistent tense (past for past roles, present for current).
- [ ] Single column, **no tables/text-boxes/images/graphics** (ATS-breakers). Submit PDF.
- [ ] Skills section is keyword-rich and matches the job description's exact terms.

---

## 1. The Google XYZ Formula

**Origin:** Laszlo Bock, Google's former SVP of People Operations, in *"My Personal Formula for a Winning Resume"* (LinkedIn) and *Work Rules!*. Google recruiters publicly endorse it.

**Formula (verbatim):**
> **"Accomplished [X] as measured by [Y], by doing [Z]."**

- **X** = what you accomplished (lead with a strong verb)
- **Y** = how it was measured (the number / metric / baseline that proves impact)
- **Z** = how you did it (method, tools, technique — where ML credibility + ATS keywords live)

**Bock's own example:**
- Weak: *"Studied financial performance of companies and made investment recommendations."*
- XYZ: *"Improved portfolio performance by 12% ($1.2M) over one year by refining cost of capital calculations for information-poor markets and re-weighting portfolio based on resulting valuations."*

The % shows improvement, the $ proves it mattered, the "by doing Z" adds credibility and reveals real skill.

**Mapping XYZ to ML:**
| Component | ML mapping |
|---|---|
| X (accomplishment) | Shipped a model / pipeline / system that changed a product or research outcome |
| Y (measurement) | F1/AUC/accuracy lift, latency/throughput, $ saved, A/B lift, data scale, training-time cut |
| Z (method) | Architecture (transformer, GBDT, CNN), framework (PyTorch/TF/JAX), technique (distillation, quantization, DDP) |

**Good ML XYZ bullets:**
- *"Cut fraud false-positive rate from 8% to 3% (~$108K/mo saved) by replacing a logistic baseline with a gradient-boosted classifier and recalibrating thresholds."*
- *"Reduced p95 inference latency 55% (420ms → 190ms) by exporting to TorchScript and serving via TensorRT on Triton."*
- *"Increased search CTR +4.2% in a 2-week A/B test across 12M users by fine-tuning a BERT re-ranker on click logs."*
- *"Shrank training time from 14 days to 18 hours by parallelizing across 64 A100 GPUs with PyTorch DDP and mixed precision."*

---

## 2. STAR vs XYZ — when to use which

**STAR** = Situation, Task, Action, Result — a *storytelling* structure.

| | XYZ | STAR |
|---|---|---|
| Use for | **Resume bullets** | **Behavioral interviews** |
| Length | One tight line | Short paragraph / spoken answer |
| Optimized for | 6–10s recruiter scan, quantified impact | Context + your role + reasoning |
| ML fit | Default for every bullet | To *talk about* the bullet live |

**Rule:** Write the resume in **XYZ** (compresses Situation/Task into the verb, foregrounds Result). Keep a **STAR** version of each bullet in a prep doc for interviews. Don't force XYZ where there's no metric — but in ML you almost always have one.

---

## 3. Quantifying ML impact — metrics that matter

Recruiters spend ~6–10s per bullet; numbers register. A bullet without a number reads as a job duty.

**Metric menu:**
- **Model quality:** accuracy, precision/recall, **F1**, AUC/ROC, RMSE/MAE, perplexity, BLEU/ROUGE, mAP — *always show lift or baseline* (78% → 93%), not just the endpoint.
- **Latency/throughput:** p50/p95/p99 latency, QPS, tokens/sec, batch throughput.
- **Cost/efficiency:** $ saved, GPU-hours, cloud-spend %, model-size reduction (4× via quantization).
- **Scale:** rows/events, parameters, dataset TB, users served (100M+), requests/day.
- **Training:** wall-clock training time cut, # GPUs, convergence speedup.
- **Business:** A/B lift, revenue, retention, conversion, churn, tickets deflected.
- **Research:** SOTA delta vs prior work, benchmark rank, citations, venue.

**Good vs bad:**
| Bad (vague / duty) | Good (XYZ + metric) |
|---|---|
| "Built a machine learning model to detect spam." | "Reduced user-reported spam 15% by training a calibrated XGBoost classifier on 40M labeled emails." |
| "Worked on improving model accuracy." | "Raised intent-classification F1 from 0.81 to 0.92 by adding back-translation augmentation and focal loss." |
| "Responsible for model deployment." | "Deployed 12 models to prod via SageMaker + Docker, sustaining 3K QPS at p99 < 120ms." |
| "Used PyTorch for deep learning projects." | "Trained a 350M-param transformer in PyTorch (DDP, 32 GPUs), cutting training cost 40% with mixed precision." |

No number available? Quantify *scale* (data size, # models, team size), *relative* improvement, or a qualitative first ("first production CV model for the team").

---

## 4. Action verbs (ML / research / eng)

Lead every bullet; never repeat a verb back-to-back; never "Responsible for" / "Helped with."

- **Build/ship:** Built, Engineered, Developed, Implemented, Deployed, Productionized, Shipped, Containerized, Automated, Scaled, Architected, Integrated, Migrated.
- **Optimize:** Optimized, Accelerated, Reduced, Cut, Improved, Tuned, Fine-tuned, Quantized, Distilled, Parallelized, Streamlined.
- **Model/experiment:** Trained, Modeled, Benchmarked, Evaluated, Validated, Calibrated, Engineered (features), Curated.
- **Research:** Researched, Investigated, Designed, Formulated, Devised, Discovered, Proved, Published, Co-authored, Presented, Analyzed.
- **Lead:** Led, Drove, Mentored, Spearheaded, Partnered, Coordinated.

Avoid: *worked on, helped, assisted, participated, was involved in, used.*

---

## 5. ML-specific content

### Skills section
Group, don't dump. ATS weighs keyword frequency + section placement; **spell out abbreviations next to the acronym** the first time ("Amazon Web Services (AWS)").
- **Languages:** Python, SQL, C++, Scala, R
- **ML/DL:** PyTorch, TensorFlow, JAX, scikit-learn, Hugging Face Transformers, XGBoost
- **MLOps/Infra:** Docker, Kubernetes, MLflow, Kubeflow, Airflow, SageMaker, Ray, Spark
- **Serving/opt:** Triton, ONNX, TensorRT, TorchServe, vLLM
- **Data:** Spark, Kafka, Snowflake, dbt, Postgres
- **Cloud:** AWS, GCP, Azure

Frequent miss: a resume with only "analysis / pandas / Jupyter" parses as **Data Scientist**, not **MLE**. For MLE roles, the words *MLOps, model serving, latency optimization, distributed training, Kubernetes* must appear.

### Show end-to-end ownership
Reward the full lifecycle: data → features → training → eval → **deployment → monitoring**. Stopping at "trained a model in a notebook" reads academic. Mention production, monitoring, retraining, drift where true.

### Research vs applied
- **Applied/prod:** lead with business/product metrics, deployment, scale, A/B lift.
- **Research:** lead with novelty vs SOTA, benchmarks, venues, *your* contribution; quantify ("+3.1 BLEU over prior SOTA").

### Publications / Kaggle / open source
- **Publications:** dedicated section; venue + year (NeurIPS/ICML/ACL/CVPR signal strongly); **bold your name**; first-author/top-venue near the top for research roles.
- **Kaggle:** a line only if meaningful rank/medal ("Competitions Master, top 0.5%, 3 gold").
- **Open source:** quantify adoption — stars, downloads, "merged N PRs into PyTorch," maintainer status; link the repo.

---

## 6. Formatting rules
- **Length:** one page for students / new grads / <~8 yrs. MIT allows two pages "if substantial relevant info." Research candidates with long pub lists may run longer (CV).
- **Bullets fit ONE line.** MIT: 1–2 lines per bullet; strongest single-page tech resumes hit exactly one line — no wrap to a 2nd line with 2–3 dangling words (awkward whitespace). If a bullet wraps, tighten until it sits on one clean line **or** fills the second line substantially.
- **Reverse chronological** in every section.
- **No pronouns.** Phrases, not sentences.
- **Consistent tense:** past for past, present for current; consistent within a role.
- **Font:** clean serif/sans (Times, Calibri, Arial, Garamond), **10–12pt**. Don't shrink to cram.
- **Margins:** ≥ 0.5", ideally ~0.75" (MIT). Keep real white space.
- **ATS:** single column; **no tables/text-boxes/columns/images/graphics**; standard headings ("Experience," "Skills," "Education"); standard round bullets; **PDF** unless .docx requested; mirror the JD's exact must-have phrasing without stuffing.

---

## 7. Common ML-candidate mistakes
1. **No metrics** — duties instead of quantified outcomes (the #1 mistake).
2. **Algorithm soup** — listing models/techniques with no context or impact.
3. **Notebook-only signal** — no deployment/monitoring/scale; reads academic.
4. **Wrong keyword profile** — MLE roles with a pure Data-Scientist keyword set.
5. **Over-indexing on coursework/academic projects** once you have pro experience.
6. **Endpoint metrics without baseline** — "achieved 93% accuracy" alone says nothing.
7. **Bullets that wrap to a third of a line** — awkward whitespace; tighten to one line.
8. **Pronouns, weak verbs, inconsistent tense.**
9. **Buzzword inflation** ("AI guru," "synergy") + unverifiable claims.
10. **Two+ pages as a new grad / non-ATS formatting.**

---

## 8. Section ordering
1. **Name + contact** (email, phone, LinkedIn, GitHub, Scholar/portfolio). No photo/address.
2. **Education** — degree, school, grad date, GPA (if strong), coursework only if new grad. Students keep high; experienced move below Experience.
3. **Skills** (grouped, keyword-rich) — many tech resumes place high so ATS + recruiter see the stack fast.
4. **Experience** (reverse chron, XYZ bullets) — the core; most-relevant roles get most bullets.
5. **Projects** — for new grads / to show depth jobs don't; treat as mini-experiences w/ metrics + links.
6. **Publications** — dedicated for research (can move above Experience for research roles).
7. **Open source / Kaggle / Awards** — as relevant.

Order by *relevance to this role* — strongest evidence highest (Harvard).

---

## 9. Tailoring: research vs production
| | **Research Scientist / PhD-track** | **ML Engineer / Applied / Production** |
|---|---|---|
| Top section | Publications, then Experience | Skills + Experience |
| Lead metric | Novelty vs SOTA, benchmarks, venues, citations | Latency, throughput, $ saved, A/B lift, scale, uptime |
| Emphasize | Problem formulation, experiments, papers, theory | Deployment, MLOps, reliability, end-to-end ownership |
| Keywords | Method/architecture names, venues, math/stats | PyTorch + Docker/K8s/MLflow/serving/distributed training |
| Length | CV can exceed one page; full pub list | One page (until senior); dense prod impact |
| Projects | Research projects, reproductions, ablations | Shipped systems, pipelines, infra |

Maintain one master resume; cut/reorder per posting — extract the JD's must-have skills, ensure those exact terms appear in Skills + Experience.

---

## Sources
- Laszlo Bock, *My Personal Formula for a Winning Resume* (LinkedIn) — https://www.linkedin.com/pulse/20140929001534-24454816-my-personal-formula-for-a-better-resume
- Google Careers — Laszlo Bock on fixing the biggest resume mistakes — https://careers.google.com/stories/laszlo-bock-head-of-people-operations-shares-how-to-fix-the-biggest-mistakes-on-your-resume/
- Inc. — "Google Recruiters Say Using the X-Y-Z Formula… Will Improve Your Odds" — https://www.inc.com/bill-murphy-jr/google-recruiters-say-these-5-resume-tips-including-x-y-z-formula-will-improve-your-odds-of-getting-hired-at-google.html
- Harvard FAS — Create a Strong Resume — https://careerservices.fas.harvard.edu/resources/create-a-strong-resume/
- Harvard FAS — 45 Rare Action Verbs for Your Resume — https://careerservices.fas.harvard.edu/blog/2025/08/14/45-rare-action-verbs-for-your-resume-with-examples/
- MIT CAPD — Career Toolkit: Crafting an Effective Resume — https://capd.mit.edu/resources/career-toolkit-crafting-an-effective-resume/
- MIT CAPD — Resume Action Verbs — https://capd.mit.edu/resources/resume-action-verbs/
- MIT CAPD — Resumes: Writing About Your Skills — https://capd.mit.edu/resources/resumes-writing-about-your-skills/
- Tech Interview Handbook — FAANG-Ready SWE Resumes — https://www.techinterviewhandbook.org/resume/
- Penn State Engineering — Action Verbs — https://career.engr.psu.edu/students/basics/action-verbs.aspx
- U-Michigan Engineering CRC — Action Verbs — https://career.engin.umich.edu/action-verbs-for-your-resume/
- Resume Worded — ML Resume Examples — https://resumeworded.com/machine-learning-resume-examples
- Resume Worded — Research Action Verbs — https://resumeworded.com/research-resume-action-verbs
- IGotAnOffer — ML Engineer Resume Examples — https://igotanoffer.com/en/advice/machine-learning-engineer-resume-examples
- Exponent — ML Engineer Resume Guide — https://www.tryexponent.com/blog/machine-learning-engineer-resume
- Exponent — Data Science Resume Guide — https://www.tryexponent.com/blog/data-science-resume
- BeamJobs — ML Resume Examples — https://www.beamjobs.com/resumes/machine-learning-resume-examples
- ResumeAdapter — ML Engineer Resume Keywords 2026 — https://www.resumeadapter.com/blog/machine-learning-engineer-resume-keywords
- Resumly — Highlighting ML Performance Metrics in Bullets — https://www.resumly.ai/blog/how-to-highlight-machine-learning-model-performance-metrics-in-resume-bullets
- Interview Kickstart — Top 10 ML Resume Mistakes — https://interviewkickstart.com/blogs/articles/machine-learning-resume-mistakes
- Enhancv — STAR Method on Your Resume — https://enhancv.com/blog/star-resume-template/
- Wonsulting — The XYZ Formula — https://www.wonsulting.com/job-search-hub/the-power-of-quantifiable-results-how-to-use-the-xyz-formula-to-supercharge-your-resume
- Jobscan — Data Science Resume Examples — https://www.jobscan.co/resume-examples/data-analysis/data-science

*Sourcing note:* XYZ wording + portfolio example quoted from Bock's LinkedIn essay (primary). No-pronoun / reverse-chron / action-verb / quantification rules corroborated by Harvard + MIT. Formatting specifics (1–2 line bullets, 0.5–0.75" margins, no tables/columns/graphics, tense) from MIT CAPD. ML metric/MLOps examples synthesized from the ML resources above.
