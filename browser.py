import pyautogui
import pychrome
import time
from bs4 import BeautifulSoup, SoupStrainer

from cerbos.sdk.model import *
from cerbos.sdk.client import CerbosClient

desired_score = 50

# Connect to the running Chrome instance
browser = pychrome.Browser(url="http://127.0.0.1:9222")
tabs = browser.list_tab()
if not tabs:
    print("No open tabs found. Ensure Chrome is running with remote debugging enabled.")
    exit(1)

# Choose the first tab (adjust if needed)
tab = tabs[0]

tab.start()
tab.DOM.enable()
tab.Runtime.enable()

def get_css_property(bs_element, property_name):
    style_attr = bs_element.get("style", "")
    style_dict = {}
    for item in style_attr.split(';'):
        item = item.strip()
        if not item:
            continue
        if ':' not in item:
            continue
        key, value = item.split(':', 1)
        style_dict[key.strip()] = value.strip()
    return style_dict.get(property_name)

debug = False
slight_debug = True

def check_logic(request_shapes, policy_shapes):
    with CerbosClient("https://demo-pdp.cerbos.cloud", playground_instance="ZCWZxXJ267add709HHImPa7GE9s6G5p8", debug=True, tls_verify=False) as cerbos:
        request = Principal(
            "request",
            roles={"USER"},
            policy_version="default",
            attr={"badges": request_shapes},
        )
        policy = Resource(
            "policy",
            "shape",
            policy_version="default",
            attr={"badges": policy_shapes},
        )
        
        return cerbos.is_allowed("view", request, policy, None)


def determine_items(item):
    is_circle = 'rounded-full' in item.get('class', [])
    shape = 'circle' if is_circle else 'square'

    color = get_css_property(item, "background-color")

    child_triangle = item.find("div", class_="w-0")
    if child_triangle:
        shape = 'triangle'
        color = get_css_property(child_triangle, "border-bottom")
        color = color.split(" ")[-1]

    return {"color": color, "shape": shape}

score = None
hash_val = None

times = []

start_time = None

def start_timer():
    global start_time
    start_time = time.time()

def end_timer():
    global start_time
    if not start_time:
        print("ending but not started!")
        return
    now = time.time()
    times.append(now - start_time)
    last_5_times = times[-5:]
    if len(last_5_times) > 0:
        avg_time = sum(last_5_times) / len(last_5_times)
        print(f"Average execution time of last {len(last_5_times)}: {avg_time}s")
    start_time = now

try:
    while True:
        result = tab.Runtime.evaluate(expression="document.documentElement.outerHTML")
        dom_html = result.get("result", {}).get("value", "")

        strainer = SoupStrainer("div")
        soup = BeautifulSoup(dom_html, "lxml")

        twoxl = soup.find_all("div", class_="text-2xl")
        for x in twoxl:
            if 'Score' in x.get_text():
                _, _, number_str = x.get_text().partition(":")
                score = int(number_str.strip())

        # Find the first <div> with class "bg-white"
        request = soup.find("div", class_="bg-white")
        policy = soup.find("div", class_="bg-gray-200")
        if request is None or policy is None:
            print("not in game")
            continue

        new_hash = hash((request, policy))

        if new_hash == hash_val:
            print("No change")
            continue
        else:
            end_timer()
        hash_val = new_hash
        start_timer()

        policy_i = policy.find_all("div", class_="w-8")
        request_i = request.find_all("div", class_="w-8")

        request_items = [determine_items(item) for item in request_i]
        policy_items = [determine_items(item) for item in policy_i]
        
        answer = check_logic(request_items, policy_items)
        print("score", score)

        if score == desired_score:
            answer = not answer # intentionally lose

        if answer:
            pyautogui.press('right')
            if debug:
                print("Pressed Right")
        else:
            pyautogui.press('left')
            if debug:
                print("Pressed left")

except KeyboardInterrupt:
    print("Exiting...")
finally:
    tab.stop()