from pypdf import PdfWriter, PdfReader
import os
import sys

def merge_folder(folder, output):
    merger = PdfWriter()
    bookmarks = []
    page_offset = 0

    pdf_files = sorted(
        [f for f in os.listdir(folder) if f.endswith(".pdf")]
    )

    for filename in pdf_files:
        path = os.path.join(folder, filename)
        reader = PdfReader(path)
        pages = len(reader.pages)

        # 自定义目录标题（去掉扩展名）
        title = os.path.splitext(filename)[0]

        bookmarks.append((title, page_offset))
        merger.append(path)

        page_offset += pages

    for title, page in bookmarks:
        merger.add_outline_item(title, page)

    merger.write(output)
    merger.close()

src = "pdfs" if len(sys.argv) < 2 else sys.argv[1]
dst = "merged.pdf" if len(sys.argv) < 3 else sys.argv[2]
merge_folder(src, dst)
