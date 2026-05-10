# Hi, I'm Ishan

Building production LLM systems with retrieval, agentic flows, and multi-stage guardrails. MS Applied AI at Northeastern. Four years at TCS shipping LLM features for enterprise clients in Life Sciences and BFSI.

Open to **Fall 2026 AI/ML co-op** in the US (Boston preferred, remote OK).

---

## Now

- Shipping public mirrors for OmegaTK, Findmejob, and UpMyRank
- Phase 3 LangGraph track (Krish Naik): multi-agent content automation,
- Writing on Medium about RAG eval, prompt caching, and the gap between architecture docs and what actually breaks in production

---

## Projects

### OmegaTK Code Assistant
Production RAG chatbot for the OpenEye Omega Toolkit (a Cadence Molecular Sciences company, Boston).

- Three-layer pipeline: GPT-4o-mini intent classifier (4 routes) → FAISS retrieval over 574 doc chunks → AST + API allowlist validation with up to 5 corrective retries
- 70-pair gold-standard eval set. RAGAS 0.85 pipeline score, groundedness 1.00. Hard refusal on low-confidence retrievals.
- Cuts time-to-working-script from 20-40 minutes to under 30 seconds at ~$0.01 per query
- Stack: FastAPI, React, Supabase + pgvector, FAISS, OpenAI text-embedding-3-small, GPT-4o-mini, Vercel + Render

[Live demo](https://prod-omega-tk-chatbot-qnm4.vercel.app) · [Repo](https://github.com/Ishan2036924/omega-tk-chatbot)

### Findmejob (CareerForge)
AI career platform with cost-aware multi-model routing.

- Next.js (App Router) on Vercel Fluid Compute, Supabase Auth (Google OAuth + email) with RLS
- Cost-aware routing through Vercel AI Gateway: Sonnet 4.6 for moat tasks, GPT-4.1-mini for support. Per-user cost target ~$0.48/mo against ~$10 all-Sonnet baseline.
- Prompt caching architecture targets 70%+ cache hits, projected to drop effective Sonnet input cost from $3 to ~$1.10 per 1M tokens
- Edit-via-JSON resume engineering: LLM emits structured edit ops, deterministic transformer applies them to a stable LaTeX template (Tectonic compiled in Vercel Sandbox). Eliminates LaTeX-syntax-from-LLM bugs.

[Live](https://findmejob-nu.vercel.app) (repo private, available on request)

### UpMyRank
RAG and Socratic tutoring engine for K-12 NCERT subjects.

- Socratic tutoring engine using OpenAI native function calling to plan multi-turn pedagogy: classify learner intent, choose retrieval scope, pick next move, escalate model tier when needed
- Two-layer policy guardrails: regex solution-seeker detector blocks direct-answer requests, CONTEXT_LOCK prompt scaffold pins agent persona
- Routes between GPT-4o-mini, GPT-4.1-mini, GPT-4o by task complexity
- RAG layer on FastAPI + Render with pgvector retrieval over Hugging Face NCERT corpus, Docker, Redis caching, GitHub Actions CI/CD. Three subject domains in production.

[Live](https://upmyrank-poc.vercel.app) (repo private, available on request)

---

## Stack

**LLM and System Design:** RAG pipelines (chunking, retrieval, reranking), agentic flows with function calling, multi-agent orchestration, multi-stage guardrails, prompt caching, cost-aware model routing, token and context-window management

**LLM Frameworks and Protocols:** OpenAI API, Claude API, LangChain, LangGraph, LangSmith, Vercel AI Gateway, Anthropic Model Context Protocol (MCP), Google A2A protocol

**Retrieval and Embeddings:** FAISS, pgvector, sentence-transformers, Hugging Face, OpenAI embeddings

**Evaluation and Reliability:** RAGAS, gold-standard dataset design, groundedness scoring, latency optimization, monitoring, hard-refusal guardrails

**Full-Stack Development:** FastAPI, Next.js (App Router), React, server-side rendering, server actions

**Cloud and Agent Hosting:** AWS SageMaker, Google ADK, Vercel (Fluid Compute, AI Gateway, Sandbox), Render, DigitalOcean, Supabase, Google Cloud Console

**Infra and DevOps:** Docker, GitHub Actions CI/CD, Redis, Postgres

**ML / DL:** PyTorch, scikit-learn, spaCy, NLTK, Pandas, NumPy

**Tools:** Python, Git, VS Code, Claude Code, conda

---

## Experience

**TCS** · Developer · Jul 2021 – Aug 2025 · Noida

LLM and NLP engineering for enterprise clients in Life Sciences and BFSI.

- Deployed LLM-powered chatbots across 3 enterprise clients using GPT-3.5/GPT-4 with intent classification, prompt engineering, and retrieval-grounded responses; achieved 60% query deflection and +9 point CSAT.
- Built end-to-end NLP pipelines for ticket classification, multi-turn FAQ handling with entity extraction, and document summarization. Processed 10K+ tickets/month, cutting resolution time 40% at 99.5% uptime.
- Led LLM orchestration workflows on internal tooling with conditional routing and automated decision points. Cut manual effort 55%, lifted SLA compliance from 88% to 96%.

---

## Writing

I write on Medium about RAG, agent eval, prompt caching, and what breaks in production.

[medium.com/@ishansri13](https://medium.com/@ishansri13)

---

## Reach me

- LinkedIn: [ishan-srivastava-7742b121a](https://www.linkedin.com/in/ishan-srivastava-7742b121a/)
- Email: srivastava.ish@northeastern.edu
- Medium: [@ishansri13](https://medium.com/@ishansri13)

---

<sub>Boston, MA · MS Applied AI @ Northeastern · Fall 2026 co-op available</sub>
