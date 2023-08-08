import os
import math
import zipfile
import spacy
import pandas as pd
from deep_translator import GoogleTranslator

nlp = spacy.load('en_core_web_trf')


def get_number_of_digits_to_name(num):
    if num <= 0:
        return 0

    return math.floor(math.log10(num)) + 1


def unzip_epub(filepath, out_path):
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(out_path)


def zip_file(filepath, out_path):
    def zipdir(path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, os.path.join(path))
                ziph.write(file_path, rel_path)

    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir(filepath, zipf)


def drop_extension(filename):
    return filename.split('.')[0]


def sentence_segment(tags):
    sentences = []
    sentences_count = 0
    for tag in tags:
        doc = nlp(tag.text)
        assert doc.has_annotation("SENT_START")
        sentences.append(doc.sents)
        sentences_count += len(list(doc.sents))
    return zip(tags, sentences), sentences_count


def extract_sentence_to_translate(translate_data_list, epub_files_path):
    book_name = os.path.basename(epub_files_path)
    csvs_dir = f'{book_name}_csvs'
    output_dir = os.path.join(epub_files_path, csvs_dir)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    for td in translate_data_list:
        epub_name = td['epub_name']
        translate_data = td['translate_data']
        file_name = drop_extension(epub_name)
        df = pd.DataFrame(translate_data)
        df.to_csv(os.path.join(output_dir, f'{file_name}.csv'), index=False)

    zip_file(output_dir, os.path.join(epub_files_path, f"{csvs_dir}.zip"))


def translator(text):
    return GoogleTranslator(source='en', target='fa').translate(text)


def translate_csv(csvs_dir):
    csv_files = (os.path.join(csvs_dir, f) for f in sorted(os.listdir(csvs_dir)))
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        df["translation"] = df["sentence"].apply(translator)
        df.to_csv(csv_file, index=False)
