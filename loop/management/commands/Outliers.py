# coding=utf-8
import copy

__author__ = 'Lokesh'

from loop.sendmail import common_send_email
from loop.models import LoopUser
from loop.utils.emailers_support import date_setter
from django.core.management.base import BaseCommand
from loop.utils.emailers_support.queries import *
from loop.utils.emailers_support.excel_generator import *
from loop.config import *
from loop.utils.emailers_support.FarmerShareOutlierCompute import FarmerShareOutlier as FSOC
from loop.utils.emailers_support.TransportShareOutlierCompute import TransportCostOutlier as TSOC


class Command(BaseCommand):
    # parse arguments from command line
    def add_arguments(self, parser):
        #create mutually exclusive command line switches
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-fd',
                           dest='from_date',
                           default=None)

        group.add_argument('-nd',
                           dest='num_days',
                           default=None)

        parser.add_argument('-a',
                            dest='aggregator',
                            default='all')

        parser.add_argument('-td',
                            dest='to_date',
                            default=None)

    #generate the excel for the given command line arguments
    def handle(self, *args, **options):
        from_to_date = date_setter.set_from_to_date(options.get('from_date'), options.get('to_date'),
                                                    options.get('num_days'))
        email_file_list = []
        if options.get('aggregator') == 'all' or options.get('aggregator') == None:

            file_for_mail = self.file_creator_per_case(from_to_date, case='FarmerShare')
            email_file_list.append(file_for_mail)

            file_for_mail = self.file_creator_per_case(from_to_date, case='TransportCost')
            email_file_list.append(file_for_mail)

        else:
            print "Specific Aggregator case not handled"

        common_send_email("Farmer Share and Transport Cost Outliers", recipients=RECIPIENTS, files=email_file_list, bcc=[],
                          from_email='lokesh@digitalgreen.org', html="", text='Please find the attached sheet for farmer share outliers and Transport Cost outliers')


    def file_creator_per_case(self, from_to_date, case=''):

        if case == 'FarmerShare':
            workbook = create_workbook(header_dict_for_farmer_outlier['workbook_name'] % (
            MEDIA_ROOT, '', str(from_to_date[0]), str(from_to_date[1])))

            daily_a_m_farmerShare_query_result = onrun_query(daily_a_m_farmerShare_query)
            aggregator_wise_outliers = FSOC.data_Manipulator(daily_a_m_farmerShare_query_result, from_to_date)
            worksheet_name = {'All': 'Farmer Share Outliers_' + str(from_to_date[0]) + "_" + str(from_to_date[1])}
            file_to_send = header_dict_for_farmer_outlier['workbook_name'] % (
            MEDIA_ROOT, '', str(from_to_date[0]), str(from_to_date[1]))


        if case == 'TransportCost':
            workbook = create_workbook(header_dict_for_transport_outlier['workbook_name'] % (
            MEDIA_ROOT, '', str(from_to_date[0]), str(from_to_date[1])))

            daily_a_m_transportShare_query_result = onrun_query(daily_a_m_transport_share_query)
            aggregator_wise_outliers = TSOC.data_Manipulator(daily_a_m_transportShare_query_result, from_to_date)
            worksheet_name = {'All': 'Transport Cost Outliers_' + str(from_to_date[0]) + "_" + str(from_to_date[1])}
            file_to_send = header_dict_for_transport_outlier['workbook_name'] % (
            MEDIA_ROOT, '', str(from_to_date[0]), str(from_to_date[1]))

        # Position of All is first as a co-incidence I think.
        # Set correct column widths
        # workbook = create_workbook('Farmer Share Outliers.xlsx')
        # all_format = ['date_format']
        # all_format_created = create_format(all_format, workbook)


        table_properties = {'data': None, 'autofilter': False, 'banded_rows': False, 'style': 'Table Style Light 15',
                            'columns': header_dict_for_farmer_outlier['column_properties']}

        # for aggregator in aggregators:
        #     table_position_to_start = {'row': 2, 'col': 0}
        #     worksheet_name[aggregator.name_en] = header_dict_for_farmer_outlier['worksheet_name'] % (
        #     str(aggregator.name_en), str(from_to_date[0]), str(from_to_date[1]))

        table_position_to_start = {'row': 2, 'col': 0}
        create_xlsx(workbook, aggregator_wise_outliers, table_properties, table_position_to_start,
                    worksheet_name)

        return file_to_send