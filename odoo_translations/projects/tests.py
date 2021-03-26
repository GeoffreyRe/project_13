from django.test import TestCase, Client
from django.utils import timezone
from django.core.files.uploadedfile import InMemoryUploadedFile
from projects.models import Project, Role, UserProject, Invitation
from translations.models import TranslationFile
from users.models import User
from unittest import mock
import datetime
import io

# Create your tests here.
class ProjectTest(TestCase):
    """
    This class contains tests of views of 'projects' application
    """

    def setUp(self):
        """
        This function is executed each time a new test function is executed
        """
        self.user1 = User.objects.create_user(
            username="Michel", password="1234", email="test@test.com")
        self.user2 = User.objects.create_user(
            username="Jean", password="1234", email="jean@test.com")
        
        self.project_test = Project.objects.create(**{
            'name': 'projet 1',
            'description': 'description 1',
            'creator': self.user1})
        self.dev_role = Role.objects.create(name="DEV")

    def test_can_create_new_project(self):
        """
        Check if special manager method can create a project
        """
        datetime_creation = timezone.now()
        vals = {'name' : 'Projet test',
        'description' : 'Projet créé via test',
        'creation_date' : datetime_creation,
        'creator' : self.user1}

        Project.objects.create_new_project(vals)
        projects = Project.objects.filter(**{
            'name' : 'Projet test',
            'description' : 'Projet créé via test',
            'creator' : self.user1})
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].name, 'Projet test')
        self.assertEqual(projects[0].description, 'Projet créé via test')
        self.assertEqual(projects[0].creation_date, datetime_creation.astimezone(timezone.utc))
        self.assertEqual(projects[0].creator, self.user1)
    
    def test_creator_is_dev_on_new_project(self):
        """
        Check if special manager method create good relationship between user creating project and project
        """
        datetime_creation = timezone.now()
        vals = {'name' : 'Projet test',
        'description' : 'Projet créé via test',
        'creation_date' : datetime_creation,
        'creator' : self.user1}

        self.assertEqual(len(UserProject.objects.filter(user_role=self.dev_role,user=self.user1)), 0)
        Project.objects.create_new_project(vals)
        project = Project.objects.filter(**{'name' : 'Projet test',
        'description' : 'Projet créé via test',
        'creator' : self.user1})[0]
        self.assertEqual(len(UserProject.objects.filter(project=project,user_role=self.dev_role,user=self.user1)), 1)

    def test_project_already_exists_for_creator_returns_false_if_no_project(self):
        """
        Check if method returns False if there is no project already created and when the project is created,
        then returns True
        """
        
        project_name = 'Projet test'
        self.assertEqual(Project.objects.project_already_exists_for_creator(self.user1, project_name), False)
        Project.objects.create(**{
            'name': project_name,
            'creator': self.user1,
            'description':'test'
        })
        self.assertEqual(Project.objects.project_already_exists_for_creator(self.user1, project_name), True)

    def test_modify_name_modifies_name_of_project(self):
        project1 = Project.objects.create(**{
            'name': 'projet test',
            'creator': self.user1,
        })
        new_name = 'Nouveau nom projet'
        project1.modify_name(new_name)
        self.assertEqual(project1.name, new_name)

    def test_repr_of_project_is_his_name(self):
        project1 = Project.objects.create(**{
            'name': 'projet test',
            'creator': self.user1,
        })
        self.assertEqual(str(project1), project1.name)

    def test_modify_description_modifies_project_description(self):
        first_description = 'description initiale'
        project1 = Project.objects.create(**{
            'name': 'projet test',
            'creator': self.user1,
            'description': first_description
        })
        self.assertEqual(project1.description, first_description)
        new_description = "Nouvelle description" 
        project1.modify_description(new_description)
        self.assertEqual(project1.description, new_description)
    
    def test_new_invitation_is_created_when_call_send_invitation_to_project(self):
        before_invitations = Invitation.objects.filter(
            project=self.project_test,
            user=self.user2,
            user_role=self.dev_role,
            inviting_user=self.user1)
        self.assertEqual(len(before_invitations), 0)
        self.project_test.send_invitation_to_project('jean@test.com', 'DEV', self.user1)
        after_invitations = Invitation.objects.filter(
            project=self.project_test,
            user=self.user2,
            user_role=self.dev_role,
            inviting_user=self.user1)
        self.assertEqual(len(after_invitations), 1)

    def test_if_delete_users_on_project_deletes_users(self):
        user_role = UserProject.objects.create(**{
            'project': self.project_test,
            'user': self.user1,
            'user_role': self.dev_role
        })
        self.assertEqual(len(self.project_test.userproject_set.all()), 1)
        self.project_test.delete_users_on_project([user_role.id])
        self.assertEqual(len(self.project_test.userproject_set.all()), 0)

    @mock.patch('django.core.files.storage.FileSystemStorage.save')
    def test_add_files_to_project_adds_translations_files_to_project(self, mock_save):
        mock_save.return_value = 'fr_test.po'
        test_file = io.BytesIO(b'Translation File \n Module belcco')
        in_memory_test_file = InMemoryUploadedFile(
            name='fr_test.po',
            file=test_file,
            field_name=None,
            size=None,
            charset=None,
            content_type=None
        )
        files = [{
            'lang': 'fr',
            'template': False,
            'file': in_memory_test_file
        }]
        
        self.assertEqual(len(self.project_test.translation_files.all()), 0)
        self.project_test.add_files_to_project(files)
        self.assertEqual(len(self.project_test.translation_files.all()), 1)
        self.assertEqual(self.project_test.translation_files.all()[0].name,'fr_test.po')

    
    def test_send_invitation_to_project_create_new_invitation(self):

        #import pdb; pdb.set_trace()
        self.assertEqual(len(self.project_test.invitations.all()), 0)
        self.project_test.send_invitation_to_project('jean@test.com', 'DEV', self.user1)
        self.assertEqual(len(self.project_test.invitations.all()), 1)
    
    @mock.patch('translations.models.translation_file.logger.error')
    @mock.patch('django.core.files.storage.FileSystemStorage.save')
    def test_delete_files_of_project_deletes_files(self, mock_save, mock_error):
        mock_save.return_value = 'fr_test.po'
        test_file = in_memory_test_file = InMemoryUploadedFile(
            name='fr_test.po',
            file=io.BytesIO(b'test'),
            field_name=None,
            size=None,
            charset=None,
            content_type=None
        )
        new_file = TranslationFile.objects.create(name='fichier test',
                                        project=self.project_test,
                                        translated_language='fr',
                                        original_file=test_file)
        
        self.assertEqual(len(self.project_test.translation_files.all()), 1)
        self.project_test.delete_files_of_project([new_file.id])
        self.assertEqual(len(self.project_test.translation_files.all()), 0)

    
    def test_from_invitation_to_project_transforms_invitation_into_project(self):
        new_invitation = Invitation.objects.create(
            project=self.project_test,
            user=self.user2,
            user_role=self.dev_role,
            accepted=True,
            inviting_user=self.user1
        )

        self.assertEqual(len(self.project_test.userproject_set.all()), 0)
        new_invitation.from_invitation_to_project()
        self.assertEqual(len(self.project_test.userproject_set.all()), 1)
        self.assertEqual(self.project_test.userproject_set.all()[0].user_role, self.dev_role)
        self.assertEqual(self.project_test.userproject_set.all()[0].user, self.user2)
        self.assertEqual(self.project_test.userproject_set.all()[0].project, self.project_test)

    def test_modify_user_role_modifies_role(self):
        new_user_project = UserProject.objects.create(
            project=self.project_test,
            user=self.user2,
            user_role=self.dev_role
        )
        tra_role = Role.objects.create(name="TRA")
        self.assertEqual(new_user_project.user_role, self.dev_role)
        new_user_project.modify_user_role(tra_role.id)
        self.assertEqual(new_user_project.user_role, tra_role)






class ProjectViewTest(TestCase):
    """
    This class contains tests of views of 'projects' application
    """

    def setUp(self):
        """
        This function is executed each time a new test function is executed
        """
        self.client = Client()
        self.user1 = User.objects.create_user(
            username="Michel", password="1234", email="test@test.com")
        self.user2 = User.objects.create_user(
            username="Jean", password="1234", email="jean@test.com")
        
        self.project_test = Project.objects.create(**{
            'name': 'projet 1',
            'description': 'description 1',
            'creator': self.user1})
        self.dev_role = Role.objects.create(name="DEV")
        UserProject.objects.create(
            project=self.project_test,
            user=self.user1,
            user_role=self.dev_role)

    def test_view_200_when_asking_projects_list_view_connected(self):
        self.client.login(email='test@test.com', password='1234')
        response = self.client.get('/project/list')
        self.assertEqual(response.status_code, 200)

    def test_view_302_when_asking_projects_list_view_and_not_connected(self):
        response = self.client.get('/project/list')
        self.assertEqual(response.status_code, 302)

    def test_view_200_when_asking_invitation_list_view_connected(self):
        self.client.login(email='test@test.com', password='1234')
        response = self.client.get('/project/invitations')
        self.assertEqual(response.status_code, 200)

    def test_view_302_when_asking_invitation_list_view_not_connected(self):
        response = self.client.get('/project/invitations')
        self.assertEqual(response.status_code, 302)
    
    def test_view_create_project_creates_new_project(self):
        self.client.login(email='test@test.com', password='1234')
        self.assertEqual(len(Project.objects.filter(name='project créé depuis test')), 0)
        response = self.client.post('/project/create', {
            'name': 'project créé depuis test',
            'description': 'project créé depuis un test',
            'initial-creation_date': timezone.now()})
        self.assertEqual(len(Project.objects.filter(name='project créé depuis test')), 1)
    
    def test_views_verification_project_name_returns_false(self):
        self.client.login(email='test@test.com', password='1234')
        response = self.client.post('/project/project_exists', {'project_name': 'test nouveau project'})
        self.assertEqual(response.json()['project_exists'], False)

    def test_views_verification_project_name_returns_true(self):
        self.client.login(email='test@test.com', password='1234')
        response = self.client.post('/project/project_exists', {'project_name': 'projet 1'})
        self.assertEqual(response.json()['project_exists'], True)

    def test_view_from_invitation_to_project_create_new_project(self):
        self.client.login(email='test@test.com', password='1234')
        invit = Invitation.objects.create(
            project=self.project_test,
            user=self.user2,
            inviting_user=self.user1,
            user_role=self.dev_role,
        )
        self.assertEqual(len(UserProject.objects.filter(user=self.user2)), 0)
        response = self.client.post('/project/invitation/to-project', {'invitation_id': invit.id})
        invit.refresh_from_db()
        self.assertEqual(invit.accepted, True)
        self.assertEqual(len(UserProject.objects.filter(user=self.user2)), 1)

    def test_invitation_refused_refuses_invitation(self):
        self.client.login(email='test@test.com', password='1234')
        invit = Invitation.objects.create(
            project=self.project_test,
            user=self.user2,
            inviting_user=self.user1,
            user_role=self.dev_role,
        )
        self.assertEqual(invit.accepted, None)
        response = self.client.post('/project/invitation/refused', {'invitation_id': invit.id})
        invit.refresh_from_db()
        self.assertEqual(invit.accepted, False)
    
    def test_detail_project_redirects_if_user_not_assigned_to_project(self):
        self.client.login(email='jean@test.com', password='1234')
        response = self.client.get(f'/project/{self.project_test.id}/details')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/home')

    def test_detail_project_display_details_if_user_is_assigned_to_project(self):
        self.client.login(email='test@test.com', password='1234') # assigned user
        response = self.client.get(f'/project/{self.project_test.id}/details')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([t.name for t in response.templates], ['projects/project_general_infos.html','projects/base_project.html','base.html'])

    def test_detail_project_modifications_redirects_if_user_not_assigned_to_project(self):
        self.client.login(email='jean@test.com', password='1234')
        response = self.client.get(f'/project/{self.project_test.id}/details/modifications')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/home')

    def test_detail_project_modifications_display_details_if_user_is_assigned_to_project(self):
        self.client.login(email='test@test.com', password='1234') # assigned user
        response = self.client.get(f'/project/{self.project_test.id}/details/modifications')
        self.assertEqual(response.status_code, 200)
        self.assertIn('projects/project_general_infos.html', [t.name for t in response.templates])

    @mock.patch('projects.views.Project.objects.get')
    @mock.patch('projects.views.organise_datas')
    @mock.patch('projects.models.Project.update_project')
    def test_view_modify_project_returns_true_if_everything_ok(self, mock_update_project, mock_organise, mock_get):
        self.client.login(email='test@test.com', password='1234')
        #breakpoint()
        mock_organise.return_value = {'infos_user': {'project':{'id': None}}}
        response = self.client.post(f'/project/{self.project_test.id}/modify_project', {})
        self.assertEqual(response.json()['success'], True)

    def test_check_if_users_can_be_added_to_project_returns_true(self):
        response = self.client.post('/project/users_exists', {'datas': ""})
        self.assertEqual(response.json()['success'], True)

        

        
        

