from django.test import TestCase, Client
from users.models import User
from projects.models import Project
from translations.models import TranslationFile, TranslationBlock, LineType, InstanceType, TranslationLine, Instance
from django.core.files.uploadedfile import InMemoryUploadedFile
from unittest import mock
import io

# Create your tests here.
class TranslationsManagerTest(TestCase):
    """
    This class contains tests of manager methods of 'translations' application
    """

    @mock.patch('django.core.files.storage.FileSystemStorage.save')
    def setUp(self, mock_save):
        """
        This function is executed each time a new test function is executed
        """
        mock_save.return_value = 'fr.po'
        self.client = Client()
        self.user1 = User.objects.create_user(
            username="Michel", password="1234", email="test@test.com")
        self.user2 = User.objects.create_user(
            username="Jean", password="1234", email="jean@test.com")
        
        self.project_test = Project.objects.create(**{
            'name': 'projet 1',
            'description': 'description 1',
            'creator': self.user1})
        
        test_file = in_memory_test_file = InMemoryUploadedFile(
            name='fr_test.po',
            file=io.BytesIO(b'test'),
            field_name=None,
            size=None,
            charset=None,
            content_type=None
        )
        self.file = TranslationFile.objects.create(name='fichier test',
                                        project=self.project_test,
                                        translated_language='fr',
                                        original_file=test_file)
    
    def test_manager_update_translated_texts_modify_texts(self):
        block = TranslationBlock.objects.create(
            file=self.file,
            raw_text="",
            original_text="VAT",
            translated_text="BTW"
        )

        self.assertEqual(block.translated_text, 'BTW')
        TranslationBlock.objects.update_translated_texts([{'id': block.id, 'translated_text': 'VAT'}])
        block.refresh_from_db()
        self.assertEqual(block.translated_text, 'VAT')
    
    def test_create_block_from_data_creates_new_block(self):

        data = {
            'block': 'block test',
            'msgid': 'VAT',
            'msgstr': 'TVA',
            'supported_lines': []
        }
        self.assertEqual(len(TranslationBlock.objects.all()), 0)
        TranslationBlock.objects.create_block_from_data(data, self.file)
        self.assertEqual(len(TranslationBlock.objects.all()), 1)
        self.assertEqual(TranslationBlock.objects.all()[0].original_text,data['msgid'])
        self.assertEqual(TranslationBlock.objects.all()[0].translated_text,data['msgstr'])



# Create your tests here.
class TranslationBlockTest(TestCase):
    """
    This class contains tests of TranslationBlock of 'translations' application
    """

    @mock.patch('django.core.files.storage.FileSystemStorage.save')
    def setUp(self, mock_save):
        """
        This function is executed each time a new test function is executed
        """
        mock_save.return_value = 'fr.po'
        self.client = Client()
        self.user1 = User.objects.create_user(
            username="Michel", password="1234", email="test@test.com")
        self.user2 = User.objects.create_user(
            username="Jean", password="1234", email="jean@test.com")
        
        self.project_test = Project.objects.create(**{
            'name': 'projet 1',
            'description': 'description 1',
            'creator': self.user1})
        
        test_file = in_memory_test_file = InMemoryUploadedFile(
            name='fr_test.po',
            file=io.BytesIO(b'test'),
            field_name=None,
            size=None,
            charset=None,
            content_type=None
        )
        self.file = TranslationFile.objects.create(name='fichier test',
                                        project=self.project_test,
                                        translated_language='fr',
                                        original_file=test_file)
    
    def test_check_errors_content(self):
        result = TranslationBlock.check_errors_content([
                                            '#. module: belcco',
                                            '#: model:ir.model,name:belcco.model_product_template',
                                            '#: model:ir.model.fields,field_description:belcco.field_product_index_history_template',
                                            'msgid "Product Template"',
                                            'msgstr "Modèle de produit"'],0)
        
        self.assertEqual(result[1]['supported_lines'], [{
            'line': '#. module: belcco',
            'instance': {'type': 'module', 'name': ' belcco'},
            'line_type': 'name'},
            {'line': '#: model:ir.model,name:belcco.model_product_template',
            'instance': {'type': 'ir.model', 'name': 'belcco.model_product_template'},
            'line_type': 'name'},
            {'line': '#: model:ir.model.fields,field_description:belcco.field_product_index_history_template',
            'instance': {'type': 'ir.model.fields', 'name': 'belcco.field_product_index_history_template'},
            'line_type': 'field_description'}])
    
    def test_check_errors_content_when_header(self):
        result = TranslationBlock.check_errors_content([
                                            '# Translation of Odoo Server.',
                                            '#: model:ir.model,name:belcco.model_product_template',
                                            '#: model:ir.model.fields,field_description:belcco.field_product_index_history_template',
                                            'msgid "Product Template"',
                                            'msgstr "Modèle de produit"'],0, is_header=True)
        self.assertEqual(result, (False,))
    

    def test_check_errors_content_when_header_but_no_header(self):
        result = TranslationBlock.check_errors_content([
                                            '#. module: belcco',
                                            '#: model:ir.model,name:belcco.model_product_template',
                                            '#: model:ir.model.fields,field_description:belcco.field_product_index_history_template',
                                            'msgid "Product Template"',
                                            'msgstr "Modèle de produit"'],0, True, 'fr.po')
        self.assertEqual(result, (True, "Erreur lors de l'analyse du fichier fr.po: ligne 0 ---" \
            " le premier bloc n'est pas le header"))


class TranslationLineTest(TestCase):
    """
    This class contains tests of TranslationLine of 'translations' application
    """

    def setUp(self):
        self.line_type = LineType.objects.create(name='name')
        self.instance_type = InstanceType.objects.create(name='ir.model')
        InstanceType.objects.create(name='module')
        InstanceType.objects.create(name='ir.model.fields')
        InstanceType.objects.create(name='ir.ui.view')
        InstanceType.objects.create(name='ir.actions.act_window')
        InstanceType.objects.create(name='ir.ui.menu')
        InstanceType.objects.create(name='code')
        InstanceType.objects.create(name='code.position')
        self.user1 = User.objects.create_user(
            username="Michel", password="1234", email="test@test.com")
        self.user2 = User.objects.create_user(
            username="Jean", password="1234", email="jean@test.com")
        
        self.project_test = Project.objects.create(**{
            'name': 'projet 1',
            'description': 'description 1',
            'creator': self.user1})
        
        test_file = in_memory_test_file = InMemoryUploadedFile(
            name='fr_test.po',
            file=io.BytesIO(b'test'),
            field_name=None,
            size=None,
            charset=None,
            content_type=None
        )
        self.file = TranslationFile.objects.create(name='fichier test',
                                        project=self.project_test,
                                        translated_language='fr',
                                        original_file=test_file)
        self.block = TranslationBlock.objects.create(
            file=self.file,
            raw_text="",
            original_text="VAT",
            translated_text="BTW"
        )
    
    def test_find_or_create_instance_create_instance(self):
        self.assertEqual(len(Instance.objects.all()), 0)
        TranslationLine(block=self.block).find_or_create_instance('account_invoice', self.instance_type, self.line_type)
        self.assertEqual(len(Instance.objects.all()), 1)
        self.assertEqual(Instance.objects.all()[0].name,'account_invoice')

    def test_find_or_create_instance_retrieve_instance(self):
        new_instance = Instance.objects.create(name='account_invoice', instance_type=self.instance_type, project=self.project_test)
        self.assertEqual(len(Instance.objects.all()), 1)
        line = TranslationLine(block=self.block)
        line.find_or_create_instance('account_invoice',
        self.instance_type, self.line_type)
        self.assertEqual(len(Instance.objects.all()), 1)
        self.assertEqual(line.instance,new_instance)
    
    def test_analyze_infos_find_infos(self):
        line = TranslationLine(block=self.block)
        self.assertEqual(len(Instance.objects.all()), 0)
        line.analyze_infos({
            'line': '#. module: belcco',
            'instance': {'type': 'module', 'name': ' belcco'}, 'line_type': 'name'},0)
        self.assertEqual(len(Instance.objects.all()), 1)
        self.assertEqual(line.instance, Instance.objects.all()[0])


class TranslationsViewsTest(TestCase):
    """
    This class contains tests of views of 'translations' application
    """

    def setUp(self):
        self.client = Client()
        self.line_type = LineType.objects.create(name='name')
        self.instance_type = InstanceType.objects.create(name='ir.model')
        self.user1 = User.objects.create_user(
            username="Michel", password="1234", email="test@test.com")
        self.user2 = User.objects.create_user(
            username="Jean", password="1234", email="jean@test.com")
        
        self.project_test = Project.objects.create(**{
            'name': 'projet 1',
            'description': 'description 1',
            'creator': self.user1})
        
        test_file = in_memory_test_file = InMemoryUploadedFile(
            name='fr_test.po',
            file=io.BytesIO(b'test'),
            field_name=None,
            size=None,
            charset=None,
            content_type=None
        )
        self.file = TranslationFile.objects.create(name='fichier test',
                                        project=self.project_test,
                                        translated_language='fr',
                                        original_file=test_file)
        self.block = TranslationBlock.objects.create(
            file=self.file,
            raw_text="",
            original_text="VAT",
            translated_text="BTW"
        )
    
    @mock.patch('users.models.User.userproject_set')
    @mock.patch('projects.models.Project.objects.get')
    @mock.patch('projects.models.Project.all_instances')
    def test_instance_translations_list(self, all_instances_mock, get_mock, userproject_mock):
        self.client.login(email='test@test.com', password='1234')
        get_mock.return_value = self.project_test
        filter_mock = mock.MagicMock()
        filter_mock.return_value = ['project']
        userproject_mock.filter = filter_mock
        new_instance = Instance.objects.create(name='account_invoice', instance_type=self.instance_type, project=self.project_test)
        all_instances_mock.return_value = [{'instance': new_instance, 'nb_fr': 2, 'nb_ndlr': 1}]
        response = self.client.get('/project/111/translations/models')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['project'], self.project_test)

    @mock.patch('users.models.User.userproject_set')
    @mock.patch('projects.models.Project.translations_instances')
    @mock.patch('projects.models.Project.objects.get')
    def test_instance_translations(self, get_mock, translation_instances_mock, userproject_mock):
        self.client.login(email='test@test.com', password='1234')
        translation_instances_mock.return_value = ['instance', ['ligne 1', 'ligne 2']]
        filter_mock = mock.MagicMock()
        filter_mock.return_value = ['project']
        userproject_mock.filter = filter_mock
        get_mock.return_value = self.project_test
        response = self.client.get('/project/111/translations/models')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['project'], self.project_test)
    
    @mock.patch('users.models.User.userproject_set')
    @mock.patch('projects.models.Project.translations_instances')
    @mock.patch('projects.models.Project.objects.get')
    def test_all_instance_translations(self, get_mock, translation_instances_mock, userproject_mock):
        self.client.login(email='test@test.com', password='1234')
        translation_instances_mock.return_value = ['instance', ['ligne 1', 'ligne 2']]
        filter_mock = mock.MagicMock()
        filter_mock.return_value = ['project']
        userproject_mock.filter = filter_mock
        get_mock.return_value = self.project_test
        response = self.client.get('/project/111/translations/models/all')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['project'], self.project_test)
    
    def test_get_block_translation(self):
        self.client.login(email='test@test.com', password='1234')
        #breakpoint()
        response = self.client.get('/translations/get_translations', {'block': self.block.id})
        #self.assertEqual(response.json()['translation'], self.block.translated_text)