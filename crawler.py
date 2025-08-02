import requests
import re
import threading
import os
from bs4 import BeautifulSoup


def is_valid_link(href, url, visitedLinks):
    isValid = False
    # Define the file extensions to ignore
    ignored_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.ics', '.pdf', '.mp4', '.mp3', '.docx', '.html']

    # Ensure the link is not null, does not lead to the same page it lives in.
    if href and href != url:
        # is an amherst.edu link
        if href.startswith("https://www.amherst.edu/"):
            # is not a duplicate page in php
            if not href.startswith("https://www.amherst.edu/index.php/"):
                # is not a shortcut, bookmark or a log in page
                if "/mm/" not in href and "/go/" not in href and "/node/" not in href and "#" not in href and "?" not in href and "-mm-" not in href and "/saml/" not in href and not re.match(r'^https://www.amherst.edu/\d', href):
                    # is a page and not a file
                    if not href.startswith("https://www.amherst.edu/system/files/") and not href.startswith("https://www.amherst.edu/securimage") and not href.startswith("https://www.amherst.edu/media/") and not any(href.endswith(ext) for ext in ignored_extensions):
                        # is not more than four pages deep
                        if href.count('/') <= 5:
                            # is not a user page (too plenty) 
                            if not href.startswith("https://www.amherst.edu/user"):
                                    # has not been visited
                                    if href not in visitedLinks:
                                        isValid = True
    return isValid


def find_links(url, toVisitLinks, visitedLinks, lock):
    print(f"Crawling: {url}")
    try:
        # Add headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all the links in the page
            links = soup.find_all('a')
            
            # Extract and print the href attribute of each link
            for link in links:
                href = link.get('href')

                if href and href.startswith("/"):
                    href = "https://www.amherst.edu" + href
                    isValidLink = is_valid_link(href, url, visitedLinks)
                else:
                    isValidLink = is_valid_link(href, url, visitedLinks)

                if isValidLink:
                    with lock:
                        if href not in toVisitLinks:
                            print(f"Found: {href}")
                        toVisitLinks.add(href)

        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"An error occurred: {e}")


def validateAndWriteLinks(links):
    print("Validating Collated Links")
    validatedLinks = set()
    
    # Create output directory if it doesn't exist
    output_dir = "data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_file = os.path.join(output_dir, "amherst_webpages.txt")
    
    # Add headers for validation requests too
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    for url in links:
        try:
            # Send a GET request to the URL
            response = requests.get(url, headers=headers, timeout=10)
            # If the request succeeds (status code 200)
            if response.status_code == 200:
                # add the link to our validated set
                validatedLinks.add(url)
                with open(output_file, 'a') as file:
                    # and write link into our output file
                    file.write(url + '\n')     
        except Exception as e: 
            print(f"An error occurred validating {url}: {e}")
    
    print(f"Validated {len(validatedLinks)} links out of {len(links)} total links")
    return validatedLinks

    
def collate_links():
    toVisitLinks = set()
    visitedLinks = set()
    lock = threading.Lock()
    
    # Start with the main page
    start_url = 'https://www.amherst.edu/'
    visitedLinks.add(start_url)
    find_links(start_url, toVisitLinks, visitedLinks, lock)

    count = 0
    max_pages = 20  # Limit to prevent infinite crawling
    
    print(f"Starting to crawl {len(toVisitLinks)} discovered links...")
    
    while toVisitLinks and count < max_pages:
        count += 1
        with lock:
            if not toVisitLinks:
                break
            presentLink = toVisitLinks.pop()
        
        visitedLinks.add(presentLink)
        find_links(presentLink, toVisitLinks, visitedLinks, lock)
        
        print(f"Progress: {count}/{max_pages} pages crawled, {len(toVisitLinks)} links in queue")

    print(f"Examining {len(visitedLinks)} Links")
    validatedLinks = validateAndWriteLinks(visitedLinks)
    print(f"Successfully validated {len(validatedLinks)} links")
    
    return validatedLinks

  
if __name__ == "__main__":
    collate_links()
