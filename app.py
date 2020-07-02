import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
import re
import csv
import requests

db_noticias = {'title':"init", "link":"init", "desc":"init","date":"init"}
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.config['DEBUG'] = True
app.debug = True


@app.route('/', methods=('GET', 'POST'))
def index():
    return render_template('index.html')

@app.route('/send', methods=('GET', 'POST'))
def send():
    LinkXML = ObtieneLinksRss()
    tema = request.form['buscar']
    grupo_telegam = "@telegram1"
    for Link_XML in LinkXML:
        r = RSSParser().parse(Link_XML, tema)
        enviar_noticias(r, tema, grupo_telegam)



def ObtieneLinksRss():
    arrays = []
    filename = r"C:\Users\eellena\Desktop\Scrip Python\clarin.csv"
    with open(filename) as csvarchivo:
        entrada = csv.DictReader(csvarchivo)
        for reg in entrada:
            arrays.append(reg['XML'])
    return arrays


class RSSParser( object ):
    items_regex = re.compile( '<item.*?>(.*?)<\/item>', re.S )
    details_title_regex = re.compile( '<title.*?>(.*?)<\/title>', re.S )
    details_link_regex = re.compile( '<link.*?>(.*?)<\/link>', re.S )
    details_date_regex = re.compile( '<pubDate>(.*?)<\/pubDate>', re.S )
    details_desc_regex = re.compile( '<description>(.*?)<\/description>', re.S)

    def parse(self, url, tema):
        items = []
        response = requests.get( url ).text
        tmpItems = self.items_regex.findall( response )
        for i in tmpItems:
            # armo un json con el título, link, fecha, y descripción de la noticia
            j_i = {"title": self.details_title_regex.search(i).group(1),
             "link": self.details_link_regex.search(i).group(1),
             "date": self.details_date_regex.search(i).group(1),
             "desc": self.details_desc_regex.search(i).group(1)}
            if not filtro_repetida(j_i):
                if not filtro_tema(j_i, tema):
                    items.append(j_i['link'])
        return items




def filtro_repetida(j_i):

    if (db_noticias['title'] == j_i['title'] \
    and db_noticias['link'] == j_i['link'] \
    and db_noticias['desc'] == j_i['desc']):
        r = True
    else:
        r= False
        db_noticias['title'] == j_i['title']
        db_noticias['link'] == j_i['link']
        db_noticias['desc'] == j_i['desc']
    return r


def filtro_tema(j_i, tema):
    c1 = tema in j_i['title']
    c2 = tema in j_i['desc']

    if c1 or c2:
        r=True
    else:
        r=False


def enviar_noticias(arr, tema, grupo_telegam):
    men = "- Noticias referidas al tema %s, enviadas al grupo de télegram %s: " % (tema,    grupo_telegam) + "\n"
    print(men)
    for a in arr:
        men += a + "\n"
    token = "bot1294708386:AAHCE0tRcq-hqT_b14UbHaArxs9q4XCj5fs/sendMessage"
    idchat  = "-489973892"

    requests.post('https://api.telegram.org/'+token, data={'chat_id': idchat, 'text': men})


if __name__ == "__main__":
    app.run(port=1500)
    app.debug = True