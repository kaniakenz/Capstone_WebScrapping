from flask import Flask, render_template 
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import base64
import matplotlib.pyplot as plt

app = Flask(__name__)

def scrap(url):
    #This is fuction for scrapping
    url_get = requests.get(url)
    soup = BeautifulSoup(url_get.content,"html.parser")
    
    #Find the key to get the information
    table = soup.find('div', attrs={'class':'lister list detail sub-list'})
    rowDiv = table.find_all('div',attrs={'class':'lister-item mode-advanced'})

    temp = [] #initiating a tuple

    for i in range(0, len(rowDiv)):

        #get title
        title = rowDiv[i].find('h3',attrs={'class':'lister-item-header'}).find('a').text
        title = title.strip() #for removing the excess whitespace
        #get rating
        rating = rowDiv[i].find('div',attrs={'class':'inline-block ratings-imdb-rating'}).text
        rating = rating.strip() #for removing the excess whitespace
        #get meta score
        if(rowDiv[i].find('span',attrs={'class':'metascore favorable'})) is None: 
            metascore = '0'
        else:
            metascore = rowDiv[i].find('span',attrs={'class':'metascore favorable'}).text
        metascore = metascore.strip()
        #votes
        votes = rowDiv[i].find('span',attrs={'name':'nv'}).text
        votes = votes.strip()

        temp.append((title,rating,metascore,votes)) 

    temp = temp[::-1] #remove the header
    df = pd.DataFrame(temp, columns= (('title','rating','metascore','votes')))
    #df = pd.DataFrame(temp, columns = (('title','rating','metascore','votes')) #creating the dataframe
    #data wranggling -  try to change the data type to right data type
    df['rating'] = df['rating'].astype('float')
    df['metascore'] = df['metascore'].astype('float')
    df['title'] = df['title'].astype('category')
    df['votes'] = df['votes'].str.replace(',', '')
    df['votes'] = df['votes'].astype('int')
    #end of data wranggling

    return df

@app.route("/")
def index():
    df = scrap('https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31') #insert url here

    #This part for rendering matplotlib
    fig = plt.figure(figsize=(5,2),dpi=300)
    df.plot()
    
    #Do not change this part
    plt.savefig('plot1',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table
    df = df.to_html(classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=df, result=result)


if __name__ == "__main__": 
    app.run()
