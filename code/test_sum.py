
from datetime import datetime
import os
from reportlab.lib.
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import landscape, letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

date_stamp = "{:%Y_%m_%d}".format(datetime.now())

in_path = os.path.join('/Users/st_buckls/programming/Projects/ExecutiveSummary/in')
out_path = os.path.join('/Users/st_buckls/programming/Projects/ExecutiveSummary/out')

# Setup the document
doc = SimpleDocTemplate((os.path.join(out_path, "Image_And_Table_Test_%s.pdf") % date_stamp), pagesize=A4)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))

# Story contains all elements to add to document
Story = []

# Mock table data
table_info = [['Modality', 'TE', 'TR', 'TI',     'x',   'y',   'z'],
              ['T1',       '120', '2300', '9', '240', '160', '256'],
              ['T2',       '120', '2300', '9', '240', '160', '256'],
              ['REST1',    '120', '2300', '9', '240', '160', '256'],
              ['REST2',    '120', '2300', '9', '240', '160', '256'],
              ['REST3',    '120', '2300', '9', '240', '160', '256'],
              [],
              []]

structural_imgs = ['temp_13', 'temp_3', 'temp_9',  # T1 panel
                   'temp_14', 'temp_4', 'temp_10']  # T2 panel

im1 = Image(os.path.join(in_path, 'temp_13.png'), inch*2, inch*1.5)
im2 = Image(os.path.join(in_path, 'temp_3.png'), inch*2, inch*1.5)
im3 = Image(os.path.join(in_path, 'temp_9.png'), inch*2, inch*1.5)
im4 = Image(os.path.join(in_path, 'temp_14.png'), inch*2, inch*1.5)
im5 = Image(os.path.join(in_path, 'temp_4.png'), inch*2, inch*1.5)
im6 = Image(os.path.join(in_path, 'temp_10.png'), inch*2, inch*1.5)

Images = [im1, im2, im3, im4, im5, im6]

dvars_im = Image(os.path.join(in_path, 'DVARS_and_FD_CONCA.png'), inch*4, inch*4)

for image in Images:
    Story.append(image)
    #Story.append(Spacer(width=1, height=12))

Story.append(Spacer(1, 24))
Story.append(dvars_im)

# setup Table
t = Table(table_info, 5*[0.4*inch], 4*[0.4*inch])
# wh_table.setStyle(TableStyle(
#     [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
#      ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
#      ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
#      ('BACKGROUND', (0, 0), (-1, 0), colors.gray)]))



doc.build(Story)

c = canvas.Canvas('testing.pdf')
