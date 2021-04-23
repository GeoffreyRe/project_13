from django.db import models
from django.apps import apps
from translations.managers import CustomTranslationBlockManager
import re


class TranslationBlock(models.Model):
    file = models.ForeignKey(
        'translations.TranslationFile',
        on_delete=models.CASCADE,
        null=False,
        related_name="translation_blocks")
    raw_text = models.TextField(null=False)
    is_header = models.BooleanField(default=False)
    original_text = models.TextField(null=True, blank=True)
    translated_text = models.TextField(null=True)
    objects = CustomTranslationBlockManager()

    def __str__(self):
        return "block de traduction numéro {} du fichier {}".format(self.id, self.file.name)

    @staticmethod
    def find_lines_infos(translation_lines):
        """
        This method will make a loop over the list of lines given to the function
        and for each line, we will determine type of line, type of instance, ...
        """
        lines_infos = []
        for line in translation_lines:
            # for each line
            line_infos = {"line": line}
            line_parts = line.split(',')
            if len(line_parts) == 1:
                if line_parts[0].startswith('#. module:'):
                    line_infos["instance"] = {
                        "type": "module",
                        "name": line[10:]
                    }
                    line_infos["line_type"] = "name"

                elif line_parts[0].startswith('#: code:'):
                    line_infos["instance"] = {
                        "type": "code",
                        "name": line[8:]
                    }
                    line_infos["line_type"] = "code"

                else:
                    line_infos["instance"] = False

            elif len(line_parts) == 2:
                line_names_list = [
                    "#: model:ir.model",
                    "#: model:ir.model.fields",
                    "#: model:ir.ui.menu",
                    "#: model:ir.actions.act_window",
                    "#: model:ir.ui.view"]
                if line_parts[0] in line_names_list:
                    line_instance = line_parts[1].split(':')
                    if len(line_instance) == 2:

                        line_infos["instance"] = {
                            "type": line_parts[0][9:],
                            "name": line_instance[1]
                        }
                        line_infos["line_type"] = line_instance[0]
                    else:
                        line_infos["instance"] = False

                else:
                    line_infos["instance"] = False
            else:
                line_infos["instance"] = False

            lines_infos.append(line_infos)

        return lines_infos

    @staticmethod
    def check_errors_content(data, line_pos, is_header=False, file_name=False):
        """
        data ==> text content of block, given as a list of lines
        is_header ==> if True, it a header block, checking is different
        line ==>
        This method will check if there are errors in block structure
        if yes: --> return error message
        if no: --> return False
        """
        begin_line = line_pos
        if is_header:
            if data[0] != "# Translation of Odoo Server.":
                return (
                    True,
                    "Erreur lors de l'analyse du fichier {}: ligne {} --- "
                    "le premier bloc n'est pas le header".format(file_name, begin_line))
            else:
                return (False,)

        # if it is a simple translation block
        if len(data) < 4:
            # if length of block is below 4, then it means that the block structure is not good.
            # Indeed, we need, for a block at least 4 lines : one for the module specification,
            # at least one for a instance to translate (translation line),
            # and 2 for the sentence to translate
            # msgstr and msgid
            return (
                True,
                "fichier {}, ligne {} : la structure du bloc n'est pas conforme"
                " -> taille du bloc inférieur à 4 lignes".format(file_name, line_pos))

        # the first line of block should be the module specification line
        supported_lines = []
        module_spec_line = data[0]
        if not module_spec_line.startswith("#. module:"):
            return (
                True,
                "fichier {}, ligne : {} --> ligne de specification "
                "du module attendue mais non trouvée".format(file_name, line_pos))
        # we extract module name from module specification line
        supported_lines.append(module_spec_line.strip())

        # now we have to find msgid and msgstr
        msgid_text = None
        msgstr_text = None

        for pos, line in enumerate(data[1:]):
            # now we will try to see if we could find msgid and msgstr, else we raise error
            line_pos += 1
            if line.startswith('msgid "'):
                msgid_text = []
                line_to_append = line[6:].strip()
                if re.fullmatch('^".*"$', line_to_append):
                    line_to_append = line_to_append[1:-1]
                msgid_text.append(line_to_append)
                i = 1
                if (pos + i) < len(data[1:]):
                    next_line = data[1:][pos + i]
                else:
                    next_line = ""

                while next_line.startswith('"'):
                    line_to_append = next_line.strip()
                    if re.fullmatch('^".*"$', line_to_append):
                        line_to_append = line_to_append[1:-1]

                    msgid_text.append(line_to_append)
                    i += 1
                    if (pos + i) < len(data[1:]):
                        next_line = data[1:][pos + i]
                    else:
                        next_line = ""

            elif line.startswith('msgstr "'):
                if msgid_text is None:
                    # if we found a msgstr before msgid, this is not a good structure
                    return (
                        True,
                        "Erreur fichier {}, ligne {}:"
                        " msgstr trouvé avant msgid".format(file_name, line_pos))

                msgstr_text = []
                line_to_append = line[6:].strip()
                if re.fullmatch('^".*"$', line_to_append):
                    line_to_append = line_to_append[1:-1]
                msgstr_text.append(line_to_append)
                i = 1
                if (pos + i) < len(data[1:]):
                    next_line = data[1:][pos + i]
                else:
                    next_line = ""

                while next_line.startswith('"'):
                    line_to_append = next_line.strip()
                    if re.fullmatch('^".*"$', line_to_append):
                        line_to_append = line_to_append[1:-1]
                    msgstr_text.append(line_to_append)
                    i += 1
                    if (pos + i) < len(data[1:]):
                        next_line = data[1:][pos + i]
                    else:
                        next_line = ""

            elif line.startswith('#: model:') or line.startswith("#: code:") or\
                    line.startswith('#, python-format') or line.startswith('#: '):
                supported_lines.append(line.strip())

            elif line.startswith('"'):
                # if the line begins with this part, then it means it is a part of msgid or msgstr
                pass

            else:
                supported_lines.append(line.strip())
                # return (True, 'Erreur :Fichier {}, ligne {}
                # non reconnue'.format(file_name, line_pos))

        if (not msgid_text) or (not msgstr_text):
            # if we found partially (or not at all) informations about msgid and msgstr
            # we raise error
            return (
                True,
                "Erreur fichier {}, bloc ligne {} : msgstr et/ou"
                " msgid non trouvé dans le bloc".format(
                    file_name,
                    begin_line
                )
                )

        # now we will find informations about lines (line type, instance to translate, etc...)
        TranslationBlock = apps.get_model('translations', 'TranslationBlock')
        supported_lines_parsed = TranslationBlock.find_lines_infos(supported_lines)

        return (
            False,
            {
                "block": "\n".join(data),
                "msgid": "\n".join(msgid_text) if isinstance(msgid_text, list) else msgid_text,
                "msgstr": "\n".join(msgstr_text) if isinstance(msgstr_text, list) else msgstr_text,
                "supported_lines": supported_lines_parsed
            })

    class Meta:
        # rename table created by django in db
        db_table = "translation_block"
