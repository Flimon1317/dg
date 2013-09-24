import os
from django.core.management.base import BaseCommand, CommandError
from django.db.models import get_model
from datetime import datetime, timedelta
from dg.settings import MEDIA_ROOT

from dimagi.models import CommCareProject, CommCareUser
from dimagi.scripts.userfile_functions import write_new_case


class Command(BaseCommand):
    args = '<commcare_project_name> <commcare_project_name> ...'
    help = '''Creates initial cases for a new CommCare Application. Prerequisites:
    (1) Create project in CommCare.
    (2) Enter project information through admin.
    (3) Create atleast one CommCare user for this project.
    (4) Enter user, project and village permissions, through admin.
    '''

    def handle(self, *args, **options):
        commcare_project_list = args
        for commcare_project_name in commcare_project_list:
            try:
                commcare_project = CommCareProject.objects.get(name=commcare_project_name)
            except CommCareProject.DoesNotExist:
                raise CommandError('CommCare Project "%s" not yet entered in the Database.' % commcare_project_name)
            
            last_update_time = datetime.now() - timedelta(days=1)
            villages = CommCareUser.objects.filter(project=commcare_project.id).values_list('assigned_villages', flat=True)
            ServerLog = get_model('dasboard','ServerLog')
            persons_list = ServerLog.objects.filter(entry_table='Person').filter(village__in=villages).filter(timestamp__gte=last_update_time)
            pma_list = ServerLog.objects.filter(entry_table='PersonMeetingAttendance').filter(village__in=villages).filter(timestamp__gte=last_update_time)
            
            case_update_list=[]
            case_close_list=[]
            for person in persons_list:
                if person.action == 0 or person.action ==1:
                    case_update_list.append(person.model_id)
                elif person.action == -1:
                    case_close_list.append(person.model_id) #this is not working for now
            
            case_videos_seen_update_list = []
            PersonMeetingAttendance = get_model('dashboard','PersonMeetingAttendance')
            for pma in pma_list:
                person_id = PersonMeetingAttendance.objects.get(id = pma.model_id).person.id
                if pma.action == 0 or pma.action ==1:
                    case_videos_seen_update_list.append(person_id)
            
            filename_newcases = os.path.join(MEDIA_ROOT, "dimagi", "updates", "%s_newcase.xls" % (commcare_project_name))
            filename_updatecases = os.path.join(MEDIA_ROOT, "dimagi", "updates", "%s_updatecase.xls" % (commcare_project_name))
            
                        
            write_new_case(case_update_list, filename_newcases)
            
            update_case(case_videos_seen_update_list, file_updatecases)
            
            try : 
                response_new = commcare_project.upload_case_file(filename_newcases)
                if response_new == 201 or response_new == 200:
                    self.stdout.write('Successfully created new cases for "%s"' % commcare_project_name)
                else:
                    self.stdout.write('Not uploaded but file ("%s") has been created in MEDIA_ROOT/dimagi/updates' % commcare_project_name)
            except Exception as ex:
                pass
            
            try : 
                response_update = commcare_project.upload_case_file(file_updatecases)
                if response_update == 201 or response_new == 200:
                    self.stdout.write('Successfully updated cases for "%s"' % commcare_project_name)
                else:
                    self.stdout.write('Not uploaded but file ("%s") has been created in MEDIA_ROOT/dimagi/updates' % commcare_project_name)
            except Exception as ex:
                pass
            
            for person_id in case_close_list:
                file_closecase = os.path.join(MEDIA_ROOT, "dimagi", "updates", "closing_forms", "%s.xls" % (person_id))
                close_case(person_id, file_closecase)
                try : 
                    response_closecase = commcare_project.upload_case_file(file_closecase)
                    if response_closecase == 201 or response_closecase == 200:
                        self.stdout.write('Successfully closed case for "%s"' % commcare_project_name)
                    else:
                        self.stdout.write('Not closed but file ("%s") has been created in MEDIA_ROOT/dimagi/closing_forms' % person_id)
                except Exception as ex:
                    pass
        
        commcare_project.last_updated_time = datetime.now()
        commcare_project.save()
    