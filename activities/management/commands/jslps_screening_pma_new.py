import urllib2
import unicodecsv as csv
from datetime import datetime 
import xml.etree.ElementTree as ET
from django.core.management.base import BaseCommand
from geographies.models import *
from people.models import *
from programs.models import *
from videos.models import *
from activities.models import *
import jslps_data_integration as jslps

class Command(BaseCommand):
	def handle(self, *args, **options):
		
		partner = Partner.objects.get(id = 24)
		url = urllib2.urlopen('http://webservicesri.swalekha.in/Service.asmx/GetExportVedioScreeingMasterData?pUsername=admin&pPassword=JSLPSSRI')
		contents = url.read()
		xml_file = open("jslps_data_integration_files/screening.xml", 'w')
		xml_file.write(contents)
		xml_file.close()

		csv_file = open('jslps_data_integration_files/screening_error.csv', 'wb')
		wtr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
		tree = ET.parse('jslps_data_integration_files/screening.xml')
		root = tree.getroot()
		for c in root.findall('VedioScreeingMasterData'):
			sc = c.find('VDO_ID').text
			vc = c.find('VillageCode').text
			ac = c.find('AKMCode').text
			sd = datetime.datetime.strptime(c.find('ScreeningDate').text, '%d/%m/%Y')
			st = datetime.datetime.strptime(c.find('start_time').text, '%H:%M:%S')
			#et = datetime.datetime.strptime(c.find('End_time').text, '%H:%M:%S')
			try:
				vdc = map(int, c.find('Video').text.split(','))
			except Exception as e:
				vdc = []
				wtr.writerow(['Can not save screening without video', sc, "video not found"])
				continue
			try:
				gc = map(int, c.find('GroupCode').text.split(','))
			except Exception as e:
				gc = []

			animator = JSLPS_Animator.objects.filter(animator_code = ac)
			if len(animator) == 0:
				wtr.writerow(['Can not save screening without animator', sc, "animator not found"])
				continue
			else:
				animator = animator[0]

			village = JSLPS_Village.objects.filter(village_code = vc)
			if len(village) == 0:
				wtr.writerow(['Can not save screening without village', sc, "village not found"])
				continue
			else:
				village = village[0]

			groups = []
			videos = []
			for v in vdc:
				vid = JSLPS_Video.objects.filter(vc = v)
				if len(vid) > 0:
					videos.append(vid[0].video)
			if len(videos) == 0:
				wtr.writerow(['Can not save screening without video', sc, "video not found"])
				continue
			for g in gc:
				grp = JSLPS_Persongroup.objects.filter(group_code = g)
				if len(grp) > 0:
					groups.append(grp[0].group)

			try:
				scr_already_exist = Screening.objects.filter(date = sd,
									start_time = st,
									village = village.Village,
									animator = animator.animator,
									partner = partner)
				if len(scr_already_exist) == 0:
					screening = Screening(date = sd,
										start_time = st,
										village = village.Village,
										animator = animator.animator,
										partner = partner)
					screening.save()
					jslps.new_count += 1
				else:
					screening = None
					jslps.duplicate_count += 1
			except Exception as e:
				screening = None
				if "Duplicate entry" not in str(e):
					jslps.other_error_count += 1
					wtr.writerow(['Screening save error', sc, e])
				else:
					jslps.duplicate_count += 1

			if screening != None:
				for i in groups:
					screening.farmer_groups_targeted.add(i)
					screening.save()
				for i in videos:
					screening.videoes_screened.add(i)
					screening.save()
				jslps_screening_list = JSLPS_Screening.objects.filter(screenig_code=sc)
				if len(jslps_screening_list) == 0:
					jslps_screening = JSLPS_Screening(screenig_code=sc,screening=screening)
					jslps_screening.save()
				else:
					jslps_screening = jslps_screening_list[0]
					jslps_screening.screening = screening
					jslps_screening.save()
			else:
				screening_list = Screening.objects.filter(date = sd,
									start_time = st,
									village = village.Village,
									animator = animator.animator,
									partner = partner)
				if len(screening_list) != 0:
					screening = screening_list[0]
					for i in groups:
						screening.farmer_groups_targeted.add(i)
						screening.save()
					for i in videos:
						screening.videoes_screened.add(i)
						screening.save()
					jslps_screening_list = JSLPS_Screening.objects.filter(screenig_code=sc,screening=screening)
					if len(jslps_screening_list) == 0:
						jslps_screening = JSLPS_Screening(screenig_code=sc,screening=screening)
						jslps_screening.save()
					else:
						jslps_screening = jslps_screening_list[0]
						if jslps_screening.screening == None:
							jslps_screening.screening = screening
							jslps_screening.save()
				else:
					wtr.writerow(['Screening not saved and duplicate also not exist',sc, "not saved"])


		#saving pma
		url = urllib2.urlopen('http://webservicesri.swalekha.in/Service.asmx/GetExportVedioScreeingMemberData?pUsername=admin&pPassword=JSLPSSRI')
		contents = url.read()
		xml_file = open("jslps_data_integration_files/pma.xml", 'w')
		xml_file.write(contents)
		xml_file.close()

		csv_file = open('jslps_data_integration_files/pma_error.csv', 'wb')
		wtrr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
		tree = ET.parse('jslps_data_integration_files/pma.xml')
		root = tree.getroot()

		for c in root.findall('VedioScreeingMemberData'):
			sc = c.find('VDO_ID').text
			pc = c.find('MemberId').text
			
			screening = JSLPS_Screening.objects.filter(screenig_code = sc)
			if len(screening) == 0:
				wtrr.writerow(['Screening not exist', sc, "Screening not found"])
				continue
			else:
				screening = screening[0]

			person = JSLPS_Person.objects.filter(person_code = pc)
			if len(person) == 0:
				wtrr.writerow(['person not exist', pc, "Person not found"])
				continue
			else:
				person = person[0]

			pma_already_exist = PersonMeetingAttendance.objects.filter(screening_id = screening.screening.id,person_id=person.person.id)
			if len(pma_already_exist) == 0:
				try:
					pma = PersonMeetingAttendance(screening = screening.screening,
													person = person.person)
					pma.save()
					jslps.new_count += 1
				except Exception as e:
					wtrr.writerow(['Error in saving attendance (scr_id=%s)'%(str(sc)), pc, e])
