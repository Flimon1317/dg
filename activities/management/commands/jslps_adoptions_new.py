import urllib2
import unicodecsv as csv
from datetime import datetime 
import xml.etree.ElementTree as ET
from django.core.management.base import BaseCommand
from people.models import *
from programs.models import *
from videos.models import *
from activities.models import *
import jslps_data_integration as jslps

class Command(BaseCommand):
	def handle(self, *args, **options):
		
		partner = Partner.objects.get(id = 24)
		animator = Animator.objects.get(id=1342)
		url = urllib2.urlopen('http://webservicesri.swalekha.in/Service.asmx/GetExportAdoptionData?pUsername=admin&pPassword=JSLPSSRI')
		contents = url.read()
		xml_file = open("jslps_data_integration_files/adoption.xml", 'w')
		xml_file.write(contents)
		xml_file.close()

		csv_file = open('jslps_data_integration_files/adoption_error.csv', 'wb')
		wtr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
		tree = ET.parse('jslps_data_integration_files/adoption.xml')
		root = tree.getroot()
		for c in root.findall('AdoptionData'):
			pc = c.find('MemberCode').text
			try:
				vc = c.find('Video').text
			except Exception as e:
				vc = 1
				#wtr.writerow(['video data missing (Member code ->)', pc, e])
				#jslps.other_error_count += 1
				#continue
			da = datetime.datetime.strptime(c.find('DOA').text, '%d/%m/%Y')
			de = datetime.datetime.strptime(c.find('DOE').text, '%d/%m/%Y')

			try:
				video = JSLPS_Video.objects.get(vc = vc)
			except Exception as e:
				vc = 1
				video = JSLPS_Video.objects.get(vc = vc)
				#wtr.writerow(['video not exist', vc, e])
				#continue
			
			person = JSLPS_Person.objects.filter(person_code = pc)
			if len(person) == 0:
				pc = 1
				person = JSLPS_Person.objects.filter(person_code = pc)
				person = person[0]
				#wtr.writerow(['person not exist', pc, "Person not found"])
				#continue
			else:
				person = person[0]
				
			try:
				pap = PersonAdoptPractice(person = person.person,
										  video = video.video,
										  date_of_adoption = da,
										  animator = animator,
										  partner = partner)
				pap.save()
				jslps.new_count += 1
			except Exception as e:
				if "Duplicate entry" not in str(e):
					jslps.other_error_count += 1
					wtr.writerow(['Adoption not saved (video code %s)'%(str(vc)), pc, e])
				else:
					jslps.duplicate_count += 1
