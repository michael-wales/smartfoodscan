def check_labels(product):
    product_labels = product.get("ingredients_analysis_tags", [])
    allergens = product.get("allergens_tags", [])

    labels = {'vegan':None,
              'vegetarian':None,
              'palm-oil-free':None,
              'gluten-free': 'yes',
              'lactose-free': 'yes'}

    if product_labels:
        if "en:vegan" in product_labels:
            labels['vegan']='yes'
        elif "en:non-vegan" in product_labels:
            labels['vegan']='no'
        elif "en:maybe-vegan" in product_labels:
            labels['vegan']='maybe'
        elif "en:vegan-status-unknown" in product_labels:
            labels['vegan'] = 'maybe'

        if "en:vegetarian" in product_labels:
            labels['vegetarian']='yes'
        if "en:non-vegetarian" in product_labels:
            labels['vegetarian']='no'
        if "en:maybe-vegetarian" in product_labels:
            labels['vegetarian']='maybe'
        elif "en:vegetarian-status-unknown" in product_labels:
            labels['vegetarian'] = 'maybe'

        if "en:palm-oil-free" in product_labels:
            labels['palm-oil-free']='yes'
        if "en:palm-oil" in product_labels:
            labels['palm-oil-free']='no'

    if allergens:
        allergens = allergens[0]
        if "en:milk" in allergens:
            labels['lactose-free'] = 'no'

        if "en:gluten" in allergens:
            labels['gluten-free'] = 'no'
    print(allergens)
    print(labels)
    return labels
