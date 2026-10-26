# -*- coding: utf-8 -*-
import json, qrcode, shutil, urllib.parse, requests, cv2
d=json.load(open("_final_qr.json",encoding="utf-8"))
cash=d["cashdesk"]
short=""
for svc in ("https://is.gd/create.php?format=simple&url=","https://tinyurl.com/api-create.php?url="):
    try:
        r=requests.get(svc+urllib.parse.quote(cash,safe=""),timeout=20)
        if r.status_code==200 and r.text.strip().startswith("http"):
            short=r.text.strip(); print("short",short); break
    except Exception as e: print("err",str(e)[:50])
tgt=short or cash
out={}
for tag,bs in (("qr_pay_a",16),("qr_pay_b",12)):
    q=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=bs,border=4)
    q.add_data(tgt); q.make(fit=True); im=q.make_image(); im.save(tag+".png")
    img=cv2.imread(tag+".png"); txt,_,_=cv2.QRCodeDetector().detectAndDecode(img)
    out[tag]={"v":q.version,"px":(q.modules_count+8)*bs,"decoded":(txt==tgt),"len":len(txt)}
    print(tag,out[tag])
    shutil.copy(tag+".png", r"C:\Users\Administrator\AppData\Local\Temp\%s.png"%tag)
if short:
    rr=requests.get(short,allow_redirects=False,timeout=15,headers={"user-agent":"Mozilla/5.0 (Linux; Android 13) Chrome/120 Mobile"})
    print("short status",rr.status_code,"->",(rr.headers.get("Location") or "")[:70])
info=dict(d); info.update({"short_cash":short,"qr_pay":out})
json.dump(info,open("_pay_final2.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("DEADLINE",d["deadline"])
