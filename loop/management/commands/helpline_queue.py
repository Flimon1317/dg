import time

from django.core.management.base import BaseCommand

from dg.settings import EXOTEL_ID, EXOTEL_TOKEN, EXOTEL_HELPLINE_NUMBER, NO_EXPERT_GREETING_APP_ID

from loop.models import HelplineExpert, HelplineIncoming, HelplineOutgoing
from loop.views import get_status, make_helpline_call

class Command(BaseCommand):

    def check_pending_or_not(self,incoming_call_id):
        incoming_call_obj = HelplineIncoming.objects.filter(id=incoming_call_id)
        if incoming_call_obj:
            incoming_call_obj = incoming_call_obj[0]
            # Check If Status of call is pending
            if incoming_call_obj.call_status == 0:
                # Fetch latest outgoing of respective Incoming
                latest_outgoing_of_incoming = HelplineOutgoing.objects.filter(incoming_call=incoming_call_obj).order_by('-id').values_list('call_id', flat=True)[:1]
                if len(latest_outgoing_of_incoming) != 0:
                    call_status = get_status(latest_outgoing_of_incoming[0])
                else: 
                    call_status = ''
                # Check If Pending call is already in-progress
                if call_status != '' and call_status['response_code'] == 200 and (call_status['status'] in ('ringing', 'in-progress')):
                        return ''
                return incoming_call_obj
            # If Status of call is not pending
            else:
                return ''
        # If Incoming Call object not found
        else:
            return ''

    def handle(self, *args, **options):
        expert_obj = HelplineExpert.objects.filter(expert_status=1)[:1]
        if expert_obj:
            expert_obj = expert_obj[0]
        else:
            #Log in file that no expert available
            pass
        pending_incoming_call_id = HelplineIncoming.objects.filter(call_status=0).order_by('id').values_list('id', flat=True)
        for ids in pending_incoming_call_id:
            incoming_call_obj = self.check_pending_or_not(ids)
            if incoming_call_obj:
                farmer_number = incoming_call_obj.from_number
                make_helpline_call(incoming_call_obj,expert_obj,farmer_number)
                time.sleep(120)