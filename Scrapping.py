import sqlite3
import ssl
import re
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

#Creating SQLitefile
conn = sqlite3.connect('Product_List.sqlite')
cur = conn.cursor()


baseurl0 = input("Enter URL from openfoodfacts.com/category : ")
if ( len(baseurl0) < 5 ) :
    baseurl0 = "https://pt-en.openfoodfacts.org/category/biscuits/"

#creating TABLE Products, with name url and grade
cur.execute('''DROP TABLE IF EXISTS Products ''')
cur.execute('''CREATE TABLE IF NOT EXISTS Products
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
     product_name TEXT,
     url TEXT,
     grade TEXT) ''')


countdown = int(input("How many pages?  "))
count = 0

while True:
    if  countdown == 0 :
        print("_______")
        print(" ")
        print("All pages scrapepd!")
        print("_______")
        break
    try:
        countdown-= 1
        count+= 1
        baseurl = baseurl0 + str(count)
        print("Scrapping of :  ", baseurl)
        u_client = uReq(baseurl, context=ctx)
        html_page = u_client.read().decode()
        u_client.close()

        page_soup = soup(html_page, "html.parser")
        containerAll = page_soup.findAll("ul", {"class":"products"})
        container = containerAll[0]
        all_products = container.findAll("a")

        # Finding url, name and grade of a product
        for line in all_products:
            line = str(line)
            try:
                urlL = re.findall('href="(\S.*)"\s.*', line) #second url part
                urlStart = "https://pt-en.openfoodfacts.org"
                urlSt = urlStart.join(urlL)
                url = urlStart + urlSt
                #Looking for name
                name = re.findall('<span>(\S.*)\s-.*', line) #name
                name = name[0]
            
                u_client_1 = uReq(url, context=ctx)
                html_page_1 = u_client_1.read().decode()
                u_client_1.close()
                #looking for a grade
                page_soup_1 = soup(html_page_1, "html.parser")
                containerAll_1 = page_soup_1.findAll("a", {"title":"How the color nutrition grade is computed"})
                try:
                    way = containerAll_1[1].img
                    grade = way.get("alt")
                    grade = re.findall(".+\s(\S)", grade)
                    grade = grade[0]
                    print(name, "has a", grade, "grade")           
                except IndexError:
                    grade = " NO "
                    print(name, "has", grade, "GRADE")
                    cur.execute('''INSERT OR IGNORE INTO Products (product_name, url, grade)
                        VALUES (?, ?, ? )''', ( name, url, grade ) )
                    conn.commit()
                    continue

                cur.execute('''INSERT OR IGNORE INTO Products (product_name, url, grade)
                            VALUES (?, ?, ? )''', ( name, url, grade ) )
                conn.commit()
            except:
                print("Page not compleate")
            continue
    except KeyboardInterrupt:
        print('')
        print('Program interrupted by user...')
        break
    except ValueError:
        print('')
        print('Value Error...')
        break
