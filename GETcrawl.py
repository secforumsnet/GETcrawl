import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
from colorama import init, Fore

# Initialize colorama for colored text
init(autoreset=True)

# Function to extract base domain from a URL
def get_base_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

# Function to crawl a URL and identify links with GET parameters
def crawl_url(url, visited_urls, target_extensions, max_depth, get_params_file):
    try:
        print(f"Crawling URL: {url}")  # Print the current URL being crawled

        # Send an HTTP GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content with BeautifulSoup to find links
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)

            # Add the URL to the set of visited URLs to avoid revisiting
            visited_urls.add(url)

            # Parse the URL to check for target file extensions and GET parameters
            parsed_url = urlparse(url)
            file_extension = parsed_url.path.split('.')[-1]
            query_params = parsed_url.query

            # Check if the URL matches the criteria
            if file_extension in target_extensions and query_params:
                print(Fore.GREEN + f"URL with GET parameters found: {url}" + Fore.RESET)
                with open(get_params_file, 'a') as file:
                    file.write(f"{url}\n")

            # Follow links to other pages and domains
            for link in links:
                href = link['href']

                # Ensure the link is not already visited
                absolute_url = urljoin(url, href)
                if absolute_url not in visited_urls and max_depth > 0:
                    crawl_url(absolute_url, visited_urls, target_extensions, max_depth - 1, get_params_file)

        else:
            print(f"Failed to retrieve {url}. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the page: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Input the filename containing starting URLs
file_name = input("Enter the filename containing starting URLs: ")

# Create a set to store visited URLs
visited_urls = set()

# Set the maximum depth for crawling (unlimited in this case)
max_depth = float("inf")

# Define the target file extensions to look for
target_extensions = {"php", "asp", "aspx"}

# Create a file to store URLs with GET parameters
get_params_file = "urls_with_get_params.txt"
open(get_params_file, 'w').close()  # Clear the file if it exists

# Read starting URLs from the input file
try:
    with open(file_name, 'r') as file:
        starting_urls = [line.strip() for line in file]

    # Start the crawl from the provided starting URLs
    for starting_url in starting_urls:
        crawl_url(starting_url, visited_urls, target_extensions, max_depth, get_params_file)

except FileNotFoundError:
    print(f"File '{file_name}' not found.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

print("Crawling complete. URLs with GET parameters are saved in 'urls_with_get_params.txt'.")
