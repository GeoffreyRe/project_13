from django.db import models
from django.apps import apps

class CustomTranslationBlockManager(models.Manager):

    
    def create_block_from_data(self, data, file, is_header=False):
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
                new_translation_line.analyze_infos(translation_line)
