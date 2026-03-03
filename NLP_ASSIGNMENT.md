# 📘 Term Project Guidelines

**Course:** Introduction to Natural Language Processing  
**Weight:** 15% of the total grade  
**Topic:** End-to-End NLP Insight & Classification System

## 🎯 Objectives
To allow students to apply the knowledge gained from Weeks 1 to 14 in building a complete language processing pipeline. Students must demonstrate the ability to handle raw text, discover hidden structures (Unsupervised Learning), and compare the performance between traditional statistical models and modern Deep Learning models.

## 📋 Requirements
Students must choose a **Data Domain** of interest (e.g., political news, e-commerce product reviews, medical abstracts, or webboard threads) and proceed through the following 4 phases:

### 📌 Phase 1: Data Engineering (Covers Weeks 2-4)
*   **1.1 Data Collection:**
    *   **Standard Dataset:** Select one standard dataset to serve as a baseline.
    *   **Web Scraping (Mandatory):** Write a program (using `requests` and `BeautifulSoup` as learned in Week 3) to collect new data from the internet (years 2025-2026) with at least 500–1,000 entries to augment the dataset.
*   **1.2 Preprocessing Pipeline:**
    *   Create a pipeline for data cleaning: handle HTML tags, URLs, and emojis.
    *   **Tokenization Comparison:** Compare tokenization results between two different tools (e.g., NLTK vs. spaCy or Word-level vs. Subword-level).

### 📌 Phase 2: Unsupervised Discovery (Covers Weeks 9-11)
*   **2.1 Topic Modeling:**
    *   Use LDA (Latent Dirichlet Allocation) or NMF techniques to discover "Themes" or hidden topics within the newly scraped data (set $k=5$ to 10 topics). Discuss whether the resulting topics are meaningful (Interpretability).
*   **2.2 Named Entity Recognition (NER):**
    *   Use a pre-trained model (e.g., spaCy) to extract entities (e.g., Person, Organization, Location) and provide basic statistical summaries (e.g., which organization is mentioned most frequently in this dataset).

### 📌 Phase 3: The "Classic vs. Neural" Showdown (Covers Weeks 6-8, 12-14)
Students must choose a **Text Classification** task (e.g., Sentiment Analysis or News Categorization) and solve it using two different approaches for comparison:
*   **Method A: The Classical Approach**
    *   **Feature:** Use Bag-of-Words or TF-IDF.
    *   **Model:** Use standard Machine Learning models such as Naive Bayes, Logistic Regression, or Random Forest.
*   **Method B: The Neural Approach**
    *   **Feature:** Use Word Embeddings (Word2Vec or GloVe) as input, or use Doc2Vec.
    *   **Model:** Build a Deep Learning model using RNN, LSTM, or GRU architectures (PyTorch/TensorFlow/Keras are permitted).

### 📌 Phase 4: Evaluation & Application (Covers Weeks 7, 13)
*   **4.1 Evaluation:** Report results using Precision, Recall, and F1-Score (Do not use Accuracy alone).
*   **4.2 Document Search (Bonus/Optional):** Try using the vectors from Method B (Embeddings) to create a simple document retrieval system using Cosine Similarity to see if the system returns relevant documents correctly when given a query.

### 📌 Phase 5: AI Audit Log (Very Important ❗)
Since the use of AI (e.g., ChatGPT/Gemini) is permitted to assist with coding, students must maintain a log to prove that **"You are the one auditing the AI, not letting the AI do all the work for you."**

#### 📝 AI Audit Log Format (Example)
Students must submit a log table at the end of the report with the following details:

| Task | Prompt Used | AI Output (Summary) | Human Verification & Edits |
| :--- | :--- | :--- | :--- |
| **Regex Cleaning** | "Write regex to remove email from text" | `r'[a-zA-Z0-9]+@[a-zA-Z]+'` | **Fail:** The AI code did not cover emails with dots (.).<br>**Fix:** Manually updated pattern to `r'[\w\.-]+@[\w\.-]+'` |
| **Model Training** | "Build LSTM model with PyTorch" | (Code Snippet...) | **Pass w/ Edit:** Code ran but did not support GPU.<br>**Fix:** Added `.to(device)` lines for speed. |
| **Scraping** | "Scrape news titles from XYZ.com" | `soup.find('div', class_='title')` | **Fail:** The website's class name had changed.<br>**Fix:** Inspected the actual site and changed to `class_='news-header-v2'` |

## 📊 Rubric (15%)

| Component | Criteria | Score (15) |
| :--- | :--- | :---: |
| **1. Data & Pipeline** | Evidence of actual Web Scraping, high data quality, and correct application of Preprocessing (Cleaning/Tokenization) principles. | 3 |
| **2. Discovery (Topic/NER)** | Ability to use LDA/NMF to find topics and extract Entities (NER) for interesting data analysis. | 3 |
| **3. Model Implementation** | Correct implementation of both models:<br>1. Classic (TF-IDF + ML)<br>2. Neural (Embeddings + RNN/LSTM) | 3 |
| **4. AI Audit, Evaluation & Analysis** | Presence of an AI Audit Log showing actual debugging/edits, correct evaluation (F1, Precision, Recall), thorough Error Analysis (why one model outperformed the other), and comparison of Embeddings vs. Bag-of-Words. | 4 |
| **5. Presentation** | Clear and easy-to-understand slides; Jupyter Notebook code is executable and well-documented with comments. | 2 |

## 💡 Tips for Students
*   **Connectivity:** This project is designed to help you visualize "why" we move from TF-IDF to Word Embeddings and Deep Learning. Focus your discussion on this comparison.
*   **Tools:** You may use any libraries covered in class (NLTK, spaCy, scikit-learn, Gensim, PyTorch/TensorFlow).
*   **Submission:** Submit as a Jupyter Notebook (.ipynb) with saved outputs, the dataset used, and the presentation file.