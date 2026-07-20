import requests
from bs4 import BeautifulSoup

class Wikipedia:
    # Grab table result based on URL
    @staticmethod
    def grabTableResult(url: str):
        params = {}
        headers= {"User-Agent": "ImportToSpotifyBot/0.0 (https://github.com/ikoded/ImportToSpotify)"}
        request = requests.get(url,headers=headers)

        soup = BeautifulSoup(request.text,'html.parser')
        table = soup.find('table', {'class': 'wikitable'})

        return table
    
    @staticmethod
    def parsebillboardhot100(table):
        results = {}
        for row in table.find_all('tr'):
            cells = [cell.text.strip() for cell in row.find_all(['td', 'th'])]
            if(len(cells) < 4 or cells[2] == 'Artist(s)'):
                continue
            songname = cells[3]
            cleanname = songname.strip('"\' ♪[]0123456789')
            results[cleanname] = cells[2]

        return results