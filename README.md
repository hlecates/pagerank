# PageRank

A complete implementation of Google's PageRank algorithm with a web crawler to collect real data from Amherst College's website.

## Overview

This project consists of two main components:

1. **Web Crawler** (`crawler.py`) - A Python script that crawls Amherst College's website to collect URLs and their linking relationships
2. **PageRank Algorithm** (`pagerank.cpp`) - A C++ implementation of the PageRank algorithm that ranks pages based on their importance

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment and install dependencies
make setup

# Or install dependencies globally
make install
```

### 2. Crawl the Website

```bash
# Crawl Amherst College website
make crawl
```

This will:
- Crawl up to 20 pages from Amherst College's website
- Filter and validate links
- Save results to `data/amherst_webpages.txt`

### 3. Analyze Link Relationships

```bash
# Analyze link relationships
make analyze
```

This will:
- Analyze which pages link to which other pages
- Generate an adjacency matrix
- Save results to `data/adjacency_matrix.json`

### 4. Run PageRank Algorithm

```bash
# Build and run the PageRank algorithm
make run
```

This will:
- Build the C++ program
- Run PageRank on a test matrix
- Display ranked results

### 5. Complete Pipeline

```bash
# Run the entire pipeline: crawl, analyze, then PageRank
make all
```

## Project Structure

```
pagerank/
├── crawler.py          # Web crawler implementation
├── pagerank.cpp        # PageRank algorithm implementation
├── analyzer.py         # Link relationship analyzer
├── requirements.txt    # Python dependencies
├── Makefile           # Build and run commands
├── README.md          # This file
└── data/              # Generated data directory
    ├── amherst_webpages.txt      # Crawled URLs
    └── adjacency_matrix.json     # Link relationship matrix
```
