import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# %matplotlib inline

from urllib.request import urlopen
from bs4 import BeautifulSoup


# specify the URL containing the dataset and pass it to urlopen() to get the html of the page.
url = "https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Intakes/wter-evkm"
html = urlopen(url)

# create a Beautiful Soup object from the html.
soup = BeautifulSoup(html, 'lxml')
type(soup)

"""

Sample Output
```
<title>Austin Animal Center Intakes | Open Data | City of Austin Texas</title>
```

"""

# The soup object allows you to extract interesting information about the
# website you're scraping such as getting the title of the page as shown below.
# Get the title
title = soup.title
print(title)

# Print out the text
text = soup.get_text()
for sptxt in soup.text:
    print(sptxt)


print(soup.find_all('inital_state'))

# for meta_tag in soup('metadata-pair-value'):
#     if meta_tag['Updated'] == 'updatedAt':
#         print(meta_tag['content'])
