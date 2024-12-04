from datetime import datetime as time
import time as t
import os
import csv
from discord_webhook import DiscordWebhook, DiscordEmbed
from pyvinted import Vinted
#import utils
#from utils import filter_price, WEBHOOK_URL


# All possible size: "XS", "S", "M", "L", "XL","37","38","39","40","41","42","43","44", "Not found","XS / IT 38 / EU 34","S / IT 40 / EU 36", "M / IT 42 / EU 38","L / IT 44 / EU 40","XL / IT 46 / EU 42"
size_list =["M", "L", "XL","40","41","42","Not found","M / IT 42 / EU 38","L / IT 44 / EU 40","XL / IT 46 / EU 42"]
size_list = ["XS", "S", "M", "L", "XL","37","38","39","40","41","42","43","44", "Not found","XS / IT 38 / EU 34","S / IT 40 / EU 36", "M / IT 42 / EU 38","L / IT 44 / EU 40","XL / IT 46 / EU 42"]
last_item_id = ""
sent_items,allowed_brands,rows = [],[],[]
WEBHOOK_URL = {}

allowed_country_code = "it"
allowed_price = 2000 # your max price


csv = csv.reader(open('list.csv', 'r'))
for row in csv:
    if row == []:   continue
    allowed_brands.append(row[0].lower())
    rows.append(row)
    WEBHOOK_URL[row[0]] = row[2]

def check_price(item, rows):
    for row in rows:
        if row == []:   
            continue
        try:
            # Estrarre l'importo dal dizionario
            item_price = float(item['price']['amount'])
            max_price = float(row[1])
        except (ValueError, TypeError, KeyError):
            print(f"[ERROR] Invalid price data: {item['price']}")
            return True
        if row[0] == item['brand_title'].lower() and item_price > max_price:
            print(f"[INFO] Price not allowed: {item['price']['amount']}€ for {item['brand_title']}")
            return True
    return False

while True:
    try:
        sleep_time = 1
        t.sleep(sleep_time)
        vinted = Vinted(0)
        vinted.InitVintedSession()
        items = vinted.search(search_text="",order_type="newest_first",max_price=allowed_price)
       
        for item in items['items']:
            if item['brand_title'].lower() in allowed_brands:
                if item['id'] not in sent_items: 
                    sent_items.append(item['id'])  
                    titler = item['title'] if item['title'] else "Not found"
                    screen = item['photo'] if item['photo'] else "Not found"
                    brand = item['brand_title'] if item['brand_title'] else "Not found"
                    price = f"{item['price']}€" if isinstance(item['price'], (int, float, str)) else "Invalid"
                    if check_price(item,rows):  continue
                    total_item_price = f"{item['total_item_price']}€" if item['total_item_price'] else "Not found"
                    size = item['size_title'] if item['size_title'] else "Not found"
                    if size not in size_list and brand.lower() not in ["apple","lenovo","nintendo"]:
                            print(f"[INFO] Size not allowed: {size}")
                            continue
                    status = item['status'] if item['status'] else "Not found"
                    url = item['url'] if item['url'] else "Not found"
                    create = time.now().strftime("%Y-%m-%d %H:%M:%S")

                    webhook = DiscordWebhook(url=WEBHOOK_URL[brand.lower()])
                    embed = DiscordEmbed(title="", description=f"**[{titler}]({url})**", color=3447003)
                    embed.add_embed_field(name="", value="", inline=False)
                    embed.set_thumbnail(url="https://media.giphy.com/avatars/weworkatvinted/tNrx2pCh2ss6.png")
                    embed.set_image(url=screen['url'])
                    #embed.add_embed_field(name="🔖 Marca", value=brand, inline=True)
                    embed.add_embed_field(name="💸 **Prezzo totale**", value=f"**{total_item_price}**", inline=True)
                    embed.add_embed_field(name="📏 Taglia", value=size, inline=True)
                    embed.add_embed_field(name="📦 Stato", value=status, inline=True)
                    embed.set_footer(text="⌛ Data: "+create)
                    webhook.add_embed(embed)
                    response = webhook.execute()

                    if response.status_code == 200:
                        print('[+] Embed sent successfully.')
                    else:
                        print('[-] Failed to send embed. Status code:', response.status_code)
                else:
                    print("[INFO] Already shown")
            else:
                print(f"[INFO] Brand not allowed: {item['brand_title']}")
    except Exception as e:
        print("[INFO] Failed:", str(e))