from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse
import time

def get_distance(driver, from_address, to_address):
    base_url = "https://www.mapdevelopers.com/distance_from_to.php"
    params = {
        "from": from_address,
        "to": to_address
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    print(f"Requesting URL: {url}")
    
    driver.get(url)
    
    try:
        # Wait for the driving distance element to be present and visible
        while True:
            driving_status_element = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.ID, "driving_status"))
            )
            distance_text = driving_status_element.text
            km_distance = distance_text.split(",")[1].strip().split()[0]

            # Check if the distance is not zero before breaking out of the loop
            if float(km_distance) > 0:
                return float(km_distance)
            else:
                print("Driving distance is 0 km, waiting for it to update...")
                time.sleep(5)  # Wait a bit before checking again

    except Exception as e:
        print(f"Could not find driving status on page: {url}, error: {e}")
        return None

# Specify the path to your ChromeDriver
chromedriver_path = ""

# Set up the Chrome WebDriver service
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service)

try:
    # List of unique addresses
    addresses = list(set([
        'Minde allé 35',              # Godt Brød Minemyren
        'Vestre Torggaten 2',         # Godt Brød Vestre Torggaten
        'Vetrlidsallmenningen 19',    # Godt Brød Fløyen
        'Marken 1 5017',                   # Godt Brød Marken
        'Nedre Korskirkeallmenningen 12',  # Godt Brød Korskirken
        'Christies gate 10 5016',          # Godt Brød Festplassen
        'Inndalsveien 6',             # Godt Brød Kronstad X og Blomsterverksted
        'Muséplassen 3',              # Godt Brød Christie
        'Damsgårdsveien 59',          # Godt Brød Fløttmannsplassen
        'Myrdalsvegen 2'              # Godt Brød Horisont
    ]))
    
    # Initialize the distance matrix
    distance_matrix = [[0 for _ in range(len(addresses))] for _ in range(len(addresses))]
    
    # Calculate distances between all combinations of addresses
    for i in range(len(addresses)):
        for j in range(i + 1, len(addresses)):
            from_address = addresses[i]
            to_address = addresses[j]
            distance = get_distance(driver, from_address, to_address)
            if distance is not None:
                print(f"Avstand fra {from_address} til {to_address}: {distance} km")
                # Update the distance matrix symmetrically
                distance_matrix[i][j] = distance
                distance_matrix[j][i] = distance
            else:
                print(f"Kunne ikke beregne avstanden mellom {from_address} og {to_address}")
            time.sleep(5)  # Add a delay between requests
    
    # Print the distance matrix
    print("\nAvstandsmatrise:")
    for row in distance_matrix:
        print(row)

finally:
    time.sleep(10)  # Wait before closing the browser
    driver.quit()
