import requests
import re
from bs4 import BeautifulSoup
import json
import os
from collections import defaultdict


def load_crawled_urls(filename="data/amherst_webpages.txt"):
    urls = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    return urls


def find_links_on_page(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a')
            
            found_links = []
            for link in links:
                href = link.get('href')
                if href:
                    if href.startswith("/"):
                        href = "https://www.amherst.edu" + href
                    if href.startswith("https://www.amherst.edu/"):
                        found_links.append(href)
            
            return found_links
    except Exception as e:
        print(f"Error analyzing {url}: {e}")
    
    return []


def analyze_link_relationships(urls, max_pages=10):
    print(f"Analyzing link relationships for {len(urls)} URLs...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # Create a mapping from URL to index
    url_to_index = {url: i for i, url in enumerate(urls)}
    index_to_url = {i: url for i, url in enumerate(urls)}
    
    # Initialize adjacency matrix
    adjacency_matrix = [[0] * len(urls) for _ in range(len(urls))]
    
    # Analyze each page
    for i, url in enumerate(urls[:max_pages]):
        print(f"Analyzing page {i+1}/{min(len(urls), max_pages)}: {url}")
        
        links_on_page = find_links_on_page(url, headers)
        
        # Find which of our crawled URLs are linked from this page
        for link in links_on_page:
            if link in url_to_index:
                target_index = url_to_index[link]
                adjacency_matrix[i][target_index] = 1
                print(f"  -> Links to: {link}")
    
    return adjacency_matrix, url_to_index, index_to_url


def save_adjacency_matrix(matrix, url_to_index, index_to_url, filename="data/adjacency_matrix.json"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    data = {
        "adjacency_matrix": matrix,
        "url_to_index": url_to_index,
        "index_to_url": index_to_url
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Saved adjacency matrix to {filename}")


def print_matrix_summary(matrix, index_to_url):
    print("\nAdjacency Matrix Summary")
    print(f"Matrix size: {len(matrix)}x{len(matrix[0])}")
    
    total_links = sum(sum(row) for row in matrix)
    print(f"Total links: {total_links}")
    
    print("\nOutgoing links per page:")
    for i, row in enumerate(matrix):
        outgoing_links = sum(row)
        url = index_to_url.get(i, f"Page {i}")
        print(f"  {url}: {outgoing_links} outgoing links")
    
    print("\nIncoming links per page:")
    incoming_counts = [0] * len(matrix)
    for row in matrix:
        for j, val in enumerate(row):
            if val == 1:
                incoming_counts[j] += 1
    
    for i, count in enumerate(incoming_counts):
        url = index_to_url.get(i, f"Page {i}")
        print(f"  {url}: {count} incoming links")


def main():
    urls = load_crawled_urls()
    
    if not urls:
        print("No crawled URLs found. Run the crawler first:")
        print("make crawl")
        return
    
    print(f"Loaded {len(urls)} URLs from crawled data")
    
    # Analyze link relationships
    matrix, url_to_index, index_to_url = analyze_link_relationships(urls, max_pages=min(10, len(urls)))
    
    # Save results
    save_adjacency_matrix(matrix, url_to_index, index_to_url)
    
    # Print summary
    print_matrix_summary(matrix, index_to_url)


if __name__ == "__main__":
    main() 