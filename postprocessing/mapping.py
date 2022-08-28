import re
from typing import List, Tuple


# Step 1 clean raw text
def clean_raw_text(raw_text: str) -> str:
    raw_text = raw_text.lower()

    # Remove anything in parentheses
    token = r"\([^)]*\)"
    clean_text = re.sub(token, "", raw_text)

    # Clean phone
    phone_token = r"(\(?\+?\d{2,2}\)?|0)[\s\-\.]*\d{3}[\s\-\.]*\d{3}[\s\-\.]*\d{3}\b"
    clean_text = re.sub(phone_token, "", clean_text)

    # Split ent between foods and prices
    token = r"(\D+\s*)(\s)([\d\,\.\w]{2,})"
    clean_text = re.sub(token, r"\g<1>\n\g<3>", clean_text)

    # Remove size entities
    token = r"size|\s+x{0,2}[lms][\.\s:-]+|(nhỏ|vừa|lớn|bự|to|small|medium|big|large):?"
    clean_text = re.sub(token, "\n", clean_text)

    return clean_text.strip()


# Step 2 get list price and food
def get_price_and_food(ents):
    # price_token = r"(\d\s?){2,}k?|(\d\s?[\.,]+)+k?|miễn\sphí|free"
    price_token = r"\d{4,}|\d+k|[\d.,]{5,}|miễn\sphí|free"

    list_price = []
    list_food = [''] * len(ents)

    for idx, ent in enumerate(ents):
        ent = ent.lower()

        # check if current token is price
        price_ent = re.search(price_token, ent)
        if price_ent:
            # format price
            price_ent = price_ent.group(0)
            price_ent = price_ent.replace("o", "0").replace("k", "000")
            price_ent = re.sub(r"[^\d]", "", price_ent)
            list_price.append([idx, price_ent])
        else:
            if ent:
                list_food[idx] = ent

    return [list_food, list_price]


def get_current_food(foods: List, current_price_idx: int):
    current_food = foods[current_price_idx - 1]

    price_token = r"\d{4,}|\d+k|[\d.,]{5,}"
    i = current_price_idx - 1
    while foods[i] != None and not re.search(price_token, foods[i]):
        current_food = foods[i] + " " + current_food
        i -= 1

    return current_food


# Step 3 mapping price and food
def map(foods: list, prices: list) -> List[List[str]]:
    menu = []

    n_prices = len(prices)
    # If only has one price on image, mapping all the food to this price
    if n_prices == 1:
        for idx, f in enumerate(foods[:-5]):
            if idx >= prices[0][0] - 1 and f:
                menu.append([f, prices[0][1]])
                foods[idx] = ''
        return menu

    i = 0
    while i < n_prices:
        current_price_ent = prices[i]
        current_price_ent_idx = current_price_ent[0]
        next_price_ent = prices[min(i + 1, n_prices - 1)]

        dis_price = next_price_ent[0] - current_price_ent_idx

        # Mapping by size
        if dis_price == 1:
            current_food = foods[current_price_ent_idx - 1]

            menu.append([current_food + " SIZE S", current_price_ent[1]])
            menu.append([current_food + " SIZE M", next_price_ent[1]])
            i += 2

            if i + 2 < n_prices:
                next_price_ent_1 = prices[i]
                dis_price_1 = next_price_ent_1[0] - next_price_ent[0]

                if dis_price_1 == 1:
                    menu.append([current_food + " SIZE L", next_price_ent_1[1]])
                    i += 1

            foods[current_price_ent_idx - 1] = ''

        # Map near
        elif dis_price == 2 or dis_price == 0:
            menu.append([foods[current_price_ent_idx - 1], current_price_ent[1]])
            foods[current_price_ent_idx - 1] = ''
            i += 1

        # Mapping group
        elif dis_price > 2:
            if i == n_prices - 1:
                for idx in range(current_price_ent_idx - 1, len(foods)):
                    food = foods[idx]
                    if food:
                        menu.append([food, current_price_ent[1]])
                        foods[idx] = ''
            else:
                for idx in range(
                    current_price_ent_idx - 1, current_price_ent_idx + dis_price
                ):
                    food = foods[idx]
                    if food:
                        menu.append([food, current_price_ent[1]])
                        foods[idx] = ''
            i += 1

    return menu
