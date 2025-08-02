#include <iostream>
#include <list>
#include <map>
#include <vector>
#include <fstream>
#include <string>
#include <sstream>
#include <algorithm>
using namespace std;

const int MAX_PAGES = 100;
const int iterations = 100;
const float damping_factor = 0.85;

map<int, std::vector<int>> linkMatrixToAdjacencyMap(int matrix[][MAX_PAGES], int rows, int cols) {
    // Page -> {kidPage, kidPage}
    std::map<int, std::vector<int>> adjacencyMap;

    // Select a page
    for (int i = 0; i < rows; i++) {
        std::vector<int> linksFrom;
        // Check what other pages it leads to (i.e. matrix[i][j] == 1) and add them to its linksFrom
        for (int j = 0; j < cols; j++) {
            if (matrix[i][j] == 1) {
                linksFrom.push_back(j);
            }
        }
        // set that page to point at the linksFrom list in our adjacency map
        adjacencyMap[i] = linksFrom;
    }
    return adjacencyMap;
}

std::map<int, float> runPageRank(int linkMatrix[][MAX_PAGES], int rows, int cols) {
    // Convert matrix to adjacency map.
    // That is if [a][b] = 1 and [a][c] = 1 in the matrix, a -> {b, c} in the adjacency map
    // where a, b, and c are link Ids, indices of the matrix
    std::map<int, std::vector<int>> adjacencyMap = linkMatrixToAdjacencyMap(linkMatrix, rows, cols);

    std::map<int, float> pageRanks;
    float initialPageRank = 1.0/rows;
    for (int i = 0; i < rows; i++){
        pageRanks.insert({i, initialPageRank});
    }

    for (int i = 0; i < iterations; i++) {
        std::map<int, float> newPageRanks;
        
        // Initialize new page ranks with damping factor
        for (int j = 0; j < rows; j++) {
            newPageRanks[j] = (1.0 - damping_factor) / rows;
        }

        // Pick a page
        for (int j = 0; j < rows; j++){
            // Collect the pages it leads to (kids),
            // and calculate the rank value to be added to the children pages' present rank
            std::vector<int> linksFrom = adjacencyMap[j];
            
            if (linksFrom.size() > 0) {
                float rankToAddForKids = (damping_factor * pageRanks[j]) / (float) linksFrom.size();

                // Iterate through the kids of this page
                for (int childLink : linksFrom) {
                    newPageRanks[childLink] += rankToAddForKids;
                }
            } else {
                // If page has no outgoing links, distribute its rank to all pages
                float rankToDistribute = (damping_factor * pageRanks[j]) / rows;
                for (int k = 0; k < rows; k++) {
                    newPageRanks[k] += rankToDistribute;
                }
            }
        }
        
        pageRanks = newPageRanks;
    }
    return pageRanks;
}

void printPageRanks(const std::map<int, float>& pageRanks, const std::vector<string>& pageNames) {
    cout << "\n=== PageRank Results ===" << endl;
    cout << "Page\t\tRank" << endl;
    cout << "----\t\t----" << endl;
    
    // Create a vector of pairs to sort by rank
    std::vector<std::pair<int, float>> sortedRanks;
    for (const auto& pair : pageRanks) {
        sortedRanks.push_back(pair);
    }
    
    // Sort by rank (descending)
    std::sort(sortedRanks.begin(), sortedRanks.end(), 
              [](const std::pair<int, float>& a, const std::pair<int, float>& b) { return a.second > b.second; });
    
    for (const auto& pair : sortedRanks) {
        int pageId = pair.first;
        float rank = pair.second;
        string pageName = (pageId < pageNames.size()) ? pageNames[pageId] : "Page " + to_string(pageId);
        cout << pageName << "\t\t" << rank << endl;
    }
}

int main() {
    // Test with a simple 4x4 matrix
    int testLinkStructure[MAX_PAGES][MAX_PAGES] = {
        {0, 1, 1, 0},
        {1, 0, 0, 1},
        {0, 1, 0, 1},
        {1, 0, 1, 0}
    };
    
    std::vector<string> testPageNames = {"Home", "About", "Services", "Contact"};
    
    cout << "Testing PageRank with 4x4 matrix..." << endl;
    std::map<int, float> results = runPageRank(testLinkStructure, 4, 4);
    printPageRanks(results, testPageNames);
    
    // Try to read crawled data if available
    ifstream dataFile("data/amherst_webpages.txt");
    if (dataFile.is_open()) {
        cout << "\n=== Processing Crawled Data ===" << endl;
        
        std::vector<string> urls;
        string line;
        while (getline(dataFile, line)) {
            if (!line.empty()) {
                urls.push_back(line);
            }
        }
        dataFile.close();
        
        if (urls.size() > 0) {
            cout << "Found " << urls.size() << " crawled URLs" << endl;
            cout << "Note: To process the crawled data, you would need to:" << endl;
            cout << "1. Create a link matrix from the crawled URLs" << endl;
            cout << "2. Analyze which pages link to which other pages" << endl;
            cout << "3. Build the adjacency matrix" << endl;
            cout << "4. Run PageRank on the real data" << endl;
        }
    } else {
        cout << "\nNo crawled data found. Run the Python crawler first:" << endl;
        cout << "python3 crawler.py" << endl;
    }
    
    return 0;
}