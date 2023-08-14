import os
import shutil
import pandas as pd
from fastapi import HTTPException, status
from bs4 import BeautifulSoup, Tag

from utils.utils import (unzip_file, get_number_of_digits_to_name,
                         drop_extension, zip_file, sentence_segment,
                         extract_sentence_to_translate, find_file_dir)
from utils.translator import translations

try:
    from afaligner import align
except ImportError:
    print('❌ Synchronization requires afaligner library. You should install it and try again.')
    exit(1)


class Epub:
    def __init__(self, epub_path):
        self._epub_path = epub_path
        self._epub_dir, self._epub_file = os.path.split(epub_path)
        self._epub_files_path = os.path.join(self._epub_dir, "epub_files")
        self._chapters_dir = os.path.join(self._epub_files_path, "..", "chapters")
        self._synced_epub_file = f'{drop_extension(self._epub_file)}_synced.epub'
        self._synced_t_epub_file = f'{drop_extension(self._epub_file)}_synced-t.epub'
        self._tagged_epub_file = f'{drop_extension(self._epub_file)}_tagged.epub'
        self._synced_epub_path = os.path.join(self._epub_dir, self._synced_epub_file)
        self._tagged_epub_path = os.path.join(self._epub_dir, self._tagged_epub_file)
        self._synced_t_epub_path = os.path.join(self._epub_dir, self._synced_t_epub_file)
        self._current_dir = os.path.dirname(os.path.realpath(__file__))
        self._epub_txt_files_base_dir = None

    def _unzip_epub(self):
        unzip_file(self._epub_path, self._epub_files_path)

    def _zip_epub(self, synced_path):
        zip_file(self._epub_files_path, synced_path)

    def _pars_content_opf(self):
        self._unzip_epub()
        self._epub_files_path = find_file_dir("content.opf", self._epub_files_path)
        with open(os.path.join(self._epub_files_path, "content.opf")) as fp:
            soup = BeautifulSoup(fp, "xml")

        item_refs = soup.spine.find_all("itemref")
        items = soup.manifest.find_all("item")

        html_files = []
        for item_ref in item_refs:
            if "title" in item_ref['idref']:
                continue
            html_files.append(item_ref['idref'])

        html_file_paths = []
        audio_file_paths = []
        for html_file in html_files:
            found = False
            for item in items:
                if item["id"] == html_file:
                    html_file_paths.append(item["href"])
                    found = True
                    break
            if not found:
                raise Exception(f"{html_file} not found in the manifest items")

        for item in items:
            if item["media-type"] == "audio/mpeg":
                audio_file_paths.append(item["href"])

        if os.path.sep in html_file_paths[0]:
            base_dir, _ = os.path.split(html_file_paths[0])
            self._epub_txt_files_base_dir = base_dir

        html_file_paths.sort()
        audio_file_paths.sort()
        return html_file_paths, audio_file_paths

    def _set_id_tag_with_audio(self):

        html_files_list, audio_files_list = self._pars_content_opf()
        if len(html_files_list) != len(audio_files_list):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=translations.get("audio_book_files_not_match"))
        chapter_num = 1
        for i in range(len(html_files_list)):
            html_filepath = html_files_list[i]
            audio_file_src = os.path.join(self._epub_files_path, audio_files_list[i])
            soup, input_file, output_dir, _ = self._extract_sentences(html_filepath, chapter_num)

            chapter_num += 1
            with open(input_file, 'w') as f:
                f.write(soup.prettify())

            text_dir = os.path.join(output_dir, "sync_text")
            if not os.path.isdir(text_dir):
                os.makedirs(text_dir)
            shutil.copy(input_file, text_dir)

            audio_file_dest = os.path.join(output_dir, "audio")
            if not os.path.isdir(audio_file_dest):
                os.makedirs(audio_file_dest)
            try:
                shutil.copy(audio_file_src, audio_file_dest)
            except FileNotFoundError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=translations.get("no_audio_file"))

    def _set_id_tag(self):

        html_files_list, _ = self._pars_content_opf()

        chapter_num = 1
        for i in range(len(html_files_list)):
            html_filepath = html_files_list[i]
            soup, input_file, output_dir, _ = self._extract_sentences(html_filepath, chapter_num)

            chapter_num += 1
            with open(input_file, 'w') as f:
                f.write(soup.prettify())

            text_dir = os.path.join(output_dir, "sync_text")
            if not os.path.isdir(text_dir):
                os.makedirs(text_dir)
            shutil.copy(input_file, text_dir)

    def _sync(self, alignment_radius=None, alignment_skip_penalty=None, language="eng"):
        chapter_dirs = (os.path.join(self._chapters_dir, f) for f in sorted(os.listdir(self._chapters_dir)))
        for chapter_dir in chapter_dirs:
            sync_text_dir = os.path.join(chapter_dir, "sync_text")
            audio_dir = os.path.join(chapter_dir, 'audio')
            output_dir = os.path.join(chapter_dir, "smil")
            print('Calling afaligner for syncing...')
            sync_map = align(
                sync_text_dir, audio_dir, output_dir,
                output_format='smil',
                sync_map_text_path_prefix='../text/',
                sync_map_audio_path_prefix='../audio/',
                radius=alignment_radius,
                skip_penalty=alignment_skip_penalty,
                language=language,
            )
            if sync_map is not None:
                print('✔ Text and audio have been successfully synced.')

            smil_files = (os.path.join(output_dir, f) for f in sorted(os.listdir(output_dir)))
            smils_output = os.path.join(self._epub_files_path,
                                        self._epub_txt_files_base_dir) if self._epub_txt_files_base_dir else self._epub_files_path
            for smil in smil_files:
                try:
                    shutil.move(smil, smils_output)
                except Exception as ex:
                    self._cleanup()
                    raise Exception(ex, "If you want to resync the book, Please set the resync argument to True.")

    def _extract_sentences(self, html_filepath, chapter_num):
        output_dir = os.path.join(self._chapters_dir, f'c{chapter_num}')
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        input_file = os.path.join(self._epub_files_path, html_filepath)
        with open(input_file, 'r') as fp:
            soup = BeautifulSoup(fp, 'html.parser')

        tags_with_text = [tag for tag in soup.find_all() if
                          len(tag.contents) == 1 and not isinstance(tag.contents[0],
                                                                    Tag) and tag.name != 'title' and tag.text.strip()]
        sentences_zip, fragments_num = sentence_segment(tags_with_text)
        n = get_number_of_digits_to_name(fragments_num)

        fragment_id = 1
        translate_data = {"fragment_id": [], "sentence": [], "translation": []}
        for t, sents in sentences_zip:
            span_list = []
            t.string = ''
            for s in sents:
                f_id = f'f{fragment_id:0>{n}}'
                span_tag = soup.new_tag("span", attrs={"id": f_id})
                translate_data["sentence"].append(s.text)
                translate_data["fragment_id"].append(f_id)
                translate_data["translation"].append("")
                span_tag.string = s.text
                span_list.append(span_tag)
                fragment_id += 1
                t.append(span_tag)
        return soup, input_file, output_dir, translate_data

    def extract_sentence(self):
        html_files_list, _ = self._pars_content_opf()
        chapter_num = 1
        translate_data_list = []
        for html_filepath in html_files_list:
            soup, input_file, output_dir, translate_data = self._extract_sentences(html_filepath, chapter_num)
            translate_data_dict = {'epub_name': html_filepath, 'translate_data': translate_data}
            translate_data_list.append(translate_data_dict)
            chapter_num += 1
        self._set_id_tag()
        self._zip_epub(self._tagged_epub_path)
        extract_sentence_to_translate(translate_data_list, self._epub_dir, self._tagged_epub_path)
        self._cleanup()

    def sync_translation(self, csvs):
        csvs_dir, csvs_file = os.path.split(csvs)
        unzip_file(csvs, csvs_dir)
        csvs_path = drop_extension(csvs_file)
        extracted_csvs_path = os.path.join(csvs_dir, csvs_path)
        html_files_list = self._pars_content_opf()
        csv_files = (os.path.join(extracted_csvs_path, f) for f in sorted(os.listdir(extracted_csvs_path)))
        for i, csv_file in enumerate(csv_files):
            _, file_name = os.path.split(csv_file)
            df = pd.read_csv(csv_file)
            df.fillna("", inplace=True)

            text_list = ['<?xml version="1.0" encoding="utf-8"?> version="3.0">\n', '<ttx language="fa">\n']
            for index, row in df.iterrows():
                f_id = row['fragment_id']
                translation = row['translation']
                txt = f'\t<text src="../{html_files_list[i]}#{f_id}">{str(translation)}</text>\n'
                text_list.append(txt)

            text_list.append('</ttx>\n')
            ttx_output = os.path.join(self._epub_files_path,
                                      self._epub_txt_files_base_dir) if self._epub_txt_files_base_dir else self._epub_files_path
            with open(os.path.join(ttx_output, f'{drop_extension(file_name)}.ttx'), 'w') as f:
                f.write(''.join(text_list))

        self._zip_epub(self._synced_t_epub_path)
        self._cleanup()

    def sync_audio(self):
        self._set_id_tag_with_audio()
        self._sync()
        self._zip_epub(self._synced_epub_path)
        self._cleanup()

    def _cleanup(self):
        if os.path.isdir(self._chapters_dir):
            shutil.rmtree(self._chapters_dir)
        if os.path.isdir(self._epub_files_path):
            shutil.rmtree(self._epub_files_path)
