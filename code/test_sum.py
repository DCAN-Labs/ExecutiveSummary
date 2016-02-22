import image_summary
from datetime import datetime
import os
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import landscape, letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Frame, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

date_stamp = "{:%Y_%m_%d}".format(datetime.now())

in_path = os.path.join('/Users/st_buckls/programming/Projects/ExecutiveSummary/in')
out_path = os.path.join('/Users/st_buckls/programming/Projects/ExecutiveSummary/out')

ohsu_in = os.path.join('\\davis.ohsu.edu\\bucklesh\\Projects\\ExecutiveSummary\\inputs')
ohsu_out = os.path.join('\\davis.ohsu.edu\\bucklesh\\Projects\\ExecutiveSummary\\summary')

# Setup the document
doc = SimpleDocTemplate((os.path.join(ohsu_out, "Image_And_Table_Test_%s.pdf") % date_stamp), pagesize=A4)

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

im1 = Image(os.path.join(ohsu_in, 'temp_13.png'), inch*2, inch*1.5)
im2 = Image(os.path.join(ohsu_in, 'temp_3.png'), inch*2, inch*1.5)
im3 = Image(os.path.join(ohsu_in, 'temp_9.png'), inch*2, inch*1.5)
im4 = Image(os.path.join(ohsu_in, 'temp_14.png'), inch*2, inch*1.5)
im5 = Image(os.path.join(ohsu_in, 'temp_4.png'), inch*2, inch*1.5)
im6 = Image(os.path.join(ohsu_in, 'temp_10.png'), inch*2, inch*1.5)

Images = [im1, im2, im3, im4, im5, im6]

dvars_im = Image(os.path.join(ohsu_in, 'DVARS_and_FD_CONCA.png'), inch*4, inch*4)

for image in Images:
    Story.append(image)
    # Story.append(Spacer(width=1, height=12)) # adds a <br> effectively

Story.append(Spacer(1, 24))
Story.append(dvars_im)

# TODO: figure out how to setup Table
# t = Table(table_info, 5*[0.4*inch], 4*[0.4*inch])
# wh_table.setStyle(TableStyle(
#     [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
#      ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
#      ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
#      ('BACKGROUND', (0, 0), (-1, 0), colors.gray)]))

# finally, after all elements added to Story list...
doc.build(Story)

# alternative, lower-level way to build the doc... any better?
c = canvas.Canvas('mydoc.pdf')
f = Frame(inch, inch, 6*inch, 9*inch, showBoundary=1)
f.addFromList(Story, c)
c.save()

