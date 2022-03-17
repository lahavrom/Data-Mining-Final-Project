import numpy as np
import requests
from bs4 import BeautifulSoup 
import pandas as pd


# adds the player's name, RPM and WIN_SHARE
def add_name_RPM_WIN(line, player_name, player_RPM, player_WIN_SHARE):
    player_name.append(line.find_all('a')[0].text)
    RPM_WIN = line.find_all('td')[-2:]
    player_RPM.append(RPM_WIN[0].text)
    player_WIN_SHARE.append(RPM_WIN[1].text)


# scrape RPM and WIN Share for each year from 2014 to 2021 for every player from ESPN
def scraper_ESPN_RPM_WIN(espn):
    for year in range(2014, 2022):
        url = espn + str(year)
        soup = BeautifulSoup(requests.get(url).content, 'html.parser')
        pages = int(soup.find_all('div', class_='page-numbers')[0].text.split(' ')[-1])
        player_name, player_RPM, player_WIN_SHARE = list(), list(), list()
        for page in range(1, pages+1):
            url = espn + str(year) + "/page/" + str(page)
            soup = BeautifulSoup(requests.get(url).content, 'html.parser')
            oddRow = soup.find_all('tr', class_='oddrow')
            evenRow = soup.find_all('tr', class_='evenrow')
            for i in range(len(oddRow)):
                add_name_RPM_WIN(oddRow[i], player_name, player_RPM, player_WIN_SHARE)
            for i in range(len(evenRow)):
                add_name_RPM_WIN(evenRow[i], player_name, player_RPM, player_WIN_SHARE)
        pd.DataFrame({"Name": player_name, "RPM": player_RPM, "WIN_SHARE": player_WIN_SHARE}).to_csv(str(year)+"_RPM_WIN_SHARE", index=False)


# scrape 2k ratings from 2k14 to 2k21
def scraper_2k_ratings(ratings_2k):
    for year in range(2014, 2022):
        url = ratings_2k + str(year-1)+"-"+str(year)
        player_name, player_rating = list(), list()
        soup = BeautifulSoup(requests.get(url).content, 'html.parser')
        content = soup.find_all('table', class_='hh-salaries-ranking-table hh-salaries-table-sortable responsive')[0].find_all('tbody')[0].find_all('tr')
        for i in range(len(content)):
            player_name.append(content[i].find_all('td', class_="name")[0].text.strip())
            player_rating.append(content[i].find_all('td', class_="value")[0].text.strip())
        pd.DataFrame({"Name": player_name, "2k Rating": player_rating}).to_csv(str(year)+"_2k_Rating", index=False)


# scrape players and his nationality
def scraper_NBA_players_nationality():
    f = open('nba.txt', 'r')
    content = f.readline()
    soup = BeautifulSoup(content, 'html.parser')
    players_name = list()
    players_country = list()
    players = soup.find_all('tr')
    for i in range(len(players)):
        name = players[i].find_all('p', class_='t6')
        players_name.append(name[0].text + ' ' + name[1].text)
        players_country.append(players[i].find_all('td', class_='text')[-1].text)
    return pd.DataFrame({"Name": players_name, "Country": players_country})


# scrape players' ages
def scraper_ages(df):
    df['birth year'] = 0
    for name in df['Name'].unique():
        url = 'https://en.wikipedia.org/wiki/' + name.replace(' ', '_')
        soup = BeautifulSoup(requests.get(url).content, 'html.parser')
        try:
            birth_year = soup.find_all('span', class_='bday')[0].text[:4]
        except:
            try:
                url += '_%28basketball%29'
                soup = BeautifulSoup(requests.get(url).content, 'html.parser')
                birth_year = soup.find_all('span', class_='bday')[0].text[:4]
            except:
                print(name)
                continue
        finally:
            df['birth year'] = np.where(df['Name'] == name, birth_year, df['birth year'])
    
    # hard coded because it is hard
    df['birth year'] = np.where(df['Name'] == 'Kevin Martin', 1983, df['birth year'])
    df['birth year'] = np.where(df['Name'] == 'Marcus Thornton', 1987, df['birth year'])
    df['birth year'] = np.where(df['Name'] == 'Mike Miller', 1980, df['birth year'])
    df['birth year'] = np.where(df['Name'] == 'Mike Dunleavy', 1980, df['birth year'])
    df['birth year'] = np.where(df['Name'] == 'Francisco Garcia', 1981, df['birth year'])
    df['birth year'] = np.where(df['Name'] == 'James Johnson', 1987, df['birth year'])
    df['birth year'] = np.where(df['Name'] == 'Reggie Williams', 1986, df['birth year'])
    df['birth year'] = np.where(df['Name'] == 'Jason Smith', 1986, df['birth year'])
    df['birth year'] = np.where(df['Name'] == 'James Jones', 1980, df['birth year'])
    df['birth year'] = np.where(df['Name'] == 'Justin Hamilton', 1990, df['birth year'])
    df['birth year'] = np.where(df['Name'] == 'Malcolm Thomas', 1988, df['birth year'])
    df['birth year'] = np.where(df['Name'] == 'Justin Jackson', 1995, df['birth year'])
    df['birth year'] = np.where(df['Name'] == 'Troy Williams', 1995, df['birth year'])
    df['birth year'] = np.where(df['Name'] == 'Alen Smailagic', 2000, df['birth year'])
    df['birth year'] = np.where(df['Name'] == 'Justin Robinson', 1997, df['birth year'])
    df['birth year'] = np.where(df['Name'] == 'Moses Brown', 1999, df['birth year'])
    df['birth year'] = np.where(df['Name'] == 'Louis King', 1999, df['birth year'])
    df['birth year'] = np.where(df['Name'] == 'Reggie Jackson', 1990, df['birth year'])
    df['birth year'] = np.where(df['Name'] == 'Paul Watson', 1994, df['birth year'])
    df['birth year'] = np.where(df['Name'] == 'Ray McCallum', 1991, df['birth year'])
    df['birth year'] = np.where(df['Name'] == 'Gerald Henderson', 1987, df['birth year'])
    df['birth year'] = np.where(df['Name'] == 'Damian Jones', 1995, df['birth year'])
    df['birth year'] = np.where(df['Name'] == 'Bruce Brown', 1996, df['birth year'])

    df.to_csv('merged', index=False)



if __name__ == "__main__":
    scraper_ESPN_RPM_WIN("http://www.espn.com/nba/statistics/rpm/_/year/")
    scraper_2k_ratings("https://hoopshype.com/nba2k/")
    merged = pd.DataFrame()
    # merge
    for year in range(2014, 2022):
        df1 = pd.read_csv(str(year)+'_2k_Rating')
        df2 = pd.read_csv(str(year)+'_RPM_WIN_SHARE')
        out = pd.merge(df1, df2, how='inner', on='Name')
        out['Year'] = year
        out.to_csv(str(year), index=False)
        merged = pd.concat([merged, out])
    df = scraper_NBA_players_nationality()
    merged = pd.merge(merged, df, how='inner', on='Name')
    merged = merged.drop_duplicates()
    scraper_ages(merged)

    
  
