# 🛠️ interview_qa_extractor

## 📌 Project Overview

This repository contains the code that **automatically extracts structured Q&A pairs** from well-known books in **Generative AI, NLP, ML, Mathematics for ML, and ML System Design**. The extracted data is then used to build **a high-quality interview question dataset**.

This is a **perfect use case for LLMs** since they excel at **understanding, summarizing, and reformatting text** into structured formats like Q&A. Instead of manually curating interview questions, we leverage **locally deployed LLMs (DeepSeek-R1, LLaMA 3.2)** to **transform raw book content into well-structured interview-style questions and answers.**  

🔗 **The extracted dataset is available here:** [nlp-math-interview-qa](https://huggingface.co/datasets/Azzedde/nlp-math-interview-qa)

---

## 🚀 How It Works

The pipeline consists of the following steps:

1. **Load Books as PDFs**:  
   - Books in **Generative AI, NLP, ML, Math for ML, and System Design** are loaded as **PDFs**.  

2. **Preprocessing & Text Chunking**:  
   - The text is extracted, cleaned, and chunked into **meaningful sections** using `RecursiveCharacterTextSplitter`.  
   - **Surrogate character issues are sanitized** to ensure clean text processing.  

3. **Retrieving Contextual Knowledge**:  
   - A **vector database (ChromaDB)** stores previous chunks to provide additional **context retrieval** for better question generation.  
   - This allows the LLM to generate **coherent and structured** Q&A based on **actual book content**.

4. **LLM-Powered Q&A Generation**:  
   - A **custom LLM prompt** instructs the model to extract **specific, well-formed** questions and answers.  
   - The **generated questions avoid generic phrasing** like _"What does this section discuss?"_, instead focusing on **insightful, detailed questions**.

5. **Saving the Extracted Data**:  
   - The extracted Q&A pairs are saved in **JSON format**.
   - The dataset is continuously refined and expanded.  

---

## 🤝 Collaboration & Contributions  

🔹 **Want to improve the dataset?**  
I’d love to collaborate! If you have **books from other AI-related fields** or even want to generalize this to **other technical domains (e.g., Cybersecurity, Mathematics, Data Engineering, etc.)**, feel free to contribute.

🔹 **How to Contribute?**  
- You can **suggest new books** to be processed.  
- If you want to **extend the script to other domains**, I’d be happy to review PRs and collaborate.  
- If you find **errors or inconsistencies**, feel free to refine the dataset.  

---

## ⚡ Why This Project Matters  

This project demonstrates how **LLMs can automate knowledge extraction**. Instead of manually crafting interview questions from hundreds of pages, we:  

✅ **Use LLMs to extract meaningful insights** from authoritative sources.  
✅ **Ensure high-quality, structured Q&A pairs** for study, fine-tuning, and AI-powered interview assistants.  
✅ **Create a scalable and adaptable pipeline** that can be expanded to more fields.  

If you’re working in **AI, ML, NLP, or education**, this project showcases a real-world application of **LLMs beyond chatbots—using them for structured knowledge curation.**  

---

## 🔧 How to Set Up the Project  

### 📥 Installation  

1. **Install `uv`** (for dependency management):  
   [uv Installation Guide](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)  

2. **Sync dependencies:**  
   ```shell
   uv sync --all-extras --dev
   ```

3. **Install `ollama` (for local LLM execution):**  
   ```shell
   curl -fsSL https://ollama.com/install.sh | sh
   ```

---

## ✅ Development & Contribution Guidelines  

### 🔍 Code Formatting & Linting  

Before submitting a PR, ensure your code follows the required formatting and type-checking standards:  
```shell
uv run ruff check --fix
uv run ruff format
uv run mypy .
```

### 🧪 Running Tests  

Run unit tests before pushing changes:  
```shell
uv run pytest
```

### 📌 Git Workflow  

- Follow **Conventional Commits** ([Spec Here](https://www.conventionalcommits.org/en/v1.0.0/)) for commit messages.  
- All work **must be merged from feature branches** into `main` via **Pull Requests (PRs)**.  
- Once your code is ready for review, **assign me as a reviewer** to notify me.  

---

## 📬 Contact  

If you have **any suggestions, feature requests, or would like to collaborate**, feel free to reach out! Let’s enhance this **LLM-powered interview question generator** together. 🚀  

