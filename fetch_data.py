import requests
import json

MY_STORE_NUMBER = 544

def build_query(page, with_availability=True):
    availability_filter = ', availability: { match: "1" }' if with_availability else ''

    # Base fields list
    fields = [
        "attribute_set_id",
        "availability",
        "canonical_url",
        "category_code",
        "color",
        "context_image",
        "country_of_manufacture",
        "country_of_origin",
        "created_at",
        "first_published_date",
        "gift_message_available",
        "id",
        "image_file",
        "is_imported",
        "item_characteristics",
        "item_description",
        "item_story_qil",
        "item_title",
        "last_published_date",
        "manufacturer",
        "marketing_category_code",
        "meta_description",
        "meta_keyword",
        "meta_title",
        "name",
        "new_from_date",
        "new_product",
        "new_to_date",
        "only_x_left_in_stock",
        "options_container",
        "other_images",
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
        "special_from_date",
        "special_price",
        "special_to_date",
        "staged",
        "stock_status",
        "swatch_image",
        "tier_price",
        "type_id",
        "uid",
        "updated_at",
        "url_key",
        "url_path",
        "url_suffix",
        "use_and_demo",
        "is_returnable",
        "price { maximalPrice { amount { currency value } } minimalPrice { amount { currency value } } regularPrice { amount { currency value } } }",
        "tier_prices { customer_group_id percentage_value qty value website_id }",
        "image { url label disabled }",
        "fun_tags",
        "url_rewrites { url parameters { name value } }",
        "thumbnail { disabled label url }",
        "product_links { link_type linked_product_sku linked_product_type sku }",
        "primary_image_meta { metadata url }",
        "other_images_meta { metadata url }",
        "media_gallery { disabled label url }",
        "media_gallery_entries { disabled file id label media_type types uid }",
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

    data['products']['items'].sort(key=lambda x: (x['name'], x['id'], x['sku'], x['uid']))
    [panel['details'].sort(key=lambda detail: detail['nutritional_item']) for product in data['products']['items'] if isinstance(product.get('nutrition'), list) for panel in product['nutrition'] if isinstance(panel.get('details'), list)]

    return data

def main():
    # First fetch with availability
    available_items = fetch_all_data(with_availability=True)

    # Write the available items to a JSON file
    with open('data.json', 'w') as f:
        json.dump(available_items, f, indent=2, sort_keys=True)

    # Second fetch without availability
    all_items = fetch_all_data(with_availability=False)

    # Write all items (with and without availability) to a JSON file
    with open('all_data.json', 'w') as f:
        json.dump(all_items, f, indent=2, sort_keys=True)

if __name__ == '__main__':
    main()
