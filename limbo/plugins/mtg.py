"""!mtg <search term> search Gatherer for information about a specific card"""

import re
from mtgsdk import Card
from string import Template

def rendercard(card):
    template_string = """$name - $mana_cost
$rarity
$setName
$type
Card text: $text
$flavor
"""
    if("Planeswalker" in card.types):
        template_string += "Loyalty: $loyalty\n"
    if("Creature" in card.types):
        template_string += "P/T: $power / $toughness"
    if("image_url" in card.__dict__):
        template_string += "$image_url"

    card_template = Template(template_string)
    return card_template.safe_substitute(card.__dict__)

def mtg(searchstring, unsafe=False):
    if(re.search(r":", searchstring)):
        return advancedsearch(searchstring)
    else:
        cards = Card.where(name=searchstring, page=0, pageSize=1).all()
        if cards:
            return cards[0].image_url
        else:
            return

def advancedsearch(searchstring):
    searchterms = parseterms(searchstring)
    if(len(searchterms) == 0):
        return
    if("limit" in searchterms):
        limit = int(searchterms['limit'])
        del searchterms['limit']
        searchterms['page'] = 0
        searchterms['pageSize'] = limit
    print(searchterms)
    cards = Card.where(**searchterms).all()
    print(cards)
    if(cards):
        renderedcards = []
        for card in cards:
            renderedcards.append(rendercard(card))
        return "\n".join(renderedcards)
    else:
        return

def parseterms(searchstring):
    searchterms = {}
    for attr, value in Card().__dict__.items():
        pattern = attr + ":(\w*)"
        match = re.findall(pattern, searchstring)
        if(match):
            searchterms[attr] = match[0]
    limitmatch = re.findall(r"limit:(\w*)", searchstring)
    if(limitmatch):
        searchterms['limit'] = limitmatch[0]

    return searchterms

def on_message(msg, server):
    text = msg.get("text", "")
    match = re.findall(r"!mtg (.*)", text)
    if not match:
        return

    searchstring = match[0]
    return mtg(searchstring)
