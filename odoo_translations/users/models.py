from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
# Create your models here.

class User(AbstractUser):
    email = models.EmailField(max_length=80, unique=True)
    username = models.CharField(max_length=80, null=False, blank=False)
    USERNAME_FIELD="email"
    REQUIRED_FIELDS=['username']

    def __str__(self):
        return self.username + " <{}>".format(self.email)

    def has_rights_to_modify_project(self, project_to_check):
        """
        This method will check role of user on project
        if role == 'developer'
        else = not rights to modify
        """
        ROLES_WHO_CAN_WRITE = ['DEV']
        project = self.userproject_set.filter(project=project_to_check)
        if len(project) == 0:
            # if there is no project, user is not on project and cannot modify it
            return False
        if project[0].user_role is not None:
            # if there is a role for user on project
            if project[0].user_role.name in ROLES_WHO_CAN_WRITE:
                # if user has a role which allows him to write on project, return True
                return True
        return False
    
    def is_on_project(project_id):
        project = self.userproject_set.filter(project=project_id)
        is_on_project = True if len(project) > 0 else False
        return is_on_project

