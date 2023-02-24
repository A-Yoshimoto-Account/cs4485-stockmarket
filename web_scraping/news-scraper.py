import requests
from bs4 import BeautifulSoup

# Make a request to the webpage
url = 'https://finance.yahoo.com/news/stocks-moving-in-after-hours-nvidia-lucid-etsy-bumble-225038026.html'
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find the relevant section of the page containing the stock information
section = soup.find('section', {'class': 'canvas-body'})

# Extract the information for each stock
stocks = section.find_all('li')
for stock in stocks:
    name = stock.find('h3').text
    symbol = stock.find('span', {'class': 'Fw(600)'}).text
    change = stock.find('span', {'class': 'Fw(600) Mend(10px)'}).text
    percent_change = stock.find('span', {'class': 'Fw(600) Mend(10px)'}).find_next_sibling('span').text

    print(f'{name}: {symbol} {change} {percent_change}')