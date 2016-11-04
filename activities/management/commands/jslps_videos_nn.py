import urllib2
import unicodecsv as csv
from datetime import * 
import xml.etree.ElementTree as ET
from django.core.management.base import BaseCommand
from geographies.models import *
from people.models import *
from programs.models import *
from videos.models import *

class Command(BaseCommand):
	def handle(self, *args, **options):
		#saving videos
		url = urllib2.urlopen('http://webservicesri.swalekha.in/Service.asmx/GetExportVedioMasterData?pUsername=admin&pPassword=JSLPSSRI')
		contents = url.read()
		xml_file = open("jslps_data_integration_files/video.xml", 'w')
		xml_file.write(contents)
		xml_file.close()

		partner = Partner.objects.get(id = 24)
		csv_file = open('jslps_data_integration_files/videos_error.csv', 'wb')
		wtr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
		tree = ET.parse('jslps_data_integration_files/video.xml')
		root = tree.getroot()
		for c in root.findall('VedioMasterData'):
			vdc = c.find('VideoID').text
			vn = c.find('VideoTitle').text
			vt = int(c.find('VideoType').text)
			if c.find('Category') is not None: 
				cg = int(c.find('Category').text)
			else:
				cg = None
			if c.find('SubCategory') is not None: 
				scg = int(c.find('SubCategory').text)
			else:
				scg = None
			if c.find('Practice') is not None: 
				vp = int(c.find('Practice').text)
			else:
				vp = None
			if c.find('YouTubeID') is not None: 
				yid = c.find('YouTubeID').text
			else:
				yid = ''
			pd = datetime.strptime(c.find('ProductionDate').text, '%d/%m/%Y')
			if c.find('ApprovalDt') is not None:
				ad = datetime.strptime(c.find('ApprovalDt').text, '%d/%m/%Y')
			else:
				ad = None
			#sd = datetime.strptime(c.find('StartDt').text, '%d/%m/%Y')
			#ed = datetime.strptime(c.find('EndDt').text, '%d/%m/%Y')
			ln = int(c.find('Video_Language').text)
			if (ln == 2):
				ln = 18
			elif (ln ==3):
				ln =10
			if c.find('Benefit') is not None:
				benefit = unicode(c.find('Benefit').text)
			else:
				benefit = ''
			vc = c.find('VillageCode').text
			pro_team = c.find('ProductionTeam').text.split(',')
			#dc = c.find('DistrictCode').text
			#bc = c.find('BlockCode').text
			#fc = int(c.find('Facililator').text)
			#co = int(c.find('Camera_Operator').text)
			#fr = map(int, c.find('MemberIDList').text.split(','))
			#act= c.find('Actors').text
			#sf = int(c.find('Suitable_For').text)
			
			error = 0
			try:
				village = JSLPS_Village.objects.get(village_code = vc)
				language = Language.objects.get(id = ln)
				try:
					facililator = JSLPS_Animator.objects.get(animator_code = pro_team[0])
				except JSLPS_Animator.DoesNotExist as e:
					facililator = JSLPS_Animator.objects.get(animator_code = str(4))
				try:
					camera_operator = JSLPS_Animator.objects.get(animator_code = pro_team[1])
				except JSLPS_Animator.DoesNotExist as e:
					camera_operator = JSLPS_Animator.objects.get(animator_code = str(4))
				try:
					category = Category.objects.get(id = cg)
				except Category.DoesNotExist as e:
					category = None
				try:
					subcategory = SubCategory.objects.get(id = scg)
				except SubCategory.DoesNotExist as e:
					subcategory = None
				try:
					videopractice = VideoPractice.objects.get(id = vp)
				except VideoPractice.DoesNotExist as e:
					videopractice = None
				'''
				farmer_list = []
				for i in fr:
					try:
						fr = JSLPS_Person.objects.get(person_code = str(i))
						farmer_list.append(fr.person)
					except JSLPS_Person.DoesNotExist as e:
						fr = JSLPS_Person.objects.get(person_code = str(630))
						farmer_list.append(fr.person)
				'''

			except (JSLPS_Village.DoesNotExist, Language.DoesNotExist) as e:
				print e
				wtr.writerow(['village',vc,'title', vn, e])
				error = 1

			if(error == 0):
				video_set = dict(Video.objects.filter(village_id = village.Village.id).values_list('title','village'))
				video_db = []
				video_xml = str(vn)+str(village.Village.id)
				for key, value in video_set.iteritems():
					name = str(key)+str(value)
					video_db.append(name)
				if video_xml not in video_db:
					try:
						vid = Video(title = vn,
									video_type = vt,
									language = language,
									benefit = benefit,
									production_date = pd,
									village_id = village.Village.id,
									partner = partner,
									approval_date=ad,
									youtubeid=yid,
									category=category,
									subcategory=subcategory,
									videopractice=videopractice
									)
						vid.save()
						print "video saved"
					except Exception as e:
						print vdc, e
						wtr.writerow(['video save', vdc, e])

					
					try:
						vid = Video.objects.get(title = vn, village_id=village.Village.id, partner_id=partner.id)
						vid.production_team.add(facililator)
						vid.save()
						vid.production_team.add(camera_operator)
						vid.save()
						print "farmer shown saved"
					except Exception as e:
						wtr.writerow(['production team save', e])

					video_added = []
					video = None
					try:
						video = Video.objects.filter(title = vn, village_id = village.Village.id, partner_id=partner.id).get()
						video_added = JSLPS_Video.objects.values_list('vc', flat= True)
						#video_added = [i[0] for i in video_added]
					except Exception as e:
						print e
					try:	
						if vdc not in video_added:
							vj = JSLPS_Video(vc = vdc,
										video = video)
							vj.save()
					except Exception as e:
						print vdc, e
						wtr.writerow(['JSLPS Video save', vdc, e])

		#saving non-negotiables
		url = urllib2.urlopen('http://webservicesri.swalekha.in/Service.asmx/GetExportVedioNon_NegotiableMasterData?pUsername=admin&pPassword=JSLPSSRI')
		contents = url.read()
		xml_file = open("jslps_data_integration_files/nn.xml", 'w')
		xml_file.write(contents)
		xml_file.close()

		partner = Partner.objects.get(id = 24)
		tree = ET.parse('jslps_data_integration_files/nn.xml')
		root = tree.getroot()

		for c in root.findall('VedioNon_NegotiableMasterData'):
			nn_c = c.find('Non_NegotiablesID').text
			vdc = int(c.find('VideoId').text)
			nn_n = c.find('Non_NegotiablesName').text
			vr = c.find('Verification').text
			if vr == 'false':
				vr = False
			else:
				vr = True
			error = 0
			try:
				video = JSLPS_Video.objects.get(vc = vdc)
			except JSLPS_Video.DoesNotExist as e:
				error = 1
			if error == 0:
				try:
					nn = NonNegotiable(video_id = video.video_id,
									non_negotiable = nn_n,
									physically_verifiable = vr)
					nn.save()
				except Exception as e:
					print e
					wtr.writerow(['Non nego', nn_c,'video',vdc, e])
