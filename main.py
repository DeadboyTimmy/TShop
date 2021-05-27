import discord
import os
import pymysql.cursors
import keep_alive

keep_alive.keep_alive()
settings = {'token': os.getenv("TOKEN"), 'id': os.getenv("ID")}
text_last = []

def getConnection():
    tries = 0
    while tries < 2:
        tries += 1
        try:
            connection = pymysql.connect(
                host=os.getenv("HOST"),
                user=os.getenv("USER"),
                password=os.getenv("PASSWORD"),
                db=os.getenv("DB"),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)
            return connection
        except:
            print("ERROR during connecting to MySQL...reconnecting, tries = " +
                  tries)
    return None

def check_shop(id):
    connection = getConnection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id_shop From Shops WHERE owner_id_ds = %s"
            cursor.execute(sql, id)
            rows = cursor.fetchall()
            for row in rows:
                id_shop = row['id_shop']
        return id_shop
    except Exception:
        return 0
        
def choose_order(text):
    shops, shops_names, prices = [], [], []
    to_return = dict({'example': 0})
    product = text[text.find(" ") + 1:]
    connection = getConnection()
    with connection.cursor() as cursor:
        sql = "SELECT id_shop From Products WHERE name_product = %s"
        cursor.execute(sql, product)
        rows = cursor.fetchall()
        for row in rows:
            shops.append(row['id_shop'])
    for i in shops:
        with connection.cursor() as cursor:
            sql = "SELECT name From Shops WHERE id_shop = %s"
            cursor.execute(sql, i)
            rows = cursor.fetchall()
            for row in rows:
                shops_names.append(row['name'])
    if len(shops_names) == 0:
        return (0)
    for i in shops:
        with connection.cursor() as cursor:
            sql = "SELECT price From Products WHERE id_shop = %s"
            cursor.execute(sql, i)
            rows = cursor.fetchall()
            for row in rows:
                prices.append(row['price'])
    to_return = dict(zip(shops_names, prices))
    return to_return

def make_order(text):
    text = text[text.find(':') + 2:]
    text = text.split(', ')
    product = text[0]
    shop_name = text[1]
    amount = text[2]
    city = text[3]
    connection = getConnection()
    with connection.cursor() as cursor:
            sql = "SELECT id_shop FROM Shops WHERE name = %s"
            cursor.execute(sql, shop_name)
            rows = cursor.fetchall()
            for row in rows:
                shop_id = row['id_shop']
    with connection.cursor() as cursor:
            sql = "SELECT price FROM Products WHERE id_shop = %s"
            cursor.execute(sql, shop_id)
            rows = cursor.fetchall()
            for row in rows:
                price = row['price']
    total_price = int(price) * int(amount)
    return_to = []
    return_to.append(amount)
    return_to.append(product)
    return_to.append(total_price)
    return_to.append(city)
    return_to.append(shop_id)
    return return_to

def confirm_order(array):
    amount = int(array[0])
    product = str(array[1])
    total_price = int(array[2])
    city = str(array[3])
    user_id = int(array[5])
    shop_id = int(array[4])
    connection = getConnection()
    try:
        with connection.cursor() as cursor:
                cursor.execute('INSERT INTO Orders VALUES(%s,%s,%s,%s,%s,%s,%s)',(0, user_id, product, amount, total_price, shop_id, city))
                connection.commit()
        with connection.cursor() as cursor:
            sql = "SELECT owner_id_ds FROM Shops WHERE id_shop = %s"
            cursor.execute(sql, shop_id)
            rows = cursor.fetchall()
            for row in rows:
                id = row['owner_id_ds']
            array.append(int(id))
        return array
    except Exception:
        return 0

def create_shop(name, owners_id):
    connection = getConnection()
    try:
        with connection.cursor() as cursor:
                cursor.execute('INSERT INTO Shops VALUES(%s,%s,%s)',(0, name, str(owners_id)))
                connection.commit()
        return 1
    except Exception:
        return 0

def add_goods(name, price, id):
    connection = getConnection()
    try:
        with connection.cursor() as cursor:
                sql = "SELECT id_shop FROM Shops WHERE owner_id_ds = %s"
                cursor.execute(sql, id)
                rows = cursor.fetchall()
                for row in rows:
                    id_shop = row['id_shop']
        with connection.cursor() as cursor:
                cursor.execute('INSERT INTO Products VALUES(%s,%s,%s,%s)',(0, name, price, id_shop))
                connection.commit()
        return 1
    except Exception:
        return 0

def my_shop(id):
    goods_names, goods_prices = [], []
    to_return = dict({'example': 0})
    connection = getConnection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id_shop From Shops WHERE owner_id_ds = %s"
            cursor.execute(sql, id)
            rows = cursor.fetchall()
            for row in rows:
                id_shop = row['id_shop']
        
        with connection.cursor() as cursor:
            sql = "SELECT name_product From Products WHERE id_shop = %s"
            cursor.execute(sql, id_shop)
            rows = cursor.fetchall()
            for row in rows:
                goods_names.append(row['name_product'])
        if len(goods_names) == 0:
            return 0
        else:
            with connection.cursor() as cursor:
                sql = "SELECT price From Products WHERE id_shop = %s"
                cursor.execute(sql, id_shop)
                rows = cursor.fetchall()
                for row in rows:
                    goods_prices.append(row['price'])
            to_return = dict(zip(goods_names, goods_prices))
            return to_return
    except Exception:
        return 0

def show_all():
    all_goods, all_prices, all_shops, all_ids = [], [], [], []
    connection = getConnection()
    try:
        with connection.cursor() as cursor:
                sql = "SELECT * From Products"
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    all_goods.append(row['name_product'])
                for row in rows:
                    all_prices.append(row['price'])
                for row in rows:
                    all_ids.append(row['id_shop'])
        for i in all_ids:
            with connection.cursor() as cursor:
                    sql = "SELECT name From Shops WHERE id_shop = %s"
                    cursor.execute(sql, i)
                    rows = cursor.fetchall()
                    for row in rows:
                        all_shops.append(row['name'])
        to_return = [all_goods, all_prices, all_shops]
        return to_return
    except Exception:
        return 0

def remove_good(name, id):
    connection = getConnection()
    try:
        with connection.cursor() as cursor:
                sql = "SELECT id_shop From Shops WHERE owner_id_ds = %s"
                cursor.execute(sql, id)
                rows = cursor.fetchall()
                for row in rows:
                            id_shop = row['id_shop']
        with connection.cursor() as cursor:    
                sql = "DELETE From Products WHERE name_product = %s AND id_shop = %s"
                cursor.execute(sql, (str(name), int(id_shop)))
                connection.commit()
        return 1
    except Exception:
        return 0

def change_price(id, name, new_price):
    connection = getConnection()

class MyClient(discord.Client):
    async def on_ready(self):
        print('Программа {0} запущена!'.format(self.user))
    async def on_message(self, message):
        if message.author != client.user:
            if str(message.channel).find('Direct Message with') != -1:
                text = str(message.content)
                
                if text == "!help":
                    await message.author.send(
                        ">>> *Список доступных команд:*\n**!make_order:** - заказать товар\n**!find_goods:** - посмотреть наличие товара в магазинах\n**!create_shop:** - создать магазин\n**!add_goods:** - добавить товар и его цену\n**!my_shop** - посмотреть товары, продающиеся в вашем магазине\n**!show_all** - посмотреть все продающиеся товары\n**!remove_good:** - удалить товар из своего магазина"
                    )
                    await message.author.send(">>> *Примеры:*\n**!make_order:** Элитры, Timmy's World, 100, Виленд\n**!find_goods:** Элитры\n**!create_shop:** Timmy's World\n**!add_goods:** Тотем, 5\n**!my_shop**\n**!show_all**\n**!remove_good: Тотем")
                
                elif text.find("!find_goods") != -1:
                    find_shops = choose_order(text)
                    if find_shops == 0:
                        await message.author.send(
                            ">>> Не найдено магазинов с товаром, который вы ищете.")
                    else:
                        for key in find_shops:
                            await message.author.send(">>> Найден магазин «" + str(key) + "» c ценой товара " + str(find_shops[key]) + " АР")
                
                elif text.find("!make_order") != -1:
                        total_information = make_order(text)
                        text_last.append(text)
                        await message.author.send('>>> Вы собираетесь купить '+ str(total_information[0])+' единиц товара «' + total_information[1] + '».\nИтоговая сумма заказа составляет '+ str(total_information[2])+' АР\nНапишите !confirm для подтверждения действия')
                
                elif text.find('!confirm') != -1:
                    total_information = make_order(text_last[-1])
                    total_information.append(message.author.id)
                    info =confirm_order(total_information)
                    if info != 0:
                        await message.author.send('>>> Ваш заказ принят, ждите доставки.')
                        amount = int(info[0])
                        product = str(info[1])
                        total_price = int(info[2])
                        city = str(info[3])
                        id = int(info[-1])
                        user = await client.fetch_user(int(id))
                        msg = 'Вам пришел заказ на ' + str(amount) + ' товара «' + str(product) + '» на сумму ' + str(total_price)+ ' АР из города '+ city
                        await user.send(msg)
                    else:
                        await message.author.send('**Ошибка заказа. Попробуйте еще раз.**')

                elif text.find('!create_shop') != -1:
                    owner_id = int(message.author.id)
                    name = str(text[text.find(':')+2:])
                    if create_shop(name, owner_id) == 1:
                        await message.author.send('>>> Ваш магазин «' + name + '» успешно зарегистрирован. Теперь вы можете добавить товары.')
                    else:
                        await message.author.send('**Ошибка. Попробуйте еще раз или проверьте наличие магазина.**')

                elif text.find('!add_goods') != -1:
                    name = text[text.find(':')+2:text.find(',')]
                    price = text[text.find(',')+1:]
                    if add_goods(name, price, message.author.id) == 1:
                        await message.author.send('>>> Успешно. Товар добавлен в список продаваемых товаров.')

                elif text.find('!my_shop') != -1:
                    id = int(message.author.id)
                    find_shops = my_shop(id)
                    if find_shops == 0:
                        await message.author.send('**Ошибка. Попробуйте еще раз или проверьте наличие магазина.**')
                    else:
                        for key in find_shops:
                            await message.author.send(">>> Найдена «" + str(key) + "» c ценой товара " + str(find_shops[key]) + " АР")
                elif text.find('!show_all') != -1:
                    all_goods = show_all()
                    if all_goods == 0:
                        await message.author.send('**Ошибка. Попробуйте еще раз.**')
                    else:
                        all_good = all_goods[0]
                        all_prices = all_goods[1]
                        all_shops = all_goods[2]
                        for i in range(len(all_goods)-1):
                            await message.author.send(">>> Найден товар «" + str(all_good[i]) + "» c ценой товара " + str(all_prices[i]) + " АР в магазине «" + str(all_shops[i]) +"»") 
                elif text.find("!remove_good:") != -1:
                    name = text[text.find(":")+2:]
                    id = int(message.author.id)
                    result = remove_good(name, id) 
                    if result != 0:
                        await message.author.send(">>> Успешно. Товар удален из списка продаваемых.")
                    else:
                        await message.author.send('**Ошибка. Попробуйте еще раз.**')
                elif text.find("!change_price:") != -1:
                    item = text[text.find(":")+2:text.rfind(",")]
                    price = text[text.rfind(","):]
                    id = int(message.author.id)
                    result = change_price(id, item, price)
                    if result == 0:
                        await message.author.send('**Ошибка. Попробуйте еще раз.**')
                    else:
                        await message.author.send(">>> Успешно. Цена товара изменена.")
                else:
                    await message.author.send('**Ошибка. Попробуйте еще раз.**')
                    raise Exception

client = MyClient()
client.run(settings['token'])