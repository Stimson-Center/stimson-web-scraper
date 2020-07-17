import os
import re
import json
import tempfile
from flask import request, send_file
from flask_restful import Resource
from fpdf import FPDF
from fpdf.ttfonts import TTFontFile
from scraper.restful.models import ArticleProcess

__title__ = 'stimson-web-scraper'
__author__ = 'Alan S. Cooper'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020, The Stimson Center'
__maintainer__ = "The Stimson Center"
__maintainer_email = "cooper@pobox.com"


class FPDF3(FPDF):
    def add_font(self, family, fname):
        "Add a TrueType or Type1 font"
        family = family.lower()
        fontkey = family
        # Font already added!
        if family in self.fonts: return
        font_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'fonts'))
        self.FPDF_FONT_DIR = font_dir
        ttffilename = os.path.join(self.FPDF_FONT_DIR, fname)
        name = ''  # noqa: F841
        unifilename = None
        font_dict = None
        if font_dict is None:
            ttf = TTFontFile()
            ttf.getMetrics(ttffilename)
            desc = {
                'Ascent'       : int(round(ttf.ascent, 0)),
                'Descent'      : int(round(ttf.descent, 0)),
                'CapHeight'    : int(round(ttf.capHeight, 0)),
                'Flags'        : ttf.flags,
                'FontBBox'     : "[%s %s %s %s]" % (
                    int(round(ttf.bbox[0], 0)),
                    int(round(ttf.bbox[1], 0)),
                    int(round(ttf.bbox[2], 0)),
                    int(round(ttf.bbox[3], 0))),
                'ItalicAngle'  : int(ttf.italicAngle),
                'StemV'        : int(round(ttf.stemV, 0)),
                'MissingWidth' : int(round(ttf.defaultWidth, 0)),
            }

            # Generate metrics .pkl file
            font_dict = {
                'name'         : re.sub('[ ()]', '', ttf.fullName),
                'type'         : 'TTF',
                'desc'         : desc,
                'up'           : round(ttf.underlinePosition),
                'ut'           : round(ttf.underlineThickness),
                'ttffile'      : ttffilename,
                'fontkey'      : fontkey,
                'originalsize' : os.stat(ttffilename).st_size,
                'cw'           : ttf.charWidths,
            }

        # include numbers in the subset! (if alias present)
        have_page_alias = lambda: hasattr(self, 'str_alias_nb_pages')
        sbarr = list(range(0, 57 if have_page_alias() else 32))

        self.fonts[fontkey] = {
            'i'           : len(self.fonts) + 1,
            'type'        : font_dict['type'],
            'name'        : font_dict['name'],
            'desc'        : font_dict['desc'],
            'up'          : font_dict['up'],
            'ut'          : font_dict['ut'],
            'cw'          : font_dict['cw'],
            'ttffile'     : font_dict['ttffile'],
            'fontkey'     : fontkey,
            'subset'      : sbarr,
            'unifilename' : unifilename
        }
        self.font_files[fontkey] = {'length1': font_dict['originalsize'],
                                    'type': "TTF", 'ttffile': ttffilename}
        self.font_files[fname]   = {'type': "TTF"}

    # def output(self):
    #     """Output PDF to some destination
    #     """
    #     # Finish document if necessary
    #     self.close()
    #     # manage binary data as latin1 until PEP461 or similar is
    #     # implemented
    #     return self.buffer.encode("latin1")

    def write_section(self, section_name, text, delimiter='\n'):
        for i, txt in enumerate(text.split(delimiter)):
            if i == 0:
                txt = f'{section_name}: {txt}'
            self.write(8, txt)
            self.ln(8)
        self.write(8, " ")
        self.ln(8)

class PDF(Resource):
    @staticmethod
    def post():
        form = request.get_json()
        article = ArticleProcess.create_article(form['url'], form['config']['language'], form['config']['translate'])
        article.set_json(form)
        pdf = FPDF3()
        pdf.add_font('OpenSans', 'OpenSans-Regular.ttf')
        pdf.set_font('OpenSans', '', 14)
        # Add a page
        pdf.add_page()
        pdf.write_section('TITLE', article.title)
        pdf.write_section('DATE', article.publish_date)
        pdf.write_section('AUTHOR', json.dumps(article.authors))
        pdf.write_section('SUMMARY', article.summary)
        pdf.write_section('ARTICLE', article.text)
        pdf.write_section('KEYWORDS', json.dumps(article.keywords))
        pdf.write_section('URL', article.url)
        # get the pdf as an array of bytes
        buffer = pdf.output(dest='S')
        # send the pdf with name .pdf
        # filename = f"{article.publish_date}_{article.title}.{article.config._language}.pdf"
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
        # https://gist.github.com/Miserlou/fcf0e9410364d98a853cb7ff42efd35a
        fp = tempfile.NamedTemporaryFile()
        fp.write(buffer)
        fp.flush()
        fp.seek(0)
        return send_file(
            filename_or_fp=fp,
            attachment_filename=fp.name,
            as_attachment=True,
            mimetype='application/pdf'
        )

