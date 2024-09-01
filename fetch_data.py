from collections import defaultdict
import re
import requests
import json
import unicodedata

MY_STORE_NUMBER = 544

# This code is for items that the store buys for itself like printer paper
NON_CONSUMER_PRODUCT_CODE = "D40702"

# This map is made by an ai and may not be 100% accurate
CATEGORY_CODE_MAP = {
    "D40702": { "name": "Non-consumer/non-purchaseable items for the store", "hide": False},
    "D10501": { "name": "Household items", "hide": False},
    "D20801": { "name": "Fresh Fruits", "hide": False},
    "D11732": { "name": "Canned Fish/Seafood", "hide": False},
    "D20201": { "name": "Salads and Salad Kits", "hide": False},
    "D11323": { "name": "Ice Cream", "hide": False},
    "D11315": { "name": "Frozen Meals", "hide": False},
    "D10101": { "name": "Sweets and Candy", "hide": False},
    "D10103": { "name": "Specialty Chocolate", "hide": False},
    "D10104": { "name": "Mints and Breath Fresheners", "hide": False},
    "D10105": { "name": "Gummies and Jelly Candy", "hide": False},
    "D10201": { "name": "Coffee", "hide": False},
    "D10202": { "name": "Tea", "hide": False},
    "D10203": { "name": "Tea Mixes and Concentrates", "hide": False},
    "D10301": { "name": "Crackers and Crispbreads", "hide": False},
    "D10302": { "name": "Chips and Tortilla Chips", "hide": False},
    "D10303": { "name": "Snack Mixes", "hide": False},
    "D10304": { "name": "Pretzels and Snack Crackers", "hide": False},
    "D10305": { "name": "Snacks and Jerky", "hide": False},
    "D10306": { "name": "Popcorn and Puffed Snacks", "hide": False},
    "D10400": { "name": "Cookies", "hide": False},
    "D10401": { "name": "Biscotti and Shortbread", "hide": False},
    "D10403": { "name": "Wafer Cookies and Snaps", "hide": False},
    "D10404": { "name": "Gluten-Free and Allergen-Free Cookies", "hide": False},
    "D10405": { "name": "Cookie Assortments", "hide": False},
    "D10406": { "name": "Sandwich Cookies", "hide": False},
    "D10407": { "name": "Ice Cream Cones and Novelty Ice Cream", "hide": False},
    "D10500": { "name": "Candles and Household Fabrics", "hide": False},
    "D10601": { "name": "Dietary Supplements", "hide": False},
    "D10603": { "name": "Throat Sprays and Wellness Drops", "hide": False},
    "D10604": { "name": "Multi-Vitamin Supplements", "hide": False},
    "D10605": { "name": "Collagen and Fiber Supplements", "hide": False},
    "D10606": { "name": "Protein Powders", "hide": False},
    "D10607": { "name": "Miscellaneous Vitamins and Supplements", "hide": False},
    "D10700": { "name": "Skin Care and Face Care Products", "hide": False},
    "D10701": { "name": "Body Care and Bath Products", "hide": False},
    "D10801": { "name": "Juices and Lemonades", "hide": False},
    "D10803": { "name": "Lemonades", "hide": False},
    "D10804": { "name": "Ready to Drink Teas", "hide": False},
    "D10808": { "name": "Fruit Juices and Blends", "hide": False},
    "D10809": { "name": "Non-Dairy Beverages", "hide": False},
    "D10810": { "name": "Cold Brew and Ready to Drink Coffees", "hide": False},
    "D10811": { "name": "Sodas and Sparkling Beverages", "hide": False},
    "D10812": { "name": "Sparkling Water and Mineral Water", "hide": False},
    "D10901": { "name": "Sparkling and Mineral Waters", "hide": False},
    "D10902": { "name": "Mountain Spring Water", "hide": False},
    "D11001": { "name": "Flavored Seltzers and Sparklings with Fruit Juice", "hide": False},
    "D11103": { "name": "Non-Dairy Beverages - Specialty", "hide": False},
    "D11200": { "name": "Reusable Bags and Produce Bags", "hide": False},
    "D11204": { "name": "Reusable Shopping Bags", "hide": False},
    "D11312": { "name": "Frozen Appetizers & Snacks", "hide": False},
    "D11313": { "name": "Frozen Breakfast Foods & Pancakes", "hide": False},
    "D11314": { "name": "Frozen Desserts & Treats", "hide": False},
    "D11316": { "name": "Frozen Fruits & Smoothie Ingredients", "hide": False},
    "D11317": { "name": "Frozen Meats & Seafood", "hide": False},
    "D11318": { "name": "Frozen Meatless & Plant-Based Foods", "hide": False},
    "D11319": { "name": "Frozen Pizzas & Flatbreads", "hide": False},
    "D11320": { "name": "Frozen Rice & Grain Dishes", "hide": False},
    "D11321": { "name": "Frozen Fish & Seafood", "hide": False},
    "D11322": { "name": "Frozen Vegetables & Sides", "hide": False},
    "D11324": { "name": "Frozen Breads", "hide": False},
    "D11401": { "name": "Non-Alcoholic Beer and Beverages", "hide": False},
    "D11501": { "name": "Granolas and Clusters", "hide": False},
    "D11502": { "name": "Oats and Oatmeal", "hide": False},
    "D11503": { "name": "Cereals", "hide": False},
    "D11504": { "name": "Cereal Bars and Granola Bars", "hide": False},
    "D11505": { "name": "Toaster Pastries and Baking Seeds", "hide": False},
    "D11600": { "name": "Protein Bars and Energy Bars", "hide": False},
    "D11601": { "name": "Meal Replacement Bars", "hide": False},
    "D11715": { "name": "Canned Vegetables", "hide": False},
    "D11716": { "name": "Dry Grains and Rice", "hide": False},
    "D11717": { "name": "Pasta", "hide": False},
    "D11718": { "name": "Pasta Sauces", "hide": False},
    "D11719": { "name": "Cooking Oils", "hide": False},
    "D11720": { "name": "Canned and Jarred Vegetables", "hide": False},
    "D11721": { "name": "Canned and Jarred Fruits", "hide": False},
    "D11722": { "name": "Syrups", "hide": False},
    "D11723": { "name": "Honey", "hide": False},
    "D11725": { "name": "Nut Butters and Spreads", "hide": False},
    "D11726": { "name": "Vinegars", "hide": False},
    "D11727": { "name": "Baking Mixes and Supplies", "hide": False},
    "D11728": { "name": "Spices and Seasonings", "hide": False},
    "D11729": { "name": "Olives and Pickled Vegetables", "hide": False},
    "D11731": { "name": "Canned Chicken & Poultry", "hide": False},
    "D11733": { "name": "Cooking Sauces", "hide": False},
    "D11734": { "name": "Salad Dressings", "hide": False},
    "D11735": { "name": "Canned Mediterranean Foods", "hide": False},
    "D11736": { "name": "Condiments and Sauces", "hide": False},
    "D11737": { "name": "Broths and Soups", "hide": False},
    "D11738": { "name": "Chili and Stews", "hide": False},
    "D11739": { "name": "Instant Meals", "hide": False},
    "D11740": { "name": "Salsas", "hide": False},
    "D11800": { "name": "Raw Nuts", "hide": False},
    "D11801": { "name": "Roasted & Salted Nuts", "hide": False},
    "D11802": { "name": "Savory Nut Mixes", "hide": False},
    "D11803": { "name": "Trail Mixes & Trek Mixes", "hide": False},
    "D11804": { "name": "Candied & Sweet Nuts", "hide": False},
    "D11901": { "name": "Dried Fruits", "hide": False},
    "D11902": { "name": "Fruit & Nut Bites", "hide": False},
    "D11903": { "name": "Dried Apricots", "hide": False},
    "D11904": { "name": "Dried Cranberries & Cherries", "hide": False},
    "D11905": { "name": "Fruit Bars", "hide": False},
    "D11906": { "name": "Freeze-Dried Fruits", "hide": False},
    "D11907": { "name": "Dried Mango & Tropical Fruits", "hide": False},
    "D11908": { "name": "Coconut Products", "hide": False},
    "D11909": { "name": "Raisins", "hide": False},
    "D11910": { "name": "Exotic Dried Fruits", "hide": False},
    "D12001": { "name": "Dog Food", "hide": False},
    "D12002": { "name": "Cat Food", "hide": False},
    "D12003": { "name": "Dog Treats", "hide": False},
    "D12004": { "name": "Gourmet Dog Treats", "hide": False},
    "D12005": { "name": "Cat Treats", "hide": False},
    "D20101": { "name": "Bread & Tortillas", "hide": False},
    "D20103": { "name": "Flour Tortillas", "hide": False},
    "D20104": { "name": "Specialty Breads & Rolls", "hide": False},
    "D20105": { "name": "Bagels & Sandwich Breads", "hide": False},
    "D20106": { "name": "Bakery Treats", "hide": False},
    "D20200": { "name": "Sushi Rolls", "hide": False},
    "D20202": { "name": "Refrigerated Ready-to-Eat Meals", "hide": False},
    "D20204": { "name": "Refrigerated Dips & Spreads", "hide": False},
    "D20205": { "name": "Wraps & Sandwiches", "hide": False},
    "D20206": { "name": "Pizza Dough", "hide": False},
    "D20209": { "name": "Salsa & Pico de Gallo", "hide": False},
    "D20211": { "name": "Refrigerated Salads", "hide": False},
    "D20212": { "name": "Refrigerated Soups", "hide": False},
    "D20213": { "name": "Refrigerated Burritos", "hide": False},
    "D20301": { "name": "Chicken Eggs", "hide": False},
    "D20302": { "name": "Brown Eggs", "hide": False},
    "D20304": { "name": "Large & Extra-Large Eggs", "hide": False},
    "D20305": { "name": "Organic Eggs", "hide": False},
    "D20306": { "name": "Pasture-Raised Eggs", "hide": False},
    "D20402": { "name": "Block & Shredded Cheese", "hide": False},
    "D20403": { "name": "Cheese and Cheese Alternatives", "hide": False},
    "D20500": { "name": "Creamers", "hide": False},
    "D20501": { "name": "Dairy Cream", "hide": False},
    "D20502": { "name": "Yogurt & Cottage Cheese", "hide": False},
    "D20503": { "name": "Butter", "hide": False},
    "D20504": { "name": "Plain Yogurt", "hide": False},
    "D20505": { "name": "Non-Dairy Creamers", "hide": False},
    "D20506": { "name": "Milk & Dairy Alternatives", "hide": False},
    "D20507": { "name": "Flavored Yogurts", "hide": False},
    "D20508": { "name": "Buttery Spreads", "hide": False},
    "D20509": { "name": "Half & Half & Whipping Cream", "hide": False},
    "D20510": { "name": "Almond Drinks", "hide": False},
    "D20600": { "name": "Sausages & Cooked Meats", "hide": False},
    "D20601": { "name": "Fresh Chicken & Beef", "hide": False},
    "D20602": { "name": "Fresh Seafood", "hide": False},
    "D20603": { "name": "Beef Steaks & Cuts", "hide": False},
    "D20604": { "name": "Fresh Chicken", "hide": False},
    "D20605": { "name": "Fresh Lamb", "hide": False},
    "D20606": { "name": "Pork", "hide": False},
    "D20607": { "name": "Chicken Sausages", "hide": False},
    "D20608": { "name": "Turkey", "hide": False},
    "D20609": { "name": "Salmon & Seafood", "hide": False},
    "D20700": { "name": "Cold-Pressed Juices and Shots", "hide": False},
    "D20701": { "name": "Smoothies and Fruit Juices", "hide": False},
    "D20800": { "name": "Salad Greens & Lettuce", "hide": False},
    "D20802": { "name": "Fresh Vegetables", "hide": False},
    "D20803": { "name": "Fresh Herbs", "hide": False},
    "D20901": { "name": "Indoor Plants", "hide": False},
    "D20902": { "name": "Bouquets", "hide": False},
    "D20903": { "name": "Single Stem Florals", "hide": False},
    "D21001": { "name": "Refrigerated Meats", "hide": False},
    "D21002": { "name": "Refrigerated Pasta & Ravioli", "hide": False},
    "D21003": { "name": "Refrigerated Dips & Hummus", "hide": False},
    "D21004": { "name": "Smoked Salmon & Trout", "hide": False},
    "D21005": { "name": "Refrigerated Sauces & Pesto", "hide": False},
    "D21006": { "name": "Plant-Based Proteins & Tofu", "hide": False},
    "D21007": { "name": "Refrigerated Dairy Alternatives", "hide": False},
    "D21008": { "name": "Charcuterie Meats", "hide": False},
    "D30001": { "name": "Red and White Wines", "hide": False},
    "D30010": { "name": "Flavored Canned Wines", "hide": False},
    "D30012": { "name": "Sparkling Wines & Mimosas", "hide": False},
    "D30101": { "name": "Rosé Wines", "hide": False},
    "D30106": { "name": "Specialty Red Wines", "hide": False},
    "D30107": { "name": "Dessert Wines", "hide": False},
    "D30108": { "name": "International Red Wines", "hide": False},
    "D30109": { "name": "Rosé Magnums", "hide": False},
    "D30110": { "name": "Sparkling Wines & Champagnes", "hide": False},
    "D30200": { "name": "Hard Seltzers", "hide": False},
    "D30201": { "name": "Craft Beers & Pilsners", "hide": False},
    "D30202": { "name": "Imported Beers & Ciders", "hide": False},
    "D30203": { "name": "Non-Alcoholic Beers", "hide": False},
    "D30204": { "name": "Trader Joe's Private Label Beers", "hide": False},
    "D30205": { "name": "Non-Alcoholic Beverages & Hops", "hide": False},
    "D30301": { "name": "Vodka", "hide": False},
    "D40102": { "name": "Work Apparel", "hide": True},
    "D40202": { "name": "Store Stickers & Labels", "hide": True},
    "D40302": { "name": "Demo Supplies", "hide": True},
    "D40305": { "name": "Demo Cooking Equipment", "hide": True},
    "D40400": { "name": "Fearless Flyers & Promotions", "hide": True},
    "D40401": { "name": "Store Promotions & Samples", "hide": True},
    "D40500": { "name": "Bags & Packaging", "hide": True},
    "D40599": { "name": "Additional Bags & Packaging", "hide": True},
    "D40600": { "name": "Store Forms", "hide": True},
    "D40601": { "name": "Marketing & Information Brochures", "hide": True},
    "D40602": { "name": "Consumer Literature", "hide": True},
    "D40604": { "name": "Envelopes", "hide": True},
    "D40701": { "name": "Store Signage", "hide": True},
    "D40800": { "name": "Store Equipment & Maintenance", "hide": True},
    "D40801": { "name": "Restroom Supplies", "hide": True},
    "D40802": { "name": "Janitorial & Cleaning Supplies", "hide": True},
    "D40803": { "name": "Point of Sale and Receipt Supplies", "hide": True},
    "D40804": { "name": "Store Supplies - Miscellaneous", "hide": True},
    "D40900": { "name": "Gift Cards and Gift Card Holders", "hide": True},
    "D41100": { "name": "Display Baskets", "hide": True},
    "D11714": { "name": "Spicy and Specialty Sauces", "hide": False },
    "D20100": { "name": "Specialty Bakery Items", "hide": False },
    "D20203": { "name": "Refrigerated Dips & Appetizers", "hide": False },
    "D30002": { "name": "Rosé Wines", "hide": False },
    "D30007": { "name": "Private Label Wines", "hide": False },
    "D30008": { "name": "Specialty Red Wines", "hide": False },
    "D30011": { "name": "Rosé Wines", "hide": False },
    "D30303": { "name": "Tequila", "hide": False },
    "D30305": { "name": "Rum", "hide": False },
    "D30307": { "name": "Bourbon", "hide": False },
    "D30308": { "name": "Liqueurs and Specialty Spirits", "hide": False },
    "D30309": { "name": "Mezcal", "hide": False },
    "D30311": { "name": "Cocktails & Ready-to-Drink Beverages", "hide": False }
}

def build_query(page, query_type):
    # Create a filter based on the query type
    availability_filter = None
    if query_type == 'availability':
        availability_filter = ', availability: { match: "1" }'
    elif query_type == 'published':
        availability_filter = ', published: { eq: "1" }'

    # Base fields list
    fields = [
        "attribute_set_id",
        "availability",
        "category_code",
        "context_image",
        "country_of_origin",
        "created_at",
        "first_published_date",
        "gift_message_available",
        "id",
        "image_file",
        "is_imported",
        "item_characteristics",
        "item_story_qil",
        "item_title",
        "last_published_date",
        "marketing_category_code",
        "name",
        "new_product",
        "options_container",
        "primary_image",
        "product_label",
        "promotion",
        "published",
        "rating_summary",
        "retail_price",
        "review_count",
        "sales_size",
        "sales_uom_code",
        "sales_uom_description",
        "sku",
        "staged",
        "stock_status",
        "type_id",
        "uid",
        "updated_at",
        "url_key",
        "url_suffix",
        "use_and_demo",
        "is_returnable",
        "image { url label disabled }",
        "fun_tags",
        "url_rewrites { url parameters { name value } }",
        "thumbnail { disabled label url }",
        "primary_image_meta { metadata url }",
        "media_gallery { disabled label url }",
        "allergens { display_sequence ingredient }"
    ]

    fields_query = "\n".join(fields)

    query = f"""
    query Products {{
        products(
            sort: {{ name: ASC }}
            filter: {{ store_code: {{ eq: "{MY_STORE_NUMBER}" }}{availability_filter if availability_filter else ''} }}
            currentPage: {page}
            pageSize: 1000
        ) {{
            total_count
            page_info {{
                current_page
                page_size
                total_pages
            }}
            items {{
                {fields_query}
            }}
        }}
    }}
    """
    return query

def convert_title_to_url_slug(title):
    # Normalize the string to remove accents and other diacritics
    title_normalized = unicodedata.normalize('NFKD', title)
    title_normalized = title_normalized.encode('ascii', 'ignore').decode('ascii')

    # Convert to lowercase
    title_lower = title_normalized.lower()

    # Remove any special characters and replace spaces with hyphens
    title_slug = re.sub(r'[^a-z0-9]+', '-', title_lower).strip('-')

    # Return the slug (URL-friendly string)
    return title_slug

def fetch_page(page, query_type):
    query = build_query(page, query_type)
    response = requests.post('https://www.traderjoes.com/api/graphql', json={'query': query})
    if response.status_code == 200:
        improved_response = response.json()
        for product in improved_response['data']['products']['items']:
            product["url"] = f"https://www.traderjoes.com/home/products/pdp/{convert_title_to_url_slug(product['item_title'])}-{product['sku']}"

        return improved_response
    else:
        raise Exception(f"Query failed with status code {response.status_code}: {response.text}")

def fetch_all_data(query_type=None):
    all_items = []
    current_page = 1
    total_pages = None

    while total_pages is None or current_page <= total_pages:
        print(f"Fetching page {current_page}/{total_pages if total_pages else '?'} ({query_type})")
        data = fetch_page(current_page, query_type)
        products_data = data['data']['products']
        all_items.extend(products_data['items'])
        total_pages = products_data['page_info']['total_pages']
        current_page += 1

    data['data']['products']['items'] = all_items
    del data['data']['products']['page_info']
    return data

def deduplicate_items(available_data, published_data):
    # Use SKU as a unique identifier to deduplicate
    sku_to_item = {}

    # Add available items to the dictionary first
    for item in available_data['data']['products']['items']:
        sku_to_item[item['sku']] = item

    # Then add published items, overwriting if needed
    for item in published_data['data']['products']['items']:
        sku_to_item[item['sku']] = item

    # Combine into a single list
    deduplicated_items = list(sku_to_item.values())

    # Update the data structure
    deduplicated_data = available_data  # use the available_data as a base
    deduplicated_data['data']['products']['items'] = deduplicated_items

    return deduplicated_data['data']

def clean_string(s):
    # Check if s is a string
    if not isinstance(s, str):
        return s
    return re.sub(r'\s+', ' ', s.replace("\n", " ").replace("\r", " ").strip()).encode().decode('utf-8')

def cleanup_data(data):
    keys_to_keep = [
        "item_title",
        "item_story_qil",
        "retail_price",
        "category_code",
        "sku",
        "name",
        "product_label",
        "url",
        "published",
        "availability",
    ]

    # Create new list with filtered data
    filtered_items = [
        {key: clean_string(item[key]) for key in keys_to_keep if key in item}
        for item in data['products']['items']
    ]

    # Add category name to the filtered items
    for item in filtered_items:
        category_code = item.get("category_code", "")
        if category_code in CATEGORY_CODE_MAP:
            item["category"] = CATEGORY_CODE_MAP[category_code]['name']
        else:
            item["category"] = category_code

        if item.get("retail_price"):
            item["cost"] = f"${item.pop('retail_price')}"

        if item.get("name"):
            item["name"] = item["name"].title()

        if item.get("item_title"):
            title = item.pop("item_title").title()
            name = item.get("name", "")
            if name in title: # name is a substring or exact match of title, set name to the full title
                item["name"] = title
            elif not title in name: # title is not a substring of name, append title so both are kept
                item["title"] = title
            # else: title is a substring of name, keep name as is and there is no need to add title

        story = item.pop("item_story_qil")
        if story:
            item["description"] = story

        product_label = item.pop("product_label")
        if product_label:
            item["label"] = product_label

        if item.pop("published") == 0:
            item.pop("url")

        item['available'] = True if item.pop("availability") == 1 else False

    grouped_data = defaultdict(dict)
    item_count = 0
    for item in filtered_items:
        category = item.pop('category_code')
        sku = item.pop('sku')
        category_info = CATEGORY_CODE_MAP.get(category, {'name': category, 'hide': False})
        if not category_info['hide']:
            item_count += 1
            grouped_data[category_info['name']][sku] = item

    return (grouped_data, item_count)

def main():
    available_items_data = fetch_all_data(query_type='availability')
    published_items_data = fetch_all_data(query_type='published')
    merged_data = deduplicate_items(available_items_data, published_items_data)

    # Process and save the merged data
    with open('data.json', 'w') as f:
        json.dump(merged_data, f, indent=1, sort_keys=True)


    available_items_clean, product_count = cleanup_data(merged_data)
    with open('product_count.txt', 'w') as f:
        f.write(str(product_count))
    with open('clean_data.json', 'w') as f:
        json.dump(available_items_clean, f, indent=1, sort_keys=True, ensure_ascii=False)


    all_items = fetch_all_data()
    # Write all items (with and without availability) to a JSON file
    with open('all_data.json', 'w') as f:
        json.dump(all_items, f, indent=1, sort_keys=True)

if __name__ == '__main__':
    main()
