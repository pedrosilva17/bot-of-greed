from bs4 import BeautifulSoup

# Read HTML string from file
with open('table.html', 'r') as file:
    html_string = file.read()

# Parse the HTML string
soup = BeautifulSoup(html_string, 'html.parser')

# Find all tables in the HTML
tables = soup.find_all('table')

# Iterate over each table
for table in tables:
    # print(table)
    if 'card-query-main' not in table.get('class', []):
        print("found")
        continue
    # Find all the rows in the table (excluding the header row)
    rows = table.find_all('tr')[1:]
    # print(rows)

    # Extract the values under the "Name" column
    names = [row.find('td', class_="Name").text.split() for row in rows]

    # Print the extracted names
    for name in names:
        print(name)
