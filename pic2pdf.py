"""
将一个文件夹得图片集中到一个pdf文档中
pic_path  图片文件夹地址
pdf_path  PDF文件夹地址
name      pdf文件名称
"""
import os
import fitz


def process_pic2pdf(pic_path, pdf_path, name):
    print(pic_path, pdf_path, name)
    doc = fitz.open()
    for img_name in os.listdir(pic_path):
        img = pic_path + '/' + img_name
        imgdoc = fitz.open(img)  # 打开图片
        pdfbytes = imgdoc.convertToPDF()  # 使用图片创建单页的 PDF
        imgpdf = fitz.open("pdf", pdfbytes)
        doc.insertPDF(imgpdf)  # 将当前页插入文档
    new_pdf_path = pdf_path + '/' + name + ".pdf"
    if not os.path.exists(pdf_path):
        os.makedirs(pdf_path)
    if os.path.exists(new_pdf_path):
        os.remove(new_pdf_path)
    doc.save(new_pdf_path)  # 保存pdf文件
    doc.close()
    return name
