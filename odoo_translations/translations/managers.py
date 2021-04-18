from django.db import models
from django.apps import apps


class CustomTranslationBlockManager(models.Manager):

    def create_block_from_data(self, data, file, block_position=False, is_header=False):
        TranslationLine = apps.get_model('translations', 'TranslationLine')
        if is_header is True:
            # if it is a header
            block = self.create(
                file=file,
                is_header=True,
                raw_text="\n".join(data)
            )
            return block

        else:
            # else, it is a standard block
            block = self.create(
                file=file,
                is_header=False,
                raw_text=data['block'],
                original_text=data['msgid'],
                translated_text=data['msgstr']
            )

            for translation_line in data['supported_lines']:
                new_translation_line = TranslationLine(block=block)
                new_translation_line.analyze_infos(translation_line, block_position)

    def update_translated_texts(self, values):
        """
        This method takes as argument a list of dict with 2 key/values:
        - id of block and new translated text
        """
        for block_val in values:
            block_id = block_val['id']
            if not block_val['translated_text']:
                continue
            block = self.get(id=block_id)
            block.translated_text = block_val['translated_text']
            block.save()
