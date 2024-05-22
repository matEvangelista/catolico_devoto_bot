import telebot
from bs4 import BeautifulSoup
import requests as re
from os import environ
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = environ['API_TOKEN']

bot = telebot.TeleBot(API_TOKEN)


# FUNÇÕES DE APOIO
def return_soup() -> BeautifulSoup:
    """
    Função para retornar um objeto BeautifulSoup gerado a partir do site da canção nova
    :return: BeautifulSoup da Canção Nova
    """
    url = "https://santo.cancaonova.com/"
    html_content = re.get(url).content
    return BeautifulSoup(html_content, 'html.parser')


def get_prayer_source(soup: BeautifulSoup) -> str:
    """
    Retorna oração do santo e fonte
    :param soup: soup gerada
    :return: oração do santo e fonte
    """
    pos = 0
    paragraph_list = soup.find('div', attrs={'class': 'content-santo'}).findChildren('p')
    for i in range(len(paragraph_list)):
        if paragraph_list[i].text.strip().lower() == 'a minha oração':
            pos = i + 1
    prayer = paragraph_list[pos].text.strip()
    return "Oração:\n<i>" + prayer + "</i>\n\nFonte: Canção Nova"


def get_saint_name(soup: BeautifulSoup) -> str:
    """
    Retorna o nome do santo
    :param soup: soup da página
    :return: nome do santo com html
    """
    return "<b>" + soup.find('h1', attrs={'class': 'entry-title'}).text.strip() + "</b>\n\n"


# FUNÇÕES DE INTERAÇÃO

# Define a command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_photo(message.chat.id,
                   "https://th.bing.com/th/id/OIG4..hzEazUio1m9jxK_R.pz?pid=ImgGn",
                   "*Seja muito bem-vindo ao bot católico!*\n\n"
                   "Aqui você pode encontrar folheto da missa dominical, encontrar a oração do santo dia e"
                   "buscar versículos da Bíblia\n\n"
                   "Descubra nossos comandos com /info. Em desenvolvimento", parse_mode='Markdown')


@bot.message_handler(commands=['info'])
def send_info(message):
    bot.reply_to(message,
                 "<b>Lista de comandos:\n</b>"
                 "/santo_do_dia: retorna imagem e oração do santo do dia\n"
                 "/folheto: folheto da missa dominical\n"
                 "/biblia: escreva \"/biblia sigla:versiculo\" para um versículo "
                 "ou \"biblia sigla:versiculo1-versiculo2\".\n"
                 "Por exemplo: \"Mt 16:18\" ou \"Jo 15:1-9\"\n"
                 "Caso não conheça as siglas de cor, digite /sigla")


# funcao para santo do dia
@bot.message_handler(commands=['santo_do_dia'])
def send_saint(message):
    try:
        soup = return_soup()
        string = get_saint_name(soup) + get_prayer_source(soup)
        src = soup.find_all('img')[1]['src']
        bot.send_photo(message.chat.id,
                       photo=src,
                       caption=string, parse_mode='html')
    except Exception as e:
        print(e)
        bot.reply_to(message, "Infelizmente, não foi possível executar este comando.")


@bot.message_handler(commands=['folheto'])
def send_folheto(message):
    url = "https://www.arqrio.com.br/app/painel/amissa/amissa.pdf"
    bot.send_document(message.chat.id,
                      document=url,
                      caption="*Folheto para a santa missa dominical*.\n\n"
                              "_Obs: Canções podem variar entre paróquias_",
                      parse_mode='Markdown')


@bot.message_handler(commands=['biblia', 'bíblia'])
def send_bible_verses(message):
    mess = message.text.lower()
    if 'bíblia' in mess:
        mess.replace("bíblia", "biblia")
    try:
        if '/' in ''.join(mess.split(' ')[1:]) or mess[mess.find(' ') + 1:].strip().count(' ') > 1:
            raise ValueError
        elif '-' in mess:
            mess = '/'.join(mess.split(' ')[1:]).replace(':', '/')
        else:
            mess = '/'.join(mess.split(' ')[1:]).replace(':', '/')
        resp = re.get("https://biblia-api-flask.onrender.com/" + mess)
        if resp.status_code == 404:
            raise ValueError
        bot.reply_to(message, resp.json()['data'])
    except ValueError:
        bot.reply_to(message, "Por favor, digite no padrão `sigla_livro capitulo:versiculo1-versiculo2` ou "
                              "`sigla_livro capitulo:versiculo`\n\n Caso tenha dificuldade, digite /siglas",
                     parse_mode="Markdown")


@bot.message_handler(commands=['siglas'])
def send_bible_short(message):
    string = ""
    for key in bible_short.keys():
        string += str(key) + ": " + bible_short[key] + "\n"
    bot.reply_to(message, string)


# será removido
bible_short = {
    "Gênesis": "Gn",
    "Êxodo": "Ex",
    "Levítico": "Lv",
    "Números": "Nm",
    "Deuteronômio": "Dt",
    "Josué": "Js",
    "Juízes": "Jz",
    "Rute": "Rt",
    "1 Samuel": "1Sm",
    "2 Samuel": "2Sm",
    "1 Reis": "1Rs",
    "2 Reis": "2Rs",
    "1 Crônicas": "1Cr",
    "2 Crônicas": "2Cr",
    "Esdras": "Ed",
    "Neemias": "Ne",
    "Tobias": "Tb",
    "Judite": "Jt",
    "Ester": "Et",
    "1 Macabeus": "1Mc",
    "2 Macabeus": "2Mc",
    "Jó": "Jó",
    "Salmos": "Sl",
    "Provérbios": "Pr",
    "Eclesiastes": "Ec",
    "Cântico dos Cânticos": "Ct",
    "Sabedoria": "Sb",
    "Eclesiástico": "Eclo",
    "Isaías": "Is",
    "Jeremias": "Jr",
    "Lamentações": "Lm",
    "Baruc": "Br",
    "Ezequiel": "Ez",
    "Daniel": "Dn",
    "Oséias": "Os",
    "Joel": "Jl",
    "Amós": "Am",
    "Abdias": "Abd",
    "Jonas": "Jn",
    "Miquéias": "Mq",
    "Naum": "Na",
    "Habacuque": "Hc",
    "Sofonias": "Sf",
    "Ageu": "Ag",
    "Zacarias": "Zc",
    "Malaquias": "Ml",
    "Mateus": "Mt",
    "Marcos": "Mc",
    "Lucas": "Lc",
    "João": "Jo",
    "Atos dos Apóstolos": "At",
    "Romanos": "Rm",
    "1 Coríntios": "1Cor",
    "2 Coríntios": "2Cor",
    "Gálatas": "Gl",
    "Efésios": "Ef",
    "Filipenses": "Fl",
    "Colossenses": "Cl",
    "1 Tessalonicenses": "1Ts",
    "2 Tessalonicenses": "2Ts",
    "1 Timóteo": "1Tm",
    "2 Timóteo": "2Tm",
    "Tito": "Tt",
    "Filemon": "Flm",
    "Hebreus": "Hb",
    "Tiago": "Tg",
    "1 Pedro": "1Pd",
    "2 Pedro": "2Pd",
    "1 João": "1Jo",
    "2 João": "2Jo",
    "3 João": "3Jo",
    "Judas": "Jd",
    "Apocalipse": "Ap"
}
bot.polling()
