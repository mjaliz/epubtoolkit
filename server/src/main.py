from epubtoolkit.epub import Epub
from epubtoolkit.utils import translate_csv

epub = Epub("../books/robin_hood/Robin Hood.epub")
epub.sync_audio()

translate_csv("../books/robin_hood/csvs/")
