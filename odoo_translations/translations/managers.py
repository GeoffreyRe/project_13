from django.db import models
from django.apps import apps

class CustomTranslationBlockManager(models.Manager):

    
    def create_block_from_data(self, data, file, is_header=False):
        if is_header is True:
            block = self.create(
                file=file,
                is_header=True,
                raw_text="\n".join(data)
            )
            return block