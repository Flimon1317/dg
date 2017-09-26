import os.path
import dg.settings
import unicodecsv as csv

from geographies.models import Village, Block, District, State
from people.models import PersonGroup, Person
from coco.models import CocoUser

ERROR = 0 #variable to identify if any error occurs in uploaded file
ERROR_FILENAMES = [] #error files to be zipped for download
SUCCESS_FILENAMES = [] #success files to be zipped for download


def upload_personal_data(file, user_id, block_id):

    file = os.path.join(dg.settings.MEDIA_ROOT, file)

    csvfile = open(file, 'rb')
    rows = csv.DictReader(csvfile)

    #check required fields
    req_field = ['Village_Name', 'Shg_Name', 'Member_Name', 'Member_Surname',
                 'Husband_Father_Name', 'Husband_Father_Surname','Gender(M/F)']

    optional_field = ['Age','Phone_Number']

    for row in rows:
        if set(row.keys()) >= set(req_field):
            execute_personal_upload(file, user_id, block_id)
            break
        else:
            return False
    return True

def upload_geographical_data(file, user_id, state_id):

    file = os.path.join(dg.settings.MEDIA_ROOT, file)

    csvfile = open(file, 'rb')
    rows = csv.DictReader(csvfile)

    #check required fields
    req_field = ['District_Name', 'Block_Name', 'Village_Name',]

    for row in rows:
        if set(row.keys()) >= set(req_field):
            execute_geographical_upload(file, user_id, state_id)
            break
        else:
            return False
    return True


def execute_personal_upload(file, user_id, block_id):
    global ERROR

    user_id = CocoUser.objects.get(user__id=user_id)
    block_id = Block.objects.get(id=block_id)

    file_name = str(os.path.splitext(file)[0])
    file_name_list = str(os.path.splitext(file)[0].split('/')[-1])

    village_errors_file = open(file_name + '_errors_village.csv', 'wb')
    wrtr = csv.writer(village_errors_file, delimiter=',', quotechar='"')
    wrtr.writerow(["Entry No.", "Village Name", "Error"])

    village_success_file = open(file_name + '_success_village.csv', 'wb')
    wrtr_success = csv.writer(village_success_file, delimiter=',', quotechar='"')
    wrtr_success.writerow(["Entry No.", "Village Name"])

    csvfile = open(file, 'rb')
    rows_villages = csv.DictReader(csvfile)

    village_querry_set = Village.objects.values_list('village_name','id').filter(block_id=block_id.id)
    village_map = dict(village_querry_set)
    i = 0
    for row in rows_villages:
        if unicode(row['Village_Name']) not in village_map:
            try:
                village = Village(user_created_id=user_id.id, 
                                  village_name=unicode(row['Village_Name']),
                                  block_id=block_id.id)
                village.save()
                village_map[unicode(row['Village_Name'])] = village.id
                wrtr_success.writerow([i, unicode(row['Village_Name'])])
                village_success_file.flush()

            except Exception as e:
                ERROR += 1
                wrtr.writerow([i, unicode(row['Village_Name']), e])
                village_errors_file.flush()

    village_success_file.close()
    village_errors_file.close()

    ERROR_FILENAMES.append(file_name_list + '_errors_village.csv')
    SUCCESS_FILENAMES.append(file_name_list + '_success_village.csv')

    group_errors_file = open(file_name + '_errors_group.csv', 'wb')
    wrtr = csv.writer(group_errors_file, delimiter=',', quotechar='"')
    wrtr.writerow(["Entry No.", "Shg Name", "Error"])

    group_success_file = open(file_name + '_success_group.csv', 'wb')
    wrtr_success = csv.writer(group_success_file, delimiter=',', quotechar='"')
    wrtr_success.writerow(["Entry No.", "Shg Name"])

    csvfile = open(file, 'rb')
    rows_groups = csv.DictReader(csvfile)

    group_querry_set = PersonGroup.objects.values_list('group_name', 'id')
    group_map = dict(group_querry_set)

    i = 0
    for row in rows_groups:
        if unicode(row['Shg_Name']) + unicode(row['Village_Name']) not in group_map:
            i = i + 1
            try:
                group = PersonGroup(user_created_id=user_id.id,
                                    partner_id=user_id.partner.id,
                                    group_name=row['Shg_Name'],
                                    village_id=village_map[unicode(row['Village_Name'])])
                group.save()
                group_map[row['Shg_Name'] + unicode(row['Village_Name'])] = group.id
                wrtr_success.writerow([i, row['Shg_Name']])
                group_success_file.flush()

            except Exception as e:
                ERROR += 1
                wrtr.writerow([i, row['Shg_Name'], e] )
            group_errors_file.flush()

    group_errors_file.close()
    group_success_file.close()

    ERROR_FILENAMES.append(file_name_list + '_errors_group.csv')
    SUCCESS_FILENAMES.append(file_name_list + '_success_group.csv')

    person_errors_file = open(file_name + '_errors_person.csv', 'wb')
    wrtr = csv.writer(person_errors_file, delimiter=',', quotechar='"')
    wrtr.writerow(["Entry No.", "Person Name", "Error"])

    person_success_file = open(file_name + '_success_person.csv', 'wb')
    wrtr_success = csv.writer(person_success_file, delimiter=',', quotechar='"')
    wrtr_success.writerow(["Entry No.", "Person Name"])

    csvfile = open(file, 'rb')
    rows_persons = csv.DictReader(csvfile)

    i = 0
    for row in rows_persons:
        i = i + 1
        try:
            person_name = ' '.join([unicode(row['Member_Name']), unicode(row['Member_Surname'])])
            father_name = ' '.join([unicode(row['Husband_Father_Name']),
                                    unicode(row['Husband_Father_Surname'])])
            gender = str(row['Gender(M/F)'])
            if (row['Age'] == ''):
                age = None
            else:
                age = float(row['Age'])
   
            if (str(row['Phone_Number']) == ''):
                phone_number = str('')
            else:
                phone_number = str(row['Phone_Number'])
            
            person = Person(user_created_id=user_id.id,
                            partner_id=user_id.partner.id,
                            person_name=person_name,
                            father_name=father_name,
                            village_id=village_map[unicode(row['Village_Name'])],
                            group_id=group_map[row['Shg_Name'] + unicode(row['Village_Name'])],
                            gender=gender,
                            age = age,
                            phone_no = phone_number
                            )
            person.save()
            wrtr_success.writerow([i, person_name])
            person_success_file.flush()
        except Exception as e:
            ERROR += 1
            wrtr.writerow([i, person_name, e])
        person_errors_file.flush()

    person_errors_file.close()
    person_success_file.close()
    ERROR_FILENAMES.append(file_name_list + '_errors_person.csv')
    SUCCESS_FILENAMES.append(file_name_list + '_success_person.csv')

def execute_geographical_upload(file, user_id, state_id):
    global ERROR

    user_id = CocoUser.objects.get(user__id=user_id)
    state_id = State.objects.get(id=state_id)

    file_name = str(os.path.splitext(file)[0])
    file_name_list = str(os.path.splitext(file)[0].split('/')[-1])

    district_errors_file = open(file_name + '_errors_district.csv', 'wb')
    wrtr = csv.writer(district_errors_file, delimiter=',', quotechar='"')
    wrtr.writerow(["Entry No.", "District Name", "Error"])

    district_success_file = open(file_name + '_success_district.csv', 'wb')
    wrtr_success = csv.writer(district_success_file, delimiter=',', quotechar='"')
    wrtr_success.writerow(["Entry No.", "District Name"])

    csvfile = open(file, 'rb')
    rows_District = csv.DictReader(csvfile)

    district_querry_set = District.objects.values_list('district_name','id').filter(state_id=state_id.id)
    district_map = dict(district_querry_set)
    i = 0
    for row in rows_District:
        if unicode(row['District_Name']) not in district_map:
            i = i + 1
            try:
                district = District(user_created_id=user_id.id, 
                                  District_name=unicode(row['District_Name']),
                                  state_id=state_id.id)
                district.save()
                district_map[unicode(row['District_Name'])] = district.id
                wrtr_success.writerow([i, unicode(row['District_Name'])])
                district_success_file.flush()

            except Exception as e:
                ERROR += 1
                wrtr.writerow([i, unicode(row['District_Name']), e])
                district_errors_file.flush()

    district_success_file.close()
    district_errors_file.close()

    ERROR_FILENAMES.append(file_name_list + '_errors_district.csv')
    SUCCESS_FILENAMES.append(file_name_list + '_success_district.csv')

    group_errors_file = open(file_name + '_errors_group.csv', 'wb')
    wrtr = csv.writer(group_errors_file, delimiter=',', quotechar='"')
    wrtr.writerow(["Entry No.", "Block Name", "Error"])

    group_success_file = open(file_name + '_success_group.csv', 'wb')
    wrtr_success = csv.writer(group_success_file, delimiter=',', quotechar='"')
    wrtr_success.writerow(["Entry No.", "Block Name"])

    csvfile = open(file, 'rb')
    rows_groups = csv.DictReader(csvfile)

    group_querry_set = PersonGroup.objects.values_list('group_name', 'id')
    group_map = dict(group_querry_set)

    i = 0
    for row in rows_groups:
        if unicode(row['District_Name']) + unicode(row['Block_Name']) not in group_map:
            i = i + 1
            try:
                group = PersonGroup(user_created_id=user_id.id,
                                    partner_id=user_id.partner.id,
                                    group_name=row['Block_Name'],
                                    block_id=block_map[unicode(row['block_Name'])])
                group.save()
                group_map[row['District_Name'] + unicode(row['block_Name'])] = group.id
                wrtr_success.writerow([i, row['District_Name']])
                group_success_file.flush()
            except Exception as e:
                ERROR += 1
                wrtr.writerow([i, row['District_Name'], e] )
            group_errors_file.flush()

    group_errors_file.close()
    group_success_file.close()

    ERROR_FILENAMES.append(file_name_list + '_errors_group.csv')
    SUCCESS_FILENAMES.append(file_name_list + '_success_group.csv')

    group_errors_file = open(file_name + '_errors_group.csv', 'wb')
    wrtr = csv.writer(group_errors_file, delimiter=',', quotechar='"')
    wrtr.writerow(["Entry No.", "Village Name", "Error"])

    group_success_file = open(file_name + '_success_group.csv', 'wb')
    wrtr_success = csv.writer(group_success_file, delimiter=',', quotechar='"')
    wrtr_success.writerow(["Entry No.", "Village Name"])

    csvfile = open(file, 'rb')
    rows_groups = csv.DictReader(csvfile)

    group_querry_set = PersonGroup.objects.values_list('group_name', 'id')
    group_map = dict(group_querry_set)

    i = 0
    for row in rows_groups:
        if unicode(row['Block_Name']) + unicode(row['Village_Name']) not in group_map:
            i = i + 1
            try:
                group = PersonGroup(user_created_id=user_id.id,
                                    partner_id=user_id.partner.id,
                                    group_name=row['Block_Name'],
                                    village_id=village_map[unicode(row['village_Name'])])
                group.save()
                group_map[row['Block_Name'] + unicode(row['village_Name'])] = group.id
                wrtr_success.writerow([i, row['Block_Name']])
                group_success_file.flush()
            except Exception as e:
                ERROR += 1
                wrtr.writerow([i, row['Block_Name'], e] )
            group_errors_file.flush()

    group_errors_file.close()
    group_success_file.close()

    ERROR_FILENAMES.append(file_name_list + '_errors_group.csv')
    SUCCESS_FILENAMES.append(file_name_list + '_success_group.csv')


