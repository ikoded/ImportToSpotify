import requests
from bs4 import BeautifulSoup

class Wikipedia:
    # Grab table result based on URL
    @staticmethod
    def grab_table_result(url: str):
        params = {}
        headers= {"User-Agent": "ImportToSpotifyBot/0.0 (https://github.com/ikoded/ImportToSpotify)"}
        request = requests.get(url,headers=headers)

        soup = BeautifulSoup(request.text,'html.parser')
        table = soup.find('table', {'class': 'wikitable'})

        return table

    # Parse result for specific page, may be brittle but necessary
    # TABLE:
    # [No , Reached No 1 , Artist(s) , Single]
    # hence cells 3 and 2 used for return values of trackname : artist in dict
    # Used for URL: https://en.wikipedia.org/wiki/List_of_Billboard_Hot_100_number-one_singles_of_the_2020s
    @staticmethod
    def parse_billboard_hot_100_2020(table):
        results = {}
        for row in table.find_all('tr'):
            cells = [cell.text.strip() for cell in row.find_all(['td', 'th'])]
            if(len(cells) < 4 or cells[2] == 'Artist(s)'): # do not have to but remove field name cell
                continue
            songname = cells[3] # Example it looks like: ['1145', '', 'Hudson Westbrook', 'House Again']
            cleanname = songname.strip('"\' ♪[]0123456789')
            results[cleanname] = cells[2]

        return results

    # Parse result for specific page, may be brittle but necessary
    # TABLE:
    # [No , Title , Artist(s)]
    # hence cells 1 and 2 used for return values of trackname : artist in dict
    # Used for URL: https://en.wikipedia.org/wiki/Billboard_Year-End_Hot_100_singles_of_{YEAR}
    @staticmethod
    def parse_billboard_hot_100_by_year(table):
        results = {}
        pastrow = None
        for row in table.find_all('tr'):
            cells = [cell.text.strip() for cell in row.find_all(['td', 'th'])]
            
            songname = cells[1] # Example it looks like: ['95', '"House Again"', 'Hudson Westbrook']
            cleanname = songname.strip('"\'')
            try:
                results[cleanname] = cells[2]
            except:
                results[cleanname] = pastrow[2] # grab from pastrow because artist can be 2 songs in a row on table (ie 2024 url)

            pastrow = cells # save in case artist is two rows in one

        return results