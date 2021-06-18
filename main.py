from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4, inch
import arrow
import logging
import os
logger = logging.getLogger(__name__)
import code128

class ManualBarcodeSequenceGeneration:
    def __init__(self, seq_start="", seq_steps=1, seq_prefix="", seq_suffix="", seq_counts="10", seq_manual=None,
                 page_size="A4", tot_digits="10"):
        self.seq_start = seq_start
        self.seq_steps = int(seq_steps)
        self.seq_prefix = seq_prefix
        self.seq_suffix = seq_suffix
        self.seq_counts = int(seq_counts)
        self.seq_manual = seq_manual
        self.page_size = page_size
        total_prefix_suffix_length = len(seq_prefix) + len(seq_suffix)

        self.remaining_seq_length = int(tot_digits) - total_prefix_suffix_length
        self.file_base = ""
        #self.barcode_folder = '/media/temp_remove/barcodes/'
        self.barcode_folder ="temp\\"
        self.abs_path = self.file_base + self.barcode_folder
        os.makedirs(self.abs_path, exist_ok=True)

    def generate_series(self):
        if self.seq_manual:
            self.series = self.seq_manual.split(",")
        else:
            self.series = []
            generate_no = self.seq_start
            for gen_step in range(self.seq_counts):
                padding_zeros = "0" * (self.remaining_seq_length - len(generate_no))
                label_item = self.seq_prefix + padding_zeros + generate_no + self.seq_suffix
                self.series.append(label_item)
                generate_no = str(int(generate_no) + self.seq_steps)

    def call_A4(self):
        """ To generate labels of 2x1 inch size and fit multiple labels in A4 paper"""
        PAGE_SIZE = A4
        pdf_name = 'barcodes_A4_' + arrow.now().format('YYYY-MM-DD-HH-mm-s') + '.pdf'
        barcode_canvas = canvas.Canvas(self.abs_path + pdf_name, pagesize=PAGE_SIZE)

        y = 11.75 * inch
        x = 10
        for key, series_item in enumerate(self.series):
            z = code128.image(series_item)
            z.save(self.abs_path + series_item + ".png")
            barcode_canvas.drawImage(self.abs_path + series_item + ".png", x, y - 1 * inch, 2 * inch, 0.8 * inch,
                                     preserveAspectRatio=True)
            barcode_canvas.drawString(x + 0.2 * inch, y - 1.1 * inch, series_item)

            x = x + 2 * inch
            # In A4 size each row will contain 4 labels and there can be 36 labels in a A4 page
            if (key + 1) % 4 == 0:
                x = 10
                y = y - inch * 1.25
            if ((key + 1) % 36 == 0):
                barcode_canvas.showPage()
                y = 11.75 * inch
                x = 10

        barcode_canvas.showPage()
        barcode_canvas.save()
        return self.barcode_folder + pdf_name

    def call_2x1(self):
        """ To generate lables of 2x1 inches"""

        PAGE_SIZE = (2 * inch, 1 * inch)
        pdf_name = 'barcodes_2x1_' + arrow.now().format('YYYY-MM-DD-HH-mm-s') + '.pdf'
        barcode_canvas = canvas.Canvas(self.abs_path + pdf_name, pagesize=PAGE_SIZE)

        for series_item in self.series:
            z = code128.image(series_item)
            z.save(self.abs_path + series_item + ".png")

            barcode_canvas.drawImage(self.abs_path + series_item + ".png", 0, 0.2 * inch, 2 * inch, 0.9 * inch,
                                     preserveAspectRatio=True)
            barcode_canvas.drawString(20, 0.1 * inch, series_item)
            barcode_canvas.showPage()
            os.remove(self.abs_path + series_item + ".png")

        barcode_canvas.save()
        return self.barcode_folder + pdf_name

    def set_page_size(self):
        """ Based on page size, relevant function call is chosen. Default A4 size """
        page_size_conf = {'A4': self.call_A4,
                          '2x1 inch': self.call_2x1}
        return page_size_conf.get(self.page_size, self.call_A4)

    def generate_barcodes(self):
        # Client Interface to generate series and barcode pdf. Returns file name as output
        self.generate_series()
        page_size_fn = self.set_page_size()
        generated_file = page_size_fn()
        #print(generated_file)
        return generated_file
if __name__ != "main":
    seq_prefix = input("Enter prefix that should appear in the generated barcode(Optional)")
    seq_start = input("Enter Starting number of the sequence(mandatory)")
    seq_suffix = input("Enter Suffix that should appear in the generated barcode(Optional)")
    seq_steps = input("Enter increment number for the sequence(Optional, Default=1) )")
    seq_counts = input("Enter Number of barcodes that are to be generated(Optional, Default=10) )")
    page_size = input("Enter Printer Page Settings(2x1 inch or A4) (Optional, Default=A4) )")
    tot_digits = input("Enter Length of barcode (Default:10))")
    barcode = ManualBarcodeSequenceGeneration(seq_start=seq_start, seq_steps=seq_steps, \
                                    seq_prefix=seq_prefix, seq_suffix=seq_suffix,\
                                    seq_counts=seq_counts, page_size=page_size, tot_digits=tot_digits)
    generated_file = barcode.generate_barcodes()
    print(f"Your file is ready: {generated_file}")