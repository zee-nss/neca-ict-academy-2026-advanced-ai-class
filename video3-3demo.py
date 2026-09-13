import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# --------------------------------------------------------
# BASIC SCRAPING - Single Page
# --------------------------------------------------------

def scrape_quotes():
    """
    Scrape quotes from quotes.toscrape.com
    This is a practice site designed for learning.
    """
    url = "http://quotes.toscrape.com/"
    
    # Step 1: Fetch the page
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Failed to fetch page. Status code:", response.status_code)
        return []
    
    # Step 2: Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Step 3: Find the elements you want
    quotes = soup.find_all('div', class_='quote')
    
    # Step 4: Extract data from each element
    data = []
    for quote in quotes:
        text = quote.find('span', class_='text').text
        author = quote.find('small', class_='author').text
        tags = [tag.text for tag in quote.find_all('a', class_='tag')]
        
        data.append({
            'quote': text,
            'author': author,
            'tags': ', '.join(tags)
        })
    
    print("Scraped", len(data), "quotes")
    return data

print("TESTING BASIC SCRAPING")
print("=" * 50)

quotes = scrape_quotes()
df_quotes = pd.DataFrame(quotes)

print()
print("Sample of scraped data:")
print(df_quotes.head())


# --------------------------------------------------------
# PAGINATION - Scraping Multiple Pages
# --------------------------------------------------------

def scrape_all_quotes(max_pages=10):
    """
    Scrape quotes across multiple pages.
    Stops when there are no more pages.
    """
    
    all_quotes = []
    
    for page in range(1, max_pages + 1):
        url = "http://quotes.toscrape.com/page/" + str(page) + "/"
        print("Scraping page", page, "...")
        
        response = requests.get(url)
        
        # Stop if page doesn't exist
        if response.status_code != 200:
            print("  No more pages. Stopping.")
            break
        
        soup = BeautifulSoup(response.text, 'html.parser')
        quotes = soup.find_all('div', class_='quote')
        
        # Stop if no quotes found
        if not quotes:
            print("  No quotes found on this page. Stopping.")
            break
        
        for quote in quotes:
            text = quote.find('span', class_='text').text
            author = quote.find('small', class_='author').text
            tags = [tag.text for tag in quote.find_all('a', class_='tag')]
            
            all_quotes.append({
                'quote': text,
                'author': author,
                'tags': ', '.join(tags),
                'page': page
            })
        
        # BE POLITE - delay between pages
        time.sleep(1.5)
    
    print()
    print("Scraped", len(all_quotes), "quotes from", page, "pages")
    return all_quotes


print()
print("TESTING PAGINATION")
print("=" * 50)

all_quotes = scrape_all_quotes()
df_all = pd.DataFrame(all_quotes)

print()
print("Total quotes collected:", len(df_all))
print("Unique authors:", df_all['author'].nunique())

# --------------------------------------------------------
# REAL-WORLD EXAMPLE - E-Commerce Prices
# --------------------------------------------------------

def scrape_product_prices(num_pages=3):
    """
    Scrape book prices from a practice e-commerce site.
    This is the same pattern you'd use for real e-commerce sites.
    """
    
    all_products = []
    base_url = "http://books.toscrape.com/catalogue/"
    
    for page in range(1, num_pages + 1):
        url = base_url + "page-" + str(page) + ".html"
        print("Scraping page", page, "...")
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print("  Error on page", page, ":", e)
            continue
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all product containers
        products = soup.find_all('article', class_='product_pod')
        
        for product in products:
            try:
                # Extract title
                title_elem = product.find('h3').find('a')
                title = title_elem.get('title', 'Unknown')
                
                # Extract price
                price_elem = product.find('p', class_='price_color')
                price = price_elem.text if price_elem else 'N/A'
                
                # Extract availability
                avail_elem = product.find('p', class_='instock availability')
                availability = avail_elem.text.strip() if avail_elem else 'Unknown'
                
                # Extract rating
                rating_elem = product.find('p', class_='star-rating')
                rating = rating_elem.get('class', [''])[1] if rating_elem else 'No rating'
                
                all_products.append({
                    'title': title,
                    'price': price,
                    'availability': availability,
                    'rating': rating,
                    'page_found': page
                })
                
            except Exception as e:
                print("  Error parsing product:", e)
                continue
        
        time.sleep(1)
    
    df = pd.DataFrame(all_products)
    print()
    print("Scraped", len(df), "products")
    print("Price range:", df['price'].min(), "to", df['price'].max())
    
    return df

print()
print("TESTING E-COMMERCE SCRAPING")
print("=" * 50)

books = scrape_product_prices(num_pages=3)

print()
print("Sample products:")
print(books[['title', 'price', 'rating']].head(10))

# Save to CSV
books.to_csv('scraped_books.csv', index=False)
print()
print("Data saved to scraped_books.csv")


# --------------------------------------------------------
# THE COMPLETE AUTOMATION ARCHITECTURE
# --------------------------------------------------------

print()
print("=" * 50)
print("AUTOMATION ARCHITECTURE SUMMARY")
print("=" * 50)
print()
print("Data Sources:")
print("  1. CSV files on your computer")
print("  2. Google Sheets (team collaboration)")
print("  3. APIs (external services)")
print("  4. Web scraping (websites without APIs)")
print()
print("Processing:")
print("  Clean, merge, analyze, chart, report")
print()
print("Delivery:")
print("  Email, Google Sheets, scheduled execution")
print()
print("All running automatically while you sleep.")
