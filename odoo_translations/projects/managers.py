from django.db import models
from django.apps import apps

class CustomProjectManager(models.Manager):
    def project_already_exists_for_creator(self, current_user, project_name):
        for project in self.filter(creator=current_user):
            if project.name == project_name:
                return True
        return False
    def create_new_project(self, values):
        # we get the model this way to avoid problem of circular import
        Project = apps.get_model('projects', 'Project')
        # we create the project with values given to the method
        project = Project(**values)
        project.save()
        # we will create a link between user that create projet and project, he will get role DEV
        role  = apps.get_model('projects', 'Role').objects.filter(name="DEV")[0]
        UserProject = apps.get_model('projects', 'UserProject')
        user_project = UserProject(
            project = project,
            user = values['creator'],
            user_role = role
        )
        user_project.save()


