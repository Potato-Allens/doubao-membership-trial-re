import time
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome",headless=True)
    pg=b.new_page(viewport={"width":1280,"height":1024})
    pg.goto("file:///C:/Users/Administrator/AppData/Local/Temp/alipay_qr2.html")
    time.sleep(1)
    sz=pg.evaluate("[...document.querySelectorAll('img')].map(i=>[i.src.split('/').pop(),i.naturalWidth,i.clientWidth,i.clientHeight])")
    print(sz)
    pg.screenshot(path="C:/Users/Administrator/AppData/Local/Temp/alipay_page_shot.png", full_page=False)
    b.close()
print("ok")
