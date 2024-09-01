from collections import defaultdict
import re
import requests
import json

MY_STORE_NUMBER = 544

# This code is for items that the store buys for itself like printer paper
NON_CONSUMER_PRODUCT_CODE = "D40702"

# This map is made by an ai and may not be 100% accurate
CATEGORY_CODE_MAP = {
    "D40702": "Non-consumer/non-purchaseable items for the store",
    "D10501": "Household items",
    "D20801": "Fresh Fruits",
    "D11732": "Canned Fish/Seafood",
    "D20201": "Salads and Salad Kits",
    "D11323": "Ice Cream",
    "D11315": "Frozen Meals",
    "D10101": "Sweets and Candy",
    "D10103": "Specialty Chocolate",
    "D10104": "Mints and Breath Fresheners",
    "D10105": "Gummies and Jelly Candy",
    "D10201": "Coffee",
    "D10202": "Tea",
    "D10203": "Tea Mixes and Concentrates",
    "D10301": "Crackers and Crispbreads",
    "D10302": "Chips and Tortilla Chips",
    "D10303": "Snack Mixes",
    "D10304": "Pretzels and Snack Crackers",
    "D10305": "Snacks and Jerky",
    "D10306": "Popcorn and Puffed Snacks",
    "D10400": "Cookies",
    "D10401": "Biscotti and Shortbread",
    "D10403": "Wafer Cookies and Snaps",
    "D10404": "Gluten-Free and Allergen-Free Cookies",
    "D10405": "Cookie Assortments",
    "D10406": "Sandwich Cookies",
    "D10407": "Ice Cream Cones and Novelty Ice Cream",
    "D10500": "Candles and Household Fabrics",
    "D10601": "Dietary Supplements",
    "D10603": "Throat Sprays and Wellness Drops",
    "D10604": "Multi-Vitamin Supplements",
    "D10605": "Collagen and Fiber Supplements",
    "D10606": "Protein Powders",
    "D10607": "Miscellaneous Vitamins and Supplements",
    "D10700": "Skin Care and Face Care Products",
    "D10701": "Body Care and Bath Products",
    "D10801": "Juices and Lemonades",
    "D10803": "Lemonades",
    "D10804": "Ready to Drink Teas",
    "D10808": "Fruit Juices and Blends",
    "D10809": "Non-Dairy Beverages",
    "D10810": "Cold Brew and Ready to Drink Coffees",
    "D10811": "Sodas and Sparkling Beverages",
    "D10812": "Sparkling Water and Mineral Water",
    "D10901": "Sparkling and Mineral Waters",
    "D10902": "Mountain Spring Water",
    "D11001": "Flavored Seltzers and Sparklings with Fruit Juice",
    "D11103": "Non-Dairy Beverages - Specialty",
    "D11200": "Reusable Bags and Produce Bags",
    "D11204": "Reusable Shopping Bags",
    "D11312": "Frozen Appetizers & Snacks",
    "D11313": "Frozen Breakfast Foods & Pancakes",
    "D11314": "Frozen Desserts & Treats",
    "D11316": "Frozen Fruits & Smoothie Ingredients",
    "D11317": "Frozen Meats & Seafood",
    "D11318": "Frozen Meatless & Plant-Based Foods",
    "D11319": "Frozen Pizzas & Flatbreads",
    "D11320": "Frozen Rice & Grain Dishes",
    "D11321": "Frozen Fish & Seafood",
    "D11322": "Frozen Vegetables & Sides",
    "D11324": "Frozen Breads",
    "D11401": "Non-Alcoholic Beer and Beverages",
    "D11501": "Granolas and Clusters",
    "D11502": "Oats and Oatmeal",
    "D11503": "Cereals",
    "D11504": "Cereal Bars and Granola Bars",
    "D11505": "Toaster Pastries and Baking Seeds",
    "D11600": "Protein Bars and Energy Bars",
    "D11601": "Meal Replacement Bars",
    "D11715": "Canned Vegetables",
    "D11716": "Dry Grains and Rice",
    "D11717": "Pasta",
    "D11718": "Pasta Sauces",
    "D11719": "Cooking Oils",
    "D11720": "Canned and Jarred Vegetables",
    "D11721": "Canned and Jarred Fruits",
    "D11722": "Syrups",
    "D11723": "Honey",
    "D11725": "Nut Butters and Spreads",
    "D11726": "Vinegars",
    "D11727": "Baking Mixes and Supplies",
    "D11728": "Spices and Seasonings",
    "D11729": "Olives and Pickled Vegetables",
    "D11731": "Canned Chicken & Poultry",
    "D11733": "Cooking Sauces",
    "D11734": "Salad Dressings",
    "D11735": "Canned Mediterranean Foods",
    "D11736": "Condiments and Sauces",
    "D11737": "Broths and Soups",
    "D11738": "Chili and Stews",
    "D11739": "Instant Meals",
    "D11740": "Salsas",
    "D11800": "Raw Nuts",
    "D11801": "Roasted & Salted Nuts",
    "D11802": "Savory Nut Mixes",
    "D11803": "Trail Mixes & Trek Mixes",
    "D11804": "Candied & Sweet Nuts",
    "D11901": "Dried Fruits",
    "D11902": "Fruit & Nut Bites",
    "D11903": "Dried Apricots",
    "D11904": "Dried Cranberries & Cherries",
    "D11905": "Fruit Bars",
    "D11906": "Freeze-Dried Fruits",
    "D11907": "Dried Mango & Tropical Fruits",
    "D11908": "Coconut Products",
    "D11909": "Raisins",
    "D11910": "Exotic Dried Fruits",
    "D12001": "Dog Food",
    "D12002": "Cat Food",
    "D12003": "Dog Treats",
    "D12004": "Gourmet Dog Treats",
    "D12005": "Cat Treats",
    "D20101": "Bread & Tortillas",
    "D20103": "Flour Tortillas",
    "D20104": "Specialty Breads & Rolls",
    "D20105": "Bagels & Sandwich Breads",
    "D20106": "Bakery Treats",
    "D20200": "Sushi Rolls",
    "D20202": "Refrigerated Ready-to-Eat Meals",
    "D20204": "Refrigerated Dips & Spreads",
    "D20205": "Wraps & Sandwiches",
    "D20206": "Pizza Dough",
    "D20209": "Salsa & Pico de Gallo",
    "D20211": "Refrigerated Salads",
    "D20212": "Refrigerated Soups",
    "D20213": "Refrigerated Burritos",
    "D20301": "Chicken Eggs",
    "D20302": "Brown Eggs",
    "D20304": "Large & Extra-Large Eggs",
    "D20305": "Organic Eggs",
    "D20306": "Pasture-Raised Eggs",
    "D20402": "Block & Shredded Cheese",
    "D20403": "Cheese and Cheese Alternatives",
    "D20500": "Creamers",
    "D20501": "Dairy Cream",
    "D20502": "Yogurt & Cottage Cheese",
    "D20503": "Butter",
    "D20504": "Plain Yogurt",
    "D20505": "Non-Dairy Creamers",
    "D20506": "Milk & Dairy Alternatives",
    "D20507": "Flavored Yogurts",
    "D20508": "Buttery Spreads",
    "D20509": "Half & Half & Whipping Cream",
    "D20510": "Almond Drinks",
    "D20600": "Sausages & Cooked Meats",
    "D20601": "Fresh Chicken & Beef",
    "D20602": "Fresh Seafood",
    "D20603": "Beef Steaks & Cuts",
    "D20604": "Fresh Chicken",
    "D20605": "Fresh Lamb",
    "D20606": "Pork",
    "D20607": "Chicken Sausages",
    "D20608": "Turkey",
    "D20609": "Salmon & Seafood",
    "D20700": "Cold-Pressed Juices and Shots",
    "D20701": "Smoothies and Fruit Juices",
    "D20800": "Salad Greens & Lettuce",
    "D20802": "Fresh Vegetables",
    "D20803": "Fresh Herbs",
    "D20901": "Indoor Plants",
    "D20902": "Bouquets",
    "D20903": "Single Stem Florals",
    "D21001": "Refrigerated Meats",
    "D21002": "Refrigerated Pasta & Ravioli",
    "D21003": "Refrigerated Dips & Hummus",
    "D21004": "Smoked Salmon & Trout",
    "D21005": "Refrigerated Sauces & Pesto",
    "D21006": "Plant-Based Proteins & Tofu",
    "D21007": "Refrigerated Dairy Alternatives",
    "D21008": "Charcuterie Meats",
    "D30001": "Red and White Wines",
    "D30010": "Flavored Canned Wines",
    "D30012": "Sparkling Wines & Mimosas",
    "D30101": "Rosé Wines",
    "D30106": "Specialty Red Wines",
    "D30107": "Dessert Wines",
    "D30108": "International Red Wines",
    "D30109": "Rosé Magnums",
    "D30110": "Sparkling Wines & Champagnes",
    "D30200": "Hard Seltzers",
    "D30201": "Craft Beers & Pilsners",
    "D30202": "Imported Beers & Ciders",
    "D30203": "Non-Alcoholic Beers",
    "D30204": "Trader Joe's Private Label Beers",
    "D30205": "Non-Alcoholic Beverages & Hops",
    "D30301": "Vodka",
    "D40102": "Work Apparel",
    "D40202": "Store Stickers & Labels",
    "D40302": "Demo Supplies",
    "D40305": "Demo Cooking Equipment",
    "D40400": "Fearless Flyers & Promotions",
    "D40401": "Store Promotions & Samples",
    "D40500": "Bags & Packaging",
    "D40599": "Additional Bags & Packaging",
    "D40600": "Store Forms",
    "D40601": "Marketing & Information Brochures",
    "D40602": "Consumer Literature",
    "D40604": "Envelopes",
    "D40701": "Store Signage",
    "D40800": "Store Equipment & Maintenance",
    "D40801": "Restroom Supplies",
    "D40802": "Janitorial & Cleaning Supplies",
    "D40803": "Point of Sale and Receipt Supplies",
    "D40804": "Store Supplies - Miscellaneous",
    "D40900": "Gift Cards and Gift Card Holders",
    "D41100": "Display Baskets",
}

def build_query(page, with_availability=True):
    availability_filter = ', availability: { match: "1" }' if with_availability else ''

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

    # Remove certain fields if availability check is disabled
    if with_availability:
        fields.extend([
            "nutrition { calories_per_serving display_sequence panel_id panel_title serving_size servings_per_container details { amount display_seq nutritional_item percent_dv } }",
            "ingredients { display_sequence ingredient }",
            "item_story_marketing"
        ])

    fields_query = "\n".join(fields)

    query = f"""
    query Products {{
        products(
            sort: {{ name: ASC }}
            filter: {{ store_code: {{ eq: "{MY_STORE_NUMBER}" }}{availability_filter} }}
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

def fetch_page(page, with_availability=True):
    query = build_query(page, with_availability)
    response = requests.post('https://www.traderjoes.com/api/graphql', json={'query': query})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed with status code {response.status_code}: {response.text}")

def fetch_all_data(with_availability=True):
    all_items = []
    current_page = 1  # Start from page 1
    total_pages = 1  # Set a default value; will be updated with actual total_pages after the first request

    data = {}
    while current_page <= total_pages:
        print(f"Fetching page {current_page}/{total_pages}")
        # Fetch data for the current page
        data = fetch_page(current_page, with_availability)

        # Extract products data
        products_data = data['data']['products']

        # Add the items from the current page to the combined list
        all_items.extend(products_data['items'])

        # Update the total_pages value based on the returned data
        total_pages = products_data['page_info']['total_pages']

        # Move to the next page
        current_page += 1

    data['data']['products']['items'] = all_items
    del data['data']['products']['page_info']
    data = data['data']

    data['products']['items'].sort(key=lambda x: (x['item_title'], x['name'], x['id'], x['sku'], x['uid']))
    [panel['details'].sort(key=lambda detail: detail['nutritional_item']) for product in data['products']['items'] if isinstance(product.get('nutrition'), list) for panel in product['nutrition'] if isinstance(panel.get('details'), list)]

    return data

def clean_string(s):
    if s is None:
        return ''
    return re.sub(r'\s+', ' ', s.replace("\n", " ").replace("\r", " ").strip()).encode().decode('utf-8')

def cleanup_data(data):
    keys_to_keep = [
        "item_title",
        "item_story_qil",
        "retail_price",
        "category_code",
        "sku",
        "name"
    ]

    # Create new list with filtered data
    filtered_items = [
        {key: clean_string(item[key]) for key in keys_to_keep if key in item}
        for item in data['products']['items']
    ]

    # Add category name to the filtered items
    for item in filtered_items:
        category_code = item.pop("category_code", "")
        if category_code in CATEGORY_CODE_MAP:
            item["category"] = CATEGORY_CODE_MAP[category_code]
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

    # Create a defaultdict to group by `category_code`
    grouped_data = defaultdict(dict)

    # Iterate over each item in the list
    for item in filtered_items:
        category = item.get('category')
        sku = item.pop('sku')
        grouped_data[category][sku] = item

    return (grouped_data, data['products']['total_count'])

def main():
    # First fetch with availability
    available_items = fetch_all_data(with_availability=True)

    # Write the available items to a JSON file
    with open('data.json', 'w') as f:
        json.dump(available_items, f, indent=1, sort_keys=True)


    available_items_clean, product_count = cleanup_data(available_items)
    with open('product_count.txt', 'w') as f:
        f.write(str(product_count))
    with open('clean_data.json', 'w') as f:
        json.dump(available_items_clean, f, indent=1, sort_keys=True, ensure_ascii=False)

    # Second fetch without availability
    all_items = fetch_all_data(with_availability=False)

    # Write all items (with and without availability) to a JSON file
    with open('all_data.json', 'w') as f:
        json.dump(all_items, f, indent=1, sort_keys=True)

if __name__ == '__main__':
    main()
