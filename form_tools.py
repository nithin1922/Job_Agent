from playwright.sync_api import sync_playwright, Page
import json

from mcp_server import MCPServer

mcp_server = MCPServer(kb_path='user_data.json')

def get_knowledge_base_schema() -> dict:
    """Returns the entire structure of the user's knowledge base."""
    print("\n[Tool] Getting knowledge base schema...")
    return mcp_server.kb.get_all_data()

def scrape_form_fields(url: str) -> list:
    """
    Scrapes a website to find all form field labels, types, and options
    using Playwright locators for improved reliability.
    """
    print(f"\n[Browser Tool] Scraping {url}...")
    form_elements = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded")
            
            form_groups = page.locator('.form-group').all()
            
            for group in form_groups:
                main_label = group.locator('label', has_not=group.locator('input')).first
                if not main_label.is_visible():
                    continue
                
                # Corrected: Call text_content() without args, then call .strip()
                label_text = main_label.text_content().strip()
                
                text_input = group.locator('input[type="text"], input[type="email"], input[type="tel"], input[type="url"]').first
                select_input = group.locator('select').first
                radio_inputs = group.locator('input[type="radio"]').all()

                if text_input.is_visible():
                    form_elements.append({
                        'label': label_text,
                        'type': text_input.get_attribute('type') or 'text',
                        'name': text_input.get_attribute('name')
                    })
                elif select_input.is_visible():
                    # Corrected: Call text_content() without args, then call .strip()
                    options = [opt.text_content().strip() for opt in select_input.locator('option').all()]
                    form_elements.append({
                        'label': label_text,
                        'type': 'select',
                        'name': select_input.get_attribute('name'),
                        'options': options
                    })
                elif len(radio_inputs) > 0:
                    radio_name = radio_inputs[0].get_attribute('name')
                    options = []
                    for radio in radio_inputs:
                        radio_id = radio.get_attribute('id')
                        option_label = group.locator(f'label[for="{radio_id}"]').first
                        if option_label.is_visible():
                            # Corrected: Call text_content() without args, then call .strip()
                            options.append(option_label.text_content().strip())
                    
                    form_elements.append({
                        'label': label_text,
                        'type': 'radio',
                        'name': radio_name,
                        'options': options
                    })

        except Exception as e:
            print(f"An error occurred during scraping: {e}")
        finally:
            browser.close()

    print(f"[Browser Tool] Found fields: {json.dumps(form_elements, indent=2)}")
    return form_elements


def query_knowledge_base(query: str) -> str:
    """Retrieves a specific piece of information from the knowledge base."""
    print(f"\n[MCP Tool] Running query: '{query}'")
    result = mcp_server.fetch_info(query)
    if result is None:
        return "No information found for that query."
    if isinstance(result, (dict, list)):
        return json.dumps(result)
    return str(result)
