import json

def is_empty_value(value):
    """Check if the value is considered empty."""
    return value is None or value == "" or value == [] or value == {}

def count_empty_keys(items):
    """Count the percentage of empty values for each key."""
    empty_keys_count = {}
    total_items = len(items)

    # Iterate over each item in the items array
    for item in items:
        for key, value in item.items():
            # Check if the value for the key is empty
            if is_empty_value(value):
                if key in empty_keys_count:
                    empty_keys_count[key] += 1
                else:
                    empty_keys_count[key] = 1

    # Calculate the percentage of empty values for each key
    empty_key_percentages = {
        key: (count / total_items) * 100
        for key, count in empty_keys_count.items()
    }

    return empty_key_percentages

def main():
    # Load the JSON data from the file
    with open('all_data.json', 'r') as file:
        data = json.load(file)

    # Extract the items array
    items = data.get("products", {}).get("items", [])

    if not items:
        print("No items found in the JSON data.")
        return

    # Count the percentage of empty values for each key
    empty_key_percentages = count_empty_keys(items)

    if empty_key_percentages:
        print("Keys with their percentage of empty values:")
        # Sort keys by descending percentage of empty values
        for key, percentage in sorted(empty_key_percentages.items(), key=lambda x: x[1], reverse=True):
            print(f"{key}: {percentage:.2f}%")
    else:
        print("No empty values were found for any key.")

if __name__ == "__main__":
    main()
