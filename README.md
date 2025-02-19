# 🛠️ interview_qa_extractor

## 📌 Project Overview

This repository contains code that **automatically extracts structured Q&A pairs** from technical content. The extracted data is used to build **a high-quality interview question dataset**.

This is a **perfect use case for LLMs** since they excel at **understanding, summarizing, and reformatting text** into structured formats like Q&A. We leverage **locally deployed LLMs (LLaMA 3.2:3b)** to **transform raw content into well-structured interview-style questions and answers.**

---

## 🚀 How It Works

The pipeline consists of the following steps:

1. **Load Content**:  
   - Technical content is loaded and processed for knowledge extraction.

2. **Preprocessing & Text Chunking**:  
   - The text is extracted, cleaned, and chunked into **meaningful sections** using `RecursiveCharacterTextSplitter`.  
   - **Surrogate character issues are sanitized** to ensure clean text processing.  

3. **Retrieving Contextual Knowledge**:  
   - A **vector database (ChromaDB)** stores previous chunks to provide additional **context retrieval** for better question generation.  
   - This allows the LLM to generate **coherent and structured** Q&A based on the content.

4. **LLM-Powered Q&A Generation**:  
   - A **custom LLM prompt** instructs the model to extract **specific, well-formed** questions and answers.  
   - The **generated questions avoid generic phrasing** like _"What does this section discuss?"_, instead focusing on **insightful, detailed questions**.

5. **Saving the Extracted Data**:  
   - The extracted Q&A pairs are saved in **JSON format**.
   - The dataset is continuously refined and expanded.  

---

## 🤝 Collaboration & Contributions  

🔹 **Want to improve the project?**  
I'd love to collaborate! If you want to extend this to **other technical domains**, feel free to contribute.

🔹 **How to Contribute?**  
- You can **suggest new content sources** to be processed.  
- If you want to **extend the script to other domains**, I'd be happy to review PRs and collaborate.  
- If you find **errors or inconsistencies**, feel free to submit improvements.  

---

## ⚡ Why This Project Matters  

This project demonstrates how **LLMs can automate knowledge extraction**. Instead of manually crafting interview questions, we:  

✅ **Use LLMs to extract meaningful insights** from technical content.  
✅ **Ensure high-quality, structured Q&A pairs** for study and AI-powered interview assistants.  
✅ **Create a scalable and adaptable pipeline** that can be expanded to more fields.  

---

## 🔧 How to Set Up the Project  

### 📥 Installation  

1. **Install `uv`** (for dependency management):  
   [uv Installation Guide](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)  

2. **Sync dependencies:**  
   ```shell
   uv sync --all-extras --dev
   ```

3. **Install and Configure Ollama:**
   ```shell
   # Install Ollama
   curl -fsSL https://ollama.com/install.sh | sh
   
   # Pull the LLaMA 3.2:3b model
   ollama pull llama3.2:3b
   
   # Apply custom Modelfile to increase context size
   ollama create custom-llama -f Modelfile
   ```

   The `Modelfile` configures LLaMA 3.2:3b with an increased context size of 5000 tokens:
   ```
   FROM llama3.2:3b
   PARAMETER num_ctx 5000
   ```

4. **Set up Dagster:**
   - The project uses Dagster for orchestration and monitoring of the extraction pipeline
   - The Dagster UI provides visibility into job runs, asset materializations, and pipeline status
   - Access the Dagster UI locally at `http://localhost:3000` after starting the server:
     ```shell
     dagster dev
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

If you have **any suggestions, feature requests, or would like to collaborate**, feel free to reach out! Let's enhance this **LLM-powered interview question generator** together. 🚀
