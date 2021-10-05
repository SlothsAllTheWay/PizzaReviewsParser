from typing import Tuple
import requests
from bs4 import BeautifulSoup
import httpx
import asyncio

BASE_URL="https://onebite.app/reviews/dave?page={}&minScore=0&maxScore=10"
NUM=37

def getData(row: BeautifulSoup)->Tuple[str]:
    score=row.find(class_="jsx-845469894 rating__score").text
    name=row.find(class_="jsx-574827726 reviewCard__title").text
    city_and_state=row.find(class_="jsx-574827726 reviewCard__location").text

    city, state=city_and_state.split(", ")

    try:
        float(score)
    except ValueError:
        score="0"

    return [score, name, city, state]

async def getFullNames(urls: dict[BeautifulSoup, str])->dict[BeautifulSoup, str]:
    async with httpx.AsyncClient() as client:
        tasks = (client.get(url, timeout=None) for url in urls.values())
        reqs = await asyncio.gather(*tasks)

    htmls = [BeautifulSoup(req.text, "html.parser") for req in reqs]
    names={item: html.find({"h1":"jsx-84601126"}).text for item, html in zip(urls.keys(), htmls)}

    return names

async def getHTMLs(urls: list[str])->list[Tuple]:
    async with httpx.AsyncClient() as client:
        tasks = (client.get(url, timeout=None) for url in urls)
        reqs = await asyncio.gather(*tasks)

    htmls = [BeautifulSoup(req.text, "html.parser") for req in reqs]
    data=[html.find_all(class_="jsx-596798944 col col--review") for html in htmls]
    rows=[]

    for item in data:
        rows.extend(item)

    data=[getData(row) for row in rows]
    
    return data, rows

def main():
    urls=[BASE_URL.format(i) for i in range(1, NUM+1)]

    data, rows=asyncio.run(getHTMLs(urls))

    urls={id(item): "https://onebite.app"+row.find(class_="jsx-574827726")["href"] for item, row in zip(data, rows) if "..." in item[1]}
        
    names=asyncio.run(getFullNames(urls))

    for item in data:
        try:
            item[1]=names[id(item)]
        except KeyError:
            pass

    with open("data.csv", "w", encoding="UTF-8") as f:
        f.write("score\tname\tcity\tstate\n")
        for item in data:
            f.write("\t ".join(item)+"\n")

if __name__=="__main__":
    main()