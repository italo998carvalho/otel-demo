import requests
import random
import time
import json
from datetime import datetime

# --- CONFIGURATION ---
# Change this to your API's base URL
BASE_URL = "http://localhost:8000" 

def log(message):
    """Simple function to display logs with a timestamp."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def generate_random_item_payload():
    """Generates a dictionary with random item data."""
    item_names = ["T-Shirt", "Jeans", "Running Shoes", "Leather Jacket", "Cap", "Socks"]
    return {
        "item_id": random.randint(1000, 999999),
        "name": f"{random.choice(item_names)} Model-{random.randint(1, 100)}",
        "price": round(random.uniform(20.0, 350.0), 2),
        "is_offer": random.choice([True, False])
    }

# --- TRAFFIC FLOW DEFINITIONS ---

def flow_complete_cycle():
    """Simulates the full lifecycle of an item: CREATE -> READ -> UPDATE -> DELETE."""
    log("--- Starting COMPLETE FLOW (C -> R -> U -> D) ---")
    created_item_id = None
    try:
        # 1. CREATE
        new_item = generate_random_item_payload()
        created_item_id = new_item["item_id"]
        log(f"[*] CREATING item ID: {created_item_id}...")
        response = requests.post(f"{BASE_URL}/items", json=new_item, timeout=5)
        response.raise_for_status()
        log(f"[+] SUCCESS creating item {created_item_id}.")
        time.sleep(random.uniform(0.5, 1.0))

        # 2. READ
        log(f"[*] READING item ID: {created_item_id}...")
        response = requests.get(f"{BASE_URL}/items/{created_item_id}", timeout=5)
        response.raise_for_status()
        log(f"[+] SUCCESS reading item {created_item_id}.")
        time.sleep(random.uniform(0.5, 1.0))

        # 3. UPDATE
        update_payload = response.json()
        update_payload['price'] = round(update_payload['price'] * 1.2, 2) # Increase price by 20%
        log(f"[*] UPDATING item ID: {created_item_id}...")
        response = requests.put(f"{BASE_URL}/items/{created_item_id}", json=update_payload, timeout=5)
        response.raise_for_status()
        log(f"[+] SUCCESS updating item {created_item_id}.")
        
    except requests.exceptions.RequestException as e:
        log(f"[!] ERROR in complete flow: {e}")
    finally:
        # 4. DELETE (even if an error occurred midway)
        if created_item_id:
            time.sleep(random.uniform(0.5, 1.0))
            try:
                log(f"[*] DELETING item ID: {created_item_id}...")
                response = requests.delete(f"{BASE_URL}/items/{created_item_id}", timeout=5)
                response.raise_for_status()
                log(f"[+] SUCCESS deleting item {created_item_id}.")
            except requests.exceptions.RequestException as e:
                log(f"[!] ERROR while trying to delete item {created_item_id}: {e}")
    log("--- End of COMPLETE FLOW ---")


def flow_heavy_listing():
    """Simulates a user who only lists items multiple times."""
    log("--- Starting HEAVY LISTING FLOW ---")
    try:
        num_requests = random.randint(3, 8)
        log(f"[*] Making {num_requests} list requests...")
        for i in range(num_requests):
            response = requests.get(f"{BASE_URL}/items", timeout=5)
            response.raise_for_status()
            log(f"    -> List request {i+1}/{num_requests} complete, {len(response.json())} items found.")
            time.sleep(random.uniform(0.3, 1.0))
        log("[+] SUCCESS in heavy listing flow.")
    except requests.exceptions.RequestException as e:
        log(f"[!] ERROR in heavy listing flow: {e}")
    log("--- End of HEAVY LISTING FLOW ---")


def flow_navigation():
    """Simulates a user who lists items and then views the details of a few."""
    log("--- Starting NAVIGATION FLOW ---")
    try:
        log("[*] Listing all items to start navigation...")
        response = requests.get(f"{BASE_URL}/items", timeout=5)
        response.raise_for_status()
        all_items = response.json()

        if not all_items:
            log("[i] No items found to navigate. Ending flow.")
            return

        # Choose up to 3 random items from the list to view
        sample_size = min(len(all_items), 3)
        items_to_view = random.sample(all_items, k=sample_size)
        
        log(f"[*] Viewing details for {len(items_to_view)} items...")
        for item in items_to_view:
            item_id = item.get("item_id")
            if item_id:
                log(f"    -> Fetching details for item {item_id}...")
                requests.get(f"{BASE_URL}/items/{item_id}", timeout=5).raise_for_status()
                time.sleep(random.uniform(0.4, 1.2))
        log("[+] SUCCESS in navigation flow.")

    except requests.exceptions.RequestException as e:
        log(f"[!] ERROR in navigation flow: {e}")
    log("--- End of NAVIGATION FLOW ---")


def flow_create_and_delete():
    """Simulates the immediate creation and deletion of an item."""
    log("--- Starting CREATE-AND-DELETE FLOW ---")
    created_item_id = None
    try:
        # 1. CREATE
        new_item = generate_random_item_payload()
        created_item_id = new_item["item_id"]
        log(f"[*] CREATING (temporarily) item ID: {created_item_id}...")
        response = requests.post(f"{BASE_URL}/items", json=new_item, timeout=5)
        response.raise_for_status()
        log(f"[+] SUCCESS creating item {created_item_id}.")
        
        time.sleep(random.uniform(0.8, 2.0)) # Wait a bit before deleting

        # 2. DELETE
        log(f"[*] DELETING (immediately) item ID: {created_item_id}...")
        response = requests.delete(f"{BASE_URL}/items/{created_item_id}", timeout=5)
        response.raise_for_status()
        log(f"[+] SUCCESS deleting item {created_item_id}.")
        
    except requests.exceptions.RequestException as e:
        log(f"[!] ERROR in create-and-delete flow: {e}")
    log("--- End of CREATE-AND-DELETE FLOW ---")


# --- MAIN EXECUTOR ---

def main():
    """
    Randomly chooses and runs one of the available flows in an infinite loop.
    """
    #
    # To adjust the probability of each flow, add or remove
    # functions from this list. More entries = higher probability.
    #
    available_flows = [
        flow_complete_cycle,    # 1x chance
        flow_heavy_listing,     # 3x chance
        flow_heavy_listing,
        flow_heavy_listing,
        flow_navigation,        # 2x chance
        flow_navigation,
        flow_create_and_delete  # 1x chance
    ]
    
    log("Starting traffic generator with varied flows. Press CTRL+C to stop.")
    
    while True:
        try:
            # Choose a random flow from the available list
            selected_flow = random.choice(available_flows)
            
            # Execute the chosen flow
            selected_flow()

            # Wait for a while before starting the next cycle
            wait_time = random.uniform(1.5, 4.0)
            print("-" * 60)
            log(f"Waiting {wait_time:.2f} seconds for the next flow...")
            print("-" * 60)
            time.sleep(wait_time)

        except KeyboardInterrupt:
            print("\n\nScript interrupted by user. Shutting down.")
            break
        except Exception as e:
            log(f"[!!!] UNEXPECTED ERROR in main loop: {e}")
            time.sleep(5) # Wait a bit longer in case of a major error

if __name__ == "__main__":
    main()