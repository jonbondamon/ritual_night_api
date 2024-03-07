import pandas as pd

# Load the items list and sets to store mapping
items_df = pd.read_excel('items_list_adjusted.xlsx')
sets_to_store_df = pd.read_excel('sets_to_store.xlsx')

# Merge to include 'Location' in the items dataframe
merged_df = pd.merge(items_df, sets_to_store_df[['Name', 'Location']], left_on='item_set', right_on='Name', how='left')
merged_df['is_general_store_item'] = merged_df['Location'] == 'General Store'

# Extract unique item types and rarities
unique_item_types = merged_df['item_type'].unique()
unique_rarities = merged_df['rarity'].unique()

# Generate INSERT statements
item_type_inserts = [f"INSERT INTO item_types (item_type_name) VALUES ('{item_type}');" for item_type in unique_item_types]
rarity_type_inserts = [f"INSERT INTO rarity_types (rarity_name) VALUES ('{rarity}');" for rarity in unique_rarities]

# Assuming mappings for item types and rarities
item_type_id_map = {item_type: index + 1 for index, item_type in enumerate(unique_item_types)}
rarity_id_map = {rarity: index + 1 for index, rarity in enumerate(unique_rarities)}

# Generate INSERT statements for items, including is_general_store_item
item_inserts = [
    f"INSERT INTO items (item_name, unity_name, item_type_id, silver_cost, gold_cost, rarity_id, is_general_store_item) VALUES "
    f"('{row['item_name']}', '{row['unity_name']}', {item_type_id_map[row['item_type']]}, "
    f"{row['silver_cost']}, {row['gold_cost']}, {rarity_id_map[row['rarity']]}, {row['is_general_store_item']});"
    for _, row in merged_df.iterrows()
]

# Print or save the INSERT statements
print("Item Types Inserts:")
for statement in item_type_inserts:
    print(statement)

print("\nRarity Types Inserts:")
for statement in rarity_type_inserts:
    print(statement)

print("\nItems Inserts:")
for statement in item_inserts:
    print(statement)
