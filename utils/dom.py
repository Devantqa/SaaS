from urllib.parse import urljoin
from selenium.webdriver.common.by import By

def get_visible_text(driver):
    # Extract visible text nodes (simple approach)
    # Skip scripts/styles; get body text and normalize whitespace
    text = driver.execute_script("""
        function visibleText(element) {
          const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT, {
            acceptNode: function(node) {
              if (!node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
              if (!node.parentElement) return NodeFilter.FILTER_REJECT;
              const style = window.getComputedStyle(node.parentElement);
              if (style && (style.visibility === 'hidden' || style.display === 'none')) return NodeFilter.FILTER_REJECT;
              return NodeFilter.FILTER_ACCEPT;
            }
          });
          let result = [];
          while (walker.nextNode()) { result.push(walker.currentNode.nodeValue); }
          return result.join(' ');
        }
        return visibleText(document.body);
    """)
    # Basic normalization
    return " ".join((text or "").split())

def collect_links(driver, include_same_origin_only=True):
    origin = driver.execute_script("return window.location.origin;")
    anchors = driver.find_elements(By.CSS_SELECTOR, "a[href]")
    hrefs = []
    for a in anchors:
        try:
            href = a.get_attribute("href")
            if not href:
                continue
            if include_same_origin_only and not href.startswith(origin):
                # Keep relative routes too
                if href.startswith("http"):
                    continue
            hrefs.append(urljoin(origin + "/", href))
        except Exception:
            continue
    # De-duplicate
    return sorted(set(hrefs))
