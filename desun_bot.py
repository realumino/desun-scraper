import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import random
import string

def generate_random_string(min_length=5, max_length=10):
    length = random.randint(min_length, max_length)
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

# Configuration
def get_user_input(prompt, default):
    value = input(f"{prompt} [{default}]: ").strip()
    return value if value else default

BASE_URL = get_user_input("Enter Base URL", "http://219.230.50.43/doc/")
USERNAME = get_user_input("Enter Username", "1989")
PASSWORD = get_user_input("Enter Password", "0604")

def main():
    # Initialize WebDriver
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Uncomment to run headless
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        print("Step 1: Logging in...")
        driver.get(BASE_URL)
        
        # Wait for login fields
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Signin1_username")))
        
        try:
            username_input = driver.find_element(By.ID, "Signin1_username")
            password_input = driver.find_element(By.ID, "Signin1_password")
            login_btn = driver.find_element(By.ID, "Signin1_ButtonLogin")

            username_input.clear()
            username_input.send_keys(USERNAME)
            password_input.clear()
            password_input.send_keys(PASSWORD)
            login_btn.click()
        except Exception as e:
            print(f"Error during login interaction: {e}")
            return

        # Wait for login to complete
        time.sleep(3)

        print("Step 2: Navigating to 'My Exercises'...")
        # Direct navigation to the exercises page
        # Based on exploration, the link is likely /doc/Main.aspx?tabindex=1&tabid=6
        driver.get(BASE_URL + "Main.aspx?tabindex=1&tabid=6")
        
        # Wait for exercises list
        time.sleep(3)
        
        # Wait for exercises list
        time.sleep(3)
        
        print("Step 3: Collecting all exercise links...")
        exercise_links = []
        try:
            # Find all "Answer" links
            # Selector: a[id$='_HyperLinkShow']
            elements = driver.find_elements(By.CSS_SELECTOR, "a[id$='_HyperLinkShow']")
            for el in elements:
                href = el.get_attribute("href")
                if href:
                    exercise_links.append(href)
            print(f"Found {len(exercise_links)} exercises.")
        except Exception as e:
            print(f"Error collecting links: {e}")
            return

        # Process each exercise
        for i, link in enumerate(exercise_links):
            print(f"\nProcessing exercise {i+1}/{len(exercise_links)}: {link}")
            try:
                # Open in a new tab to keep the main list (though we have the links now)
                # and to satisfy the requirement "close the corresponding page"
                driver.execute_script("window.open(arguments[0], '_blank');", link)
                driver.switch_to.window(driver.window_handles[-1])
                
                # Wait for page load
                time.sleep(3)
                
                process_single_exercise(driver)
                
                # Close the tab
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                print(f"Finished exercise {i+1}.")
                
            except Exception as e:
                print(f"Error processing exercise {i+1}: {e}")
                # Ensure we close the tab if it's still open and not the main one
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

    except Exception as e:
        print(f"An error occurred: {e}")
        driver.save_screenshot("error_screenshot.png")
    
    finally:
        driver.quit()
        if os.path.exists("Reference_Answer.doc"):
            try:
                os.remove("Reference_Answer.doc")
            except:
                pass

def process_single_exercise(driver):
    # Check for existing answers
    try:
        # If there are "删除" (Delete) links, it means an answer has been submitted
        existing_answers = driver.find_elements(By.PARTIAL_LINK_TEXT, "删除")
        if len(existing_answers) > 0:
            print("  Answer already submitted. Skipping.")
            return
    except:
        pass

    print("  Extracting Reference Answer...")
    try:
        # Find the answer link
        try:
            answer_link = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@id, 'HyperLinkA1002')]"))
            )
            answer_url = answer_link.get_attribute("href")
        except:
            # Fallback by text
            links = driver.find_elements(By.TAG_NAME, "a")
            answer_url = None
            for link in links:
                href = link.get_attribute("href")
                if href and "introduce.mht" in href:
                    answer_url = href
                    break
            if not answer_url:
                print("  Answer link not found. Skipping.")
                return

        # Download the answer
        cookies = {c['name']: c['value'] for c in driver.get_cookies()}
        response = requests.get(answer_url, cookies=cookies)
        
        if response.status_code != 200:
            print("  Failed to download answer.")
            return

        # Save as .doc with random name
        random_name = generate_random_string()
        file_name = f"{random_name}.doc"
        file_path = os.path.abspath(file_name)
        with open(file_path, "wb") as f:
            f.write(response.content)
        
        # Submit Answer
        print("  Submitting Answer...")
        # Click "Add New" (新增)
        try:
            add_new_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "ButtonAddNew"))
            )
            add_new_btn.click()
        except:
            try:
                add_new_btn = driver.find_element(By.XPATH, "//input[@value='新增']")
                add_new_btn.click()
            except:
                print("  'Add New' button not found.")
                return
        
        time.sleep(1)
        
        # Fill the form
        try:
            title_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//input[contains(@id, 'TextBoxA1306')]"))
            )
            title_input.clear()
            random_title = generate_random_string()
            title_input.send_keys(random_title)
            
            file_input = driver.find_element(By.XPATH, "//input[contains(@id, 'FileA1304')]")
            file_input.send_keys(file_path)
            
            # Save
            save_btn = driver.find_element(By.XPATH, "//a[contains(@id, 'LinkButtonUpdate')]")
            save_btn.click()
            print("  Clicked Save.")
            
            # Wait for save to complete
            time.sleep(2)
            
            # Clean up
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"  Removed temporary file: {file_path}")
            
        except Exception as e:
            print(f"  Error filling form: {e}")

    except Exception as e:
        print(f"  Error in single exercise: {e}")


if __name__ == "__main__":
    main()
