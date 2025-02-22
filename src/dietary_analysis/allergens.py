import re
def identify_allergens(ingredients):
    allergen_list = {
        "Wheat": ["wheat", "spelt", "durum", "semolina", "farro"],
        "Milk": ["whey","casein","lactose","milk", "cream", "butter", "cheese", "yogurt"],
        "Egg": ["egg", "ovalbumin", "albumin"],
        "Peanuts": ["peanut","groundnuts"],
        "Soy": ["soy", "soybean", "tofu", "miso", "tempeh"],
        "Fish": ["salmon", "tuna", "cod", "haddock", "anchovy","halibut","mackarel","bass","sardines","trout","snapper","sole"],
        "Shellfish": ["shrimp", "crab", "lobster", "prawn", "scallop","clams","oyster","squid","octopus","crawfish","mussels"],
        "Tree nuts": ["walnut", "cashew", "pecan", "hazelnut", "pistachio"],
        "Sesame": ["sesame", "tahini"],
        }

    found_allergens = {}
    ingredients = [i.lower().strip() for i in ingredients]

    for allergen, keywords in allergen_list.items():
        matches = [item for item in ingredients if any(re.search(rf"\b{kw}\b", item, re.IGNORECASE) for kw in keywords)]
        found_allergens[allergen] = "Contains" if matches else "Free"

    return found_allergens
