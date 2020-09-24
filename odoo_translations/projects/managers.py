from django.db import models

class CustomProjectManager(models.Manager):
    def project_already_exists_for_creator(self, creator=None, name=None):
        if creator == None or name==None:
            # if creator or name is None, we return none
            return None
        # we retrieve all projects where user is the creator
        user_projects_creator = self.filter(creator=creator)
        for project in user_projects_creator:
            # if a project has the same name than the variable name, we return True, else False 
            if project.name == name:
                return True
        return False