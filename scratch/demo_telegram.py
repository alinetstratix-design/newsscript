import os
import sys
import io
import json
import logging

# Force UTF-8 for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Fix module import paths
project_root = os.getcwd()
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, "newsbot"))

from newsbot.bot.rewrite import rewrite
from newsbot.bot.telegram import send_message

# Mock a news item
item = {
    "title": "देहरादून में बड़ा हादसा, मसूरी मार्ग पर अनियंत्रित होकर खाई में गिरी कार",
    "source": "Dehradun NIC Portal",
    "description": "देहरादून के मसूरी रोड पर आज सुबह एक दर्दनाक हादसा हुआ। एक स्विफ्ट कार अनियंत्रित होकर 500 फीट गहरी खाई में जा गिरी। कार में सवार 4 लोग गंभीर रूप से घायल हुए हैं, जिन्हें स्थानीय लोगों और पुलिस की मदद से अस्पताल पहुंचाया गया है।",
    "trending": True,
    "category": "Accident/Dehradun"
}

print("--- STARTING DEMO ---")
print(f"Source: {item['source']}")
print(f"Link: {item.get('link', 'N/A')}")
print(f"Original Title: {item['title']}")

try:
    print("\n[AI] Generating structured multi-platform content...")
    formatted_text = rewrite(item)
    
    print("\n--- GENERATED CONTENT ---")
    print(formatted_text)
    
    print("\n[Telegram] Sending to your channel...")
    send_message(formatted_text)
    print("SUCCESS: Demo message sent.")
    
except Exception as e:
    print(f"\nCRITICAL ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n--- END DEMO ---")
