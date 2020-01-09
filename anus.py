import configparser
import discord
import psycopg2
from itertools import islice

client = discord.Client()
PageSize = 10
config = configparser.ConfigParser()
config.read('anusconf.cfg')

def get_db()
    wtf = config['wtf']
    host = wtf['dbhost']
    name = wtf['name']
    user = wtf['user']
    pswd = wtf['dbpass']
   
    return psycopg2.connect(host = host, dbname = name, user = user, password = pswd)  

async def random_wtf(message, db, cnt):
    cnt = min(cnt, 42)
    cur = db.cursor()
    cur.execute("SELECT sub.keyword FROM (SELECT DISTINCT keyword FROM wtf) AS sub ORDER BY RANDOM() LIMIT %s", (cnt,))
    keywords = []
    for res in cur:
        keywords.append(res[0])
    cur.execute("SELECT keyword, STRING_AGG(value, ', ' ORDER BY created ASC) FROM wtf \
                 WHERE keyword IN %s GROUP BY keyword", (tuple(keywords), ))
    for res in cur:
        await message.channel.send('%s: %s' % (res[0], res[1]))

async def find_wtf(message, db, keyword):
    cur = db.cursor()
    cur.execute("SELECT keyword, STRING_AGG(value, ', ' ORDER BY created ASC) FROM wtf WHERE keyword ILIKE %s GROUP BY keyword", (keyword,))
    if cur.rowcount > 0:
        for res in cur.fetchall():
            await message.channel.send('%s: %s' % (res[0], res[1]))
    else:
        await message.channel.send('%s: WAT?' % keyword)

async def remove_from_wtf(message, db, keyword, wtf):
    cur = db.cursor()
    cur.execute("DELETE FROM wtf WHERE keyword = %s AND value = %s", (keyword, wtf))
    db.commit()        
    cur.execute("SELECT keyword, STRING_AGG(value, ', ' ORDER BY created ASC) FROM wtf WHERE keyword = %s GROUP BY keyword", (keyword,))
    if cur.rowcount > 0:
        res = cur.fetchone()
        await message.channel.send('%s: %s' % (res[0], res[1]))
    else:
        await message.channel.send('%s: IT\'S GONE, OK?' % keyword)

async def append_to_wtf(message, db, keyword, wtf):
    cur = db.cursor()
    for val in wtf.split(','):
        v = val.strip()
        if not v:
            continue
        cur.execute("INSERT INTO wtf (keyword, value) VALUES (%s, %s)", (keyword, v))
    db.commit()
    await find_wtf(message, db, keyword)

async def replace_wtf(message, db, keyword, wtf):
    cur = db.cursor()
    cur.execute("DELETE FROM wtf WHERE keyword = %s", (keyword,))
    await append_to_wtf(bot, db, keyword, wtf)


    return psycopg2.connect(host = host, dbname = name, user = user, password = pswd)

async def wtf(message):
    """Hovna z pctuningu. 'wtf [slovo]' nebo 'wtf slovo +/-/= kravina'"""
    trigger = message.remove('wtf ')
    db = get_db(bot)
    if db == None:
        return message.channel.send('I\'m not configured!')

    if not trigger.group(2) or trigger.group(2).isnumeric():
        random_wtf(bot, db, 1 if not trigger.group(2) else int(trigger.group(2)))
        return

    cmd = trigger.group(2).split(' ', 2)
    if len(cmd) == 1:
        find_wtf(bot, db, cmd[0])
    elif len(cmd) == 3:
        if cmd[1] == '-':
            remove_from_wtf(bot, db, cmd[0], cmd[2])
        elif cmd[1] == '+':
            append_to_wtf(bot, db, cmd[0], cmd[2])
        elif cmd[1] == '=':
            replace_wtf(bot, db, cmd[0], cmd[2])
        else:
            return bot.reply('Vo co se jako pokoušíš?')

@client.event
async def on_message(message):
    if message.content.startswith('wtf'):
        wtf(message)

@client.event
async def on_ready():
    print('logged in as {0.user}'.format(client))
    discord = config['discord']
    apikey = discord['apikey']
client.run(apikey)
