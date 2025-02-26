def check_labels(product):
    product_labels = product.get("ingredients_analysis_tags", [])
    labels = {'vegan':None,'vegetarian':None, 'palm-oil-free':None }
    if product_labels:
        if "en:vegan" in product_labels:
            labels['vegan']='yes'
        if "en:non-vegan" in product_labels:
            labels['vegan']='no'
        if "en:maybe-vegan" in product_labels:
            labels['vegan']='maybe'
        if "en:vegetarian" in product_labels:
            labels['vegetarian']='yes'
        if "en:non-vegetarian" in product_labels:
            labels['vegetarian']='no'
        if "en:maybe-vegetarian" in product_labels:
            labels['vegetarian']='maybe'
        if "en:palm-oil-free" in product_labels:
            labels['palm-oil-free']='yes'
        if "en:palm-oil" in product_labels:
            labels['palm-oil-free']='no'
    else:
        None
    return labels
