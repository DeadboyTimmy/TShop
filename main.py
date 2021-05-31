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

def add_goods(name, price, id, amount):
        id_shop = 0
        nam = ''
        connection = getConnection()
        try:
            with connection.cursor() as cursor:
                    sql = "SELECT id FROM Shops WHERE owner_id = %s"
                    cursor.execute(sql, id)
                    rows = cursor.fetchall()
                    for row in rows:
                        id_shop = int(row['id'])
            if id_shop == 0:
                return 0
        except:
            return 0
        try:
            with connection.cursor() as cursor: 
                    sql = "SELECT amount FROM Products WHERE name = %s"
                    cursor.execute(sql, name)
                    rows = cursor.fetchall()
                    for row in rows:
                        amount += row['name']
        except Exception:
            amount = amount

        try:
            with connection.cursor() as cursor:
                    cursor.execute('INSERT INTO Products VALUES(%s,%s,%s,%s,%s)',(0, name, price, id_shop, amount))
                    connection.commit()
            with connection.cursor() as cursor: 
                    sql = "SELECT name FROM Shops WHERE owner_id = %s"
                    cursor.execute(sql, id)
                    rows = cursor.fetchall()
                    for row in rows:
                        nam = row['name']
            return nam
        except Exception:
            return 0

def remove_good(name, id, amount):
    connection = getConnection()
    if amount == 0:
        #try:
            with connection.cursor() as cursor:
                sql = "SELECT id From Shops WHERE owner_id = %s"
                cursor.execute(sql, id)
                rows = cursor.fetchall()
                for row in rows:
                            id_shop = row['id']
            with connection.cursor() as cursor:    
                sql = "DELETE From Products WHERE name = %s AND id_shop = %s"
                cursor.execute(sql, (str(name), int(id_shop)))
                connection.commit()
            with connection.cursor() as cursor:
                sql = "SELECT name From Shops WHERE owner_id = %s"
                cursor.execute(sql, id)
                rows = cursor.fetchall()
                for row in rows:
                            name_shop = row['name']
            return name_shop
        #except Exception:
            #return 0
    else:
        try:
            amount = -amount
            with connection.cursor() as cursor:
                    sql = "SELECT id_shop From Shops WHERE owner_id = %s"
                    cursor.execute(sql, id)
                    rows = cursor.fetchall()
                    for row in rows:
                                id_shop = row['id_shop']
            with connection.cursor() as cursor:
                    sql = "SELECT amount From Products WHERE name = %s"
                    cursor.execute(sql, name)
                    rows = cursor.fetchall()
                    for row in rows:
                                amoun = row['amount']
            amount = amoun + amount
            with connection.cursor() as cursor:    
                    sql = "UPDATE Products SET amount = %s WHERE id_shop = %s"
                    cursor.execute(sql, (amount, id_shop))
                    connection.commit()
            with connection.cursor() as cursor:
                sql = "SELECT name From Shops WHERE owner_id = %s"
                cursor.execute(sql, id)
                rows = cursor.fetchall()
                for row in rows:
                            name_shop = row['name']
            return name_shop
        except:
            return 0    

class MyClient(discord.Client):
    
    async def on_ready(self):
        print('Программа {0} запущена!'.format(self.user))
    async def on_message(self, message):
        if message.author != client.user:
            if str(message.channel).find('Direct Message with') != -1:
                text = str(message.content)
                if text == "!help":
                    await message.author.send(
                        ">>> *Список доступных команд:*\n**!make_order:** - заказать товар\n**!create_shop:** - создать магазин\n**!add_goods:** - добавить товар и его цену\n**!remove_good:** - удалить товар из своего магазина"
                    )
                    await message.author.send(">>> *Примеры:*\n**!make_order:** Элитры, Timmy's World, 100\n**!create_shop:** Timmy's World\n**!add_goods:** Тотем, 5, 5\n**!remove_good:** Тотем")
                
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
                        id = int(info[-1])
                        user = await client.fetch_user(int(id))
                        msg = 'Вам пришел заказ на ' + str(amount) + ' товара «' + str(product) + '» на сумму ' + str(total_price)+ ' АР'
                        await user.send(msg)
                    else:
                        await message.author.send('**Ошибка заказа. Попробуйте еще раз.**')

                elif text.find('!create_shop') != -1:
                    owner_id = int(message.author.id)
                    name = str(text[text.find(':')+2:])
                    if create_shop(name, owner_id) == 1:
                        await message.author.send('>>> Ваш магазин «' + name + '» успешно зарегистрирован. Теперь вы можете добавить товары.')
                        my_channel = await client.fetch_channel(845345224461123619)
                        msg = await my_channel.send(">>> **----{" + str(name) + "}----**\nПока товаров нет!\nВладелец: <@"+ str(owner_id) +">")
                    else:
                        await message.author.send('**Ошибка. Попробуйте еще раз или проверьте наличие магазина.**')

                elif text.find('!add_goods:') != -1:
                    name = text[text.find(':')+2:text.find(',')]
                    price = text[text.find(',')+2:text.rfind(',')]
                    amount = text[text.rfind(',')+2:]
                    id = message.author.id
                    result = add_goods(name, price, id, amount)
                    if result != 0:
                        await message.author.send('>>> Успешно. Товар добавлен в список продаваемых товаров.')
                        channel = client.get_channel(845345224461123619)
                        messages = await channel.history(limit=200).flatten()
                        for msg in messages:
                            res = msg.content.find(str(result))
                            if res != -1:
                                text = text[:text.find("Владелец")] + '\n' + name + ': ' + price + 'АР -' + amount + 'штук' + text[text.find("Владелец"):]
                                await msg.edit(content = text)
                            else:
                                pass
                    else:
                        await message.author.send('**Ошибка. Попробуйте еще раз.**')

                                
                elif text.find("!remove_good:") != -1:
                    m = ''
                    id = int(message.author.id)
                    info = text.find(',')
                    if text.find(',') != -1:
                        name = text[text.find(":")+2:text.find(',')]
                        amount = text[text.rfind(','):]
                        result = remove_good(name, id, amount) 
                    else:
                        name = text[text.find(":"):]
                        result = remove_good(name, id, 0) 
                    if result != 0:
                        await message.author.send(">>> Успешно. Товар удален из списка продаваемых.")
                        channel = client.get_channel(845345224461123619)
                        messages = await channel.history(limit=200).flatten()
                        for msg in messages:
                            res = msg.content.find(str(result))
                            print(res)
                            await msg.edit(content=m)
                    else:
                        await message.author.send('**Ошибка. Попробуйте еще раз.**')

                
client = MyClient()
client.run(settings['token'])