import os
import math
import zipfile
import spacy
import pandas as pd

nlp = spacy.load('en_core_web_trf')


def get_number_of_digits_to_name(num):
    if num <= 0:
        return 0

    return math.floor(math.log10(num)) + 1


def unzip_epub(filepath, out_path):
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(out_path)


def zip_epub(filepath, out_path):
    # shutil.make_archive(out_path, 'zip', filepath)

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


def extract_sentence_to_translate(sentences_list, output_dir, epub_name):
    file_name = drop_extension(epub_name)
    df = pd.DataFrame({"sentence": sentences_list})
    df.to_csv(os.path.join(output_dir, f'{file_name}.csv'), header=False)
