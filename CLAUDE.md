# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## About

This project is a collection of Jupyter Notebooks for Thai News NLP, as part of a class assignment.

This project uses [uv](https://docs.astral.sh/uv/) as a dependency manager.

```sh
uv sync
uv add [package-name]
uv remove [package-name]
```

## Assignment instructions

There are 4 tasks that should be submitted:

1. **Phase 1: Data Engineering**
    - Select a baseline dataset, and collect new data using web scraping to augment the dataset.
    - Create a pipeline for data cleaning.
    - Compare tokenization results.

2. **Phase 2: Unsupervised Discovery**
    - Use topic modeling to discover topics in the newly scraped data.
    - Perform NER to extract entities in the newly scraped data.

3. **Phase 3: Text Classification - Comparision**
    Train a model using two different approaches for comparison:
    - **Classical Model**
        * **Feature:** Use Bag-of-Words or TF-IDF.
        * **Model:** Use standard Machine Learning models.
    - **Neutral Model**
        * **Feature:** Use Word2Vec, Doc2Vec, or FastText.
        * **Model:** Build a Deep Learning model using RNN, LSTM, or GRU.

4. **Phase 4: Evaluation & Application**
    - Report results from Phase 3 using Accuracy, Precision, Recall, and F1-Score.
    - (Optional) Use vector embeddings from Phase 3 to a create simple document retrieval system using Cosine Similarity.

The full instruction of this assignment can be found at `NLP_ASSIGNMENT.md`

## Dataset information

All dataset are loaded from Hugging Face using the `datasets` library.

### **Baseline dataset:** `szzs1693/prachathai-67k`

`prachathai-67` is news article corpus and multi-label text classification from Prachathai.com. It has the total of 67,889 articles, ranging from 2004-2018.

#### Data Processing Notes

- Based on evidence, we have strictly filtered articles for single-label classification in 3 categories, social, economics, and politics. We then downsampled to 1,801 articles per category. The process for normalizing this dataset can be seen in the notebook `01-data-engineer/merge-normalize-dataset.ipynb`.

### **Scraped dataset:** `szzs1693/nlp-thaipbs-news`

`nlp-thaipbs-news` is dataset of news article scraped from Thai PBS, covering three topic categories: politics, economy, and social. It has the total of 1,200 articles, 400 articles per each, ranging from Aug 2025 - Mar 2026.

#### Data Processing Notes

- **See-also section stripped:** Articles often ended with an "อ่านข่าว" (read more) section containing links to related articles. This section was removed from ~87 % of articles (1,049/1,200); the remaining ~13% either had no detectable header pattern or used edge-case formatting (e.g. `<strong>`-wrapped headers, inline typos).
- **Stratified sampling for politics:** The 400 politics articles are drawn from three sub-groups — 40% (160) from the 2569 general-election cycle, 10% (40) from Cambodia border-conflict coverage, and 50% (200) general politics — to prevent two dominant news cycles from skewing the category distribution.

### **Final dataset:** `szzs1693/intro-nlp-thai-news`

**Schema:**

```json
{
  "url": "large_string",
  "date": "timestamp[us]",
  "title": "large_string",
  "body_text": "large_string",
  "category": "large_string", // politics | economics | social
  "source": "large_string" // prachathai | thaipbs
}
```

## Writing guidelines

- If you are writing a new notebook, write in English. If you are editing an existing notebook, refers to the written language in that notebook.
- Use `pandas` for data exploration and processing.