from typing import Tuple
import requests
from bs4 import BeautifulSoup
import httpx
import asyncio

BASE_URL="https://onebite.app/reviews/dave?page={}&minScore=0&maxScore=10"
NUM=37

def getData(row: BeautifulSoup)->Tuple:
    score=row.find(class_="jsx-845469894 rating__score").text
    name=row.find(class_="jsx-574827726 reviewCard__title").text
    city_and_state=row.find(class_="jsx-574827726 reviewCard__location").text

    city, state=city_and_state.split(", ")

    """try:
        score=float(score)
    except ValueError:
        score=0"""

    return (score, name, city, state)

async def getHTMLs(urls: list[str])->list[Tuple]:
    async with httpx.AsyncClient() as client:
        tasks = (client.get(url) for url in urls)
        reqs = await asyncio.gather(*tasks)

    htmls = [BeautifulSoup(req.text, "html.parser") for req in reqs]
    data=[html.find_all(class_="jsx-574827726 reviewCard reviewCard--feedItem") for html in htmls]
    rows=[]

    for item in data:
        rows.extend(item)

    data=[getData(row) for row in rows]
    
    return data

def main():
    urls=[BASE_URL.format(i) for i in range(1, NUM+1)]

    data=asyncio.run(getHTMLs(urls))

    #for item in data:
    #    print(*item, sep="\t")

    with open("data.csv", "w") as f:
        f.write("score\tname\tcity\tstate\n")
        for item in data:
            f.write("\t ".join(item)+"\n")

if __name__=="__main__":
    main()