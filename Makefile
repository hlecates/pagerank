.PHONY: setup crawl build run clean test

# Setup virtual environment and install dependencies
setup:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

# Crawl the Amherst website
crawl:
	. venv/bin/activate && python3 crawler.py

# Analyze link relationships from crawled data
analyze:
	. venv/bin/activate && python3 analyzer.py

# Build the C++ PageRank program
build:
	g++ -std=c++11 -o pagerank pagerank.cpp

# Run the PageRank algorithm
run: build
	./pagerank

# Run the complete pipeline: crawl, analyze, then run PageRank
all: crawl analyze run

# Clean up generated files
clean:
	rm -f pagerank
	rm -rf data/
	rm -rf venv/

# Test the PageRank algorithm with sample data
test: build
	./pagerank

# Install dependencies (without virtual environment)
install:
	pip3 install -r requirements.txt 