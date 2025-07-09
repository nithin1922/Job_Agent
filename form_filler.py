import time
from playwright.sync_api import sync_playwright, Page, expect

def fill_form_field(page: Page, field_info: dict, value: str):
    """
    Finds a form field based on its info dictionary and fills it with the provided value.
    """
    label_text = field_info['label']
    field_type = field_info['type']
    field_name = field_info.get('name')

    try:
        print(f"[Form Filler] Attempting to fill '{label_text}' ({field_type}) with '{value}'...")

        if field_type in ['text', 'email', 'tel', 'url']:
            # Find by label's 'for' attribute matching input's 'id'
            label = page.locator(f"label:has-text('{label_text}')").first
            input_id = label.get_attribute('for')
            if input_id:
                page.locator(f"#{input_id}").fill(value)
                print(f"  - Success: Filled text input.")
            else:
                print(f"  - Warning: Could not find 'for' attribute on label '{label_text}'.")

        elif field_type == 'select':
            label = page.locator(f"label:has-text('{label_text}')").first
            input_id = label.get_attribute('for')
            if input_id:
                page.locator(f"#{input_id}").select_option(label=value)
                print(f"  - Success: Selected option '{value}'.")
            else:
                print(f"  - Warning: Could not find 'for' attribute on label '{label_text}'.")

        elif field_type == 'radio':
            # For radio buttons, we find the group by name and select the option by its label text or value
            # Find the specific radio button label that matches the value
            option_to_select = page.locator(f"input[name='{field_name}'] + label:has-text('{value}')").first
            option_to_select.click()
            print(f"  - Success: Clicked radio button '{value}'.")
            
    except Exception as e:
        print(f"  - Error filling field for label '{label_text}': {e}")


def automate_form_filling(url: str, form_data: dict, all_fields_info: list):
    """
    Launches a browser and fills out the form.
    """
    # Create a mapping from label text to the full field info dictionary
    field_info_map = {field['label']: field for field in all_fields_info}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        try:
            print("\n--- Starting Form Filling Automation ---")
            page.goto(url)
            expect(page.locator("h1")).to_be_visible()
            
            for label, answer in form_data.items():
                if label in field_info_map:
                    field_info = field_info_map[label]
                    fill_form_field(page, field_info, str(answer))
                else:
                    print(f"  - Warning: No field info found for label '{label}', skipping.")

            print("\nForm filling complete. The browser will close in 10 seconds.")
            time.sleep(10)
        except Exception as e:
            print(f"An error occurred during browser automation: {e}")
        finally:
            browser.close()
