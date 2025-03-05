def identify_allergens(product_info):
    allergen_emojis = {
        'milk': '🥛',
        'peanuts': '🥜',
        'fish': '🐟',
        'soybeans': '🌱',
        'gluten': '🍞',
        'molluscs': '🐚',
        'nuts': '🌰',
        'eggs': '🥚',
        'sesame-seeds': '🍥',

    }
    allergens = product_info.get("allergens_tags", [])
    common_allergens = ['milk', 'peanuts', 'fish', 'soybeans', 'gluten', 'molluscs', 'nuts', 'eggs', 'sesame-seeds']

    if allergens:
        allergens = allergens[0]

        unsuitable = [a for a in common_allergens if a in allergens]
        suitable = [a for a in common_allergens if a not in allergens]

        suitable_allergens = [f"{allergen_emojis.get(a, '')} {a.title()}" for a in suitable]
        unsuitable_allergens = [f"{allergen_emojis.get(a, '')} {a.title()}" for a in unsuitable]
        return suitable_allergens, unsuitable_allergens

    else:
        suitable_allergens = [f"{allergen_emojis.get(a, '')} {a.title()}" for a in common_allergens]
        return suitable_allergens, []
