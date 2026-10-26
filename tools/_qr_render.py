# -*- coding: utf-8 -*-
import json, qrcode, shutil, os
sch=open("_scheme_app.txt",encoding="utf-8").read().strip()
info=json.load(open("_qr_app_info.json",encoding="utf-8"))
out={}
for bs in (6,8,10,12):
    q=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L,box_size=bs,border=4)
    q.add_data(sch); q.make(fit=True)
    img=q.make_image()
    p="qr_app_%d.png"%bs
    img.save(p)
    out[bs]=(q.version, os.path.getsize(p))
print(json.dumps({str(k):v for k,v in out.items()}))
# 100% 显示页（像素化放大，避免缩放糊掉）
html = """<!doctype html><html><head><meta charset=utf-8><title>Alipay QR</title>
<style>body{margin:0;background:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;font-family:Segoe UI,Microsoft YaHei}
img{image-rendering:pixelated;width:900px;height:900px}
p{font-size:20px;color:#333}</style></head><body>
<img src="qr_app_12.png"><p>%s &nbsp;|&nbsp; 订单 %s &nbsp;|&nbsp; 失效 %s</p></body></html>""" % ("alipays:// 原生支付码", info["order_id"], info["deadline"])
open("alipay_qr.html","w",encoding="utf-8").write(html)
shutil.copy("qr_app_10.png", r"C:\Users\Administrator\AppData\Local\Temp\alipay_app_qr.png")
shutil.copy("alipay_qr.html", r"C:\Users\Administrator\AppData\Local\Temp\alipay_qr.html")
print("ok", info)
