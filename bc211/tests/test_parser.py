import unittest
import logging
import xml.etree.ElementTree as etree
from common.testhelpers.random_test_values import a_string

from bc211 import parser, dtos
from bc211.exceptions import MissingRequiredFieldXmlParseException

logging.disable(logging.ERROR)

REAL_211_DATA_SET = 'bc211/data/BC211_data_one_agency.xml'
MULTI_AGENCY__211_DATA_SET = 'bc211/data/BC211_data_excerpt.xml'
MINIMAL_211_DATA_SET = '''
<Source>
    <Agency>
        <Key>the agency key</Key>
        <Name>the agency name</Name>
        <AgencyDescription>the agency description</AgencyDescription>
        <URL>
            <Address>http://www.the-agency.org</Address>
        </URL>
        <Email>
            <Address>info@the-agency.org</Address>
        </Email>
        <Site>
            <Key>the site key</Key>
            <Name>the site name</Name>
            <SiteDescription>the site description</SiteDescription>
            <SpatialLocation>
                <Latitude>123.456</Latitude>
                <Longitude>-154.321</Longitude>
            </SpatialLocation>
            <SiteService>
                <Key>the service key</Key>
                <Name>the service name</Name>
                <Description>the service description</Description>
            </SiteService>
            <SiteService>
                <Key>the second service key</Key>
                <Name>the second service name</Name>
                <Description>the second service description</Description>
            </SiteService>
            <MailingAddress>
                <Line1>Line1</Line1>
                <Line2>Line2</Line2>
                <City>City</City>
                <Country>Country</Country>
                <State>State</State>
                <ZipCode>Code</ZipCode>
            </MailingAddress>
            <PhysicalAddress>
                <Line1>Line1</Line1>
                <City>City</City>
                <Country>Country</Country>
                <State>State</State>
                <ZipCode>Code</ZipCode>
            </PhysicalAddress>
        </Site>
        <Site>
            <Key>the second site key</Key>
            <Name>the second site name</Name>
            <SiteDescription>the second site description</SiteDescription>
            <SpatialLocation>
                <Latitude>123.456</Latitude>
                <Longitude>-154.321</Longitude>
            </SpatialLocation>
            <SiteService>
                <Key>the second site's service key</Key>
                <Name>the second site's service name</Name>
                <Description>the second site's service description</Description>
            </SiteService>
            <MailingAddress>
                <Line1>Line1</Line1>
                <Line2>Line2</Line2>
                <City>City</City>
                <Country>Country</Country>
                <State>State</State>
                <ZipCode>Code</ZipCode>
            </MailingAddress>
            <PhysicalAddress>
                <Line1>Line1</Line1>
                <City>City</City>
                <Country>Country</Country>
                <State>State</State>
                <ZipCode>Code</ZipCode>
            </PhysicalAddress>
        </Site>
    </Agency>
</Source>'''

class BC211ParserTests(unittest.TestCase):
    def test_parse_many_locations(self):
        file_open_for_reading = open(MULTI_AGENCY__211_DATA_SET, 'r')
        xml = file_open_for_reading.read()
        organizations = list(parser.parse(xml))
        locations_from_first_organization = list(organizations[0].locations)
        services_from_first_location = list(locations_from_first_organization[0].services)
        taxonomy_terms_from_first_service = list(services_from_first_location[0].taxonomy_terms)
        addresses_from_first_location = [
            locations_from_first_organization[0].physical_address,
            locations_from_first_organization[0].postal_address
        ]
        self.assertEqual(len(organizations), 16)
        self.assertEqual(len(locations_from_first_organization), 1)
        self.assertEqual(len(services_from_first_location), 1)
        self.assertEqual(len(taxonomy_terms_from_first_service), 27)
        self.assertEqual(len(addresses_from_first_location), 2)


class OrganizationParserTests(unittest.TestCase):
    def setUp(self):
        root = etree.fromstring(open(REAL_211_DATA_SET, 'r').read())
        self.from_real_data = parser.parse_agency(root.find('Agency'))

        root = etree.fromstring(MINIMAL_211_DATA_SET)
        self.from_minimal_data = parser.parse_agency(root.find('Agency'))

    def test_can_parse_id(self):
        self.assertEqual(self.from_real_data.id, '9487364')
        self.assertEqual(self.from_minimal_data.id, 'the agency key')

    def test_can_parse_name(self):
        self.assertEqual(self.from_real_data.name, 'Langley Child Development Centre')
        self.assertEqual(self.from_minimal_data.name, 'the agency name')

    def test_can_parse_description(self):
        self.assertEqual(self.from_real_data.description[:30], 'Provides inclusive, family-cen')
        self.assertEqual(self.from_minimal_data.description, 'the agency description')

    def test_can_parse_website(self):
        self.assertEqual(self.from_real_data.website, 'http://www.langleycdc.com')
        self.assertEqual(self.from_minimal_data.website, 'http://www.the-agency.org')

    def test_website_without_prefix_parsed_as_http(self):
        xml = self.data_set_with_website('www.the-agency.org')
        website = self.get_website_as_parsed(xml)
        self.assertEqual(website, 'http://www.the-agency.org')

    def test_website_with_http_prefix_parsed_as_http(self):
        xml = self.data_set_with_website('http://www.the-agency.org')
        website = self.get_website_as_parsed(xml)
        self.assertEqual(website, 'http://www.the-agency.org')

    def test_website_with_https_prefix_parsed_as_https(self):
        xml = self.data_set_with_website('https://www.the-agency.org')
        website = self.get_website_as_parsed(xml)
        self.assertEqual(website, 'https://www.the-agency.org')

    def data_set_with_website(self, website):
        return MINIMAL_211_DATA_SET.replace('http://www.the-agency.org', website)

    def get_website_as_parsed(self, xml):
        root = etree.fromstring(xml)
        organization = parser.parse_agency(root.find('Agency'))
        return organization.website

    def test_can_parse_email(self):
        self.assertEqual(self.from_real_data.email, 'info@langleycdc.com')
        self.assertEqual(self.from_minimal_data.email, 'info@the-agency.org')

    def test_can_parse_locations_under_organization(self):
        self.assertEqual(len(list(self.from_real_data.locations)), 1)
        self.assertEqual(len(list(self.from_minimal_data.locations)), 2)


class LocationParserTests(unittest.TestCase):
    def setUp(self):
        root = etree.fromstring(open(REAL_211_DATA_SET, 'r').read())
        self.organization_id_passed_to_parser = 'the organization id'
        self.from_real_data = parser.parse_site(root.find('Agency/Site'),
                                                self.organization_id_passed_to_parser)
        root = etree.fromstring(MINIMAL_211_DATA_SET)
        self.from_minimal_data = parser.parse_site(root.find('Agency/Site'),
                                                   self.organization_id_passed_to_parser)

    def test_can_parse_name(self):
        self.assertEqual(self.from_real_data.name, 'Langley Child Development Centre')
        self.assertEqual(self.from_minimal_data.name, 'the site name')

    def test_can_parse_description(self):
        self.assertEqual(self.from_real_data.description[:30], 'Provides inclusive, family-cen')
        self.assertEqual(self.from_minimal_data.description, 'the site description')

    def test_can_parse_latitude(self):
        self.assertAlmostEqual(self.from_real_data.spatial_location.latitude, 49.087284)
        self.assertAlmostEqual(self.from_minimal_data.spatial_location.latitude, 123.456)

    def test_can_parse_longitude(self):
        self.assertAlmostEqual(self.from_real_data.spatial_location.longitude, -122.607918)
        self.assertAlmostEqual(self.from_minimal_data.spatial_location.longitude, -154.321)

    def test_sets_the_organization_id(self):
        self.assertEqual(self.from_real_data.organization_id,
                         self.organization_id_passed_to_parser)
        self.assertEqual(self.from_minimal_data.organization_id,
                         self.organization_id_passed_to_parser)


class ServiceParserTests(unittest.TestCase):
    def setUp(self):
        root = etree.fromstring(open(REAL_211_DATA_SET, 'r').read())
        self.organization_id_passed_to_parser = 'the organization id'
        self.site_id_passed_to_parser = 'the site id'
        self.from_real_data = parser.parse_service(
            root.find('Agency/Site/SiteService'),
            self.organization_id_passed_to_parser,
            self.site_id_passed_to_parser
        )
        root = etree.fromstring(MINIMAL_211_DATA_SET)
        self.from_minimal_data = parser.parse_service(
            root.find('Agency/Site/SiteService'),
            self.organization_id_passed_to_parser,
            self.site_id_passed_to_parser
        )

    def test_can_parse_name(self):
        self.assertEqual(self.from_real_data.name, 'Langley Child Development Centre')
        self.assertEqual(self.from_minimal_data.name, 'the service name')

    def test_can_parse_description(self):
        self.assertEqual(self.from_real_data.description[:30], 'Provides inclusive, family-cen')
        self.assertEqual(self.from_minimal_data.description, 'the service description')

    def test_sets_the_organization_id(self):
        self.assertEqual(self.from_real_data.organization_id,
                         self.organization_id_passed_to_parser)
        self.assertEqual(self.from_minimal_data.organization_id,
                         self.organization_id_passed_to_parser)

    def test_sets_the_site_id(self):
        self.assertEqual(self.from_real_data.site_id,
                         self.site_id_passed_to_parser)
        self.assertEqual(self.from_minimal_data.site_id,
                         self.site_id_passed_to_parser)

class AddressParserTests(unittest.TestCase):
    def test_parses_physical_address(self):
        xml_address = '''
            <Site>
                <PhysicalAddress>
                    <Line1>Line1</Line1>
                    <City>City</City>
                    <Country>Country</Country>
                </PhysicalAddress>
            </Site>'''
        root = etree.fromstring(xml_address)
        address_type_id = 'physical_address'
        address = parser.parse_address(root.find('PhysicalAddress'),
                                       a_string(), address_type_id)
        self.assertIsInstance(address, dtos.Address)
        self.assertEqual(address.address_type_id, address_type_id)

    def test_parses_postal_address(self):
        xml_address = '''
            <Site>
                <MailingAddress>
                    <Line1>Line1</Line1>
                    <City>City</City>
                    <Country>Country</Country>
                </MailingAddress>
            </Site>'''
        root = etree.fromstring(xml_address)
        address_type_id = 'postal_address'
        address = parser.parse_address(root.find('MailingAddress'),
                                       a_string(), address_type_id)
        self.assertIsInstance(address, dtos.Address)
        self.assertEqual(address.address_type_id, address_type_id)

    def test_missing_line_1_throws_exception(self):
        xml_address = '''
            <Site>
                <MailingAddress>
                    <City>City</City>
                    <Country>Country</Country>
                </MailingAddress>
            </Site>'''
        root = etree.fromstring(xml_address)
        address_type_id = 'postal_address'
        with self.assertRaisesRegex(MissingRequiredFieldXmlParseException,
                                    'Missing required field: "Line1"'):
            parser.parse_address(root.find('MailingAddress'),
                                 a_string(), address_type_id)

    def test_missing_city_throws_exception(self):
        xml_address = '''
            <Site>
                <MailingAddress>
                    <Line1>Line1</Line1>
                    <Country>Country</Country>
                </MailingAddress>
            </Site>'''
        root = etree.fromstring(xml_address)
        address_type_id = 'postal_address'
        with self.assertRaisesRegex(MissingRequiredFieldXmlParseException,
                                    'Missing required field: "City"'):
            parser.parse_address(root.find('MailingAddress'),
                                 a_string(), address_type_id)

    def test_missing_country_throws_exception(self):
        xml_address = '''
            <Site>
                <MailingAddress>
                    <Line1>Line1</Line1>
                    <City>City</City>
                </MailingAddress>
            </Site>'''
        root = etree.fromstring(xml_address)
        address_type_id = 'postal_address'
        with self.assertRaisesRegex(MissingRequiredFieldXmlParseException,
                                    'Missing required field: "Country"'):
            parser.parse_address(root.find('MailingAddress'),
                                 a_string(), address_type_id)

    def test_address_line_parser_only_parses_lines_one_to_four(self):
        xml_address = '''
            <Site>
                <MailingAddress>
                    <Line1>Line1</Line1>
                    <Line2>Line2</Line2>
                    <Line3>Line3</Line3>
                    <Line4>Line4</Line4>
                    <Line5>Line5</Line5>
                </MailingAddress>
            </Site>'''
        root = etree.fromstring(xml_address)
        address_lines = parser.parse_address_lines(root.find('MailingAddress'))
        self.assertEqual(address_lines, 'Line1\nLine2\nLine3\nLine4')

    def test_address_line_parser_sorts_address_lines(self):
        xml_address = '''
            <Site>
                <MailingAddress>
                    <Line3>Line3</Line3>
                    <Line1>Line1</Line1>
                    <Line2>Line2</Line2>
                </MailingAddress>
            </Site>'''
        root = etree.fromstring(xml_address)
        address_lines = parser.parse_address_lines(root.find('MailingAddress'))
        self.assertEqual(address_lines, 'Line1\nLine2\nLine3')

    def test_address_line_parser_returns_none_when_line_1_is_empty(self):
        xml_address = '''
            <Site>
                <MailingAddress>
                    <Line1 />
                    <Line2>Line2</Line2>
                    <Line3>Line3</Line3>
                </MailingAddress>
            </Site>'''
        root = etree.fromstring(xml_address)
        address_lines = parser.parse_address_lines(root.find('MailingAddress'))
        self.assertEqual(address_lines, None)


class PhoneNumberParserTests(unittest.TestCase):

    def test_parses_all_valid_phone_numbers(self):
        xml = '''
            <Site>
                <Phone TollFree="false" Confidential="false">
                    <PhoneNumber>604-530-5033</PhoneNumber>
                    <Type>Phone1</Type>
                </Phone>
                <Phone TollFree="false" Confidential="false">
                    <PhoneNumber>604-530-5033</PhoneNumber>
                    <Type>Fax</Type>
                </Phone>
            </Site>'''
        root = etree.fromstring(xml)
        site_id = a_string()
        phone_numbers = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(len(phone_numbers), 2)

    def test_does_not_parse_invalid_phone_numbers(self):
        xml = self.build_phone_xml(a_string(), 'Unsupported')
        root = etree.fromstring(xml)
        parsed_phone_numbers = parser.parse_site_phone_number_list(root, a_string())
        self.assertEqual(len(parsed_phone_numbers), 0)

    def test_parses_phone1_phone_number(self):
        self.run_parses_phone_number_for_type_test('Phone1')

    def test_parses_after_hours_phone_number(self):
        self.run_parses_phone_number_for_type_test('After Hours')

    def test_parses_business_line_phone_number(self):
        self.run_parses_phone_number_for_type_test('Business Line')

    def test_parses_hotline_phone_number(self):
        self.run_parses_phone_number_for_type_test('Hotline')

    def test_parses_out_of_area_phone_number(self):
        self.run_parses_phone_number_for_type_test('Out of area')

    def test_parses_fax_phone_number(self):
        self.run_parses_phone_number_for_type_test('Fax')

    def test_convert_to_type_id_replaces_spaces_with_underscores(self):
        strings = [a_string(), a_string()]
        phone_type = ' '.join(strings)
        expected_phone_type_id = '_'.join(strings)
        self.assertEqual(parser.convert_phone_type_to_type_id(phone_type), expected_phone_type_id)

    def test_convert_to_type_id_lowercases(self):
        strings = [a_string(), a_string()]
        phone_type = ' '.join(strings).upper()
        expected_phone_type_id = '_'.join(strings).lower()
        self.assertEqual(parser.convert_phone_type_to_type_id(phone_type), expected_phone_type_id)

    def run_parses_phone_number_for_type_test(self, phone_number_type):
        site_id = a_string()
        phone_number = a_string()
        xml = self.build_phone_xml(phone_number, phone_number_type)
        root = etree.fromstring(xml)
        parsed_phone_number = parser.parse_site_phone_number_list(root, site_id)[0]

        expected_location_id = site_id
        expected_phone_number_type_id = parser.convert_phone_type_to_type_id(phone_number_type)
        expected_phone_number = phone_number

        self.assertIsInstance(parsed_phone_number, dtos.PhoneNumber)
        self.assertEqual(parsed_phone_number.location_id, expected_location_id)
        self.assertEqual(parsed_phone_number.phone_number_type_id, expected_phone_number_type_id)
        self.assertEqual(parsed_phone_number.phone_number, expected_phone_number)

    def build_phone_xml(self, phone_number, phone_number_type):
        return '''
            <Site>
                <Phone TollFree="false" Confidential="false">
                    <PhoneNumber>{}</PhoneNumber>
                    <Type>{}</Type>
                </Phone>
            </Site>'''.format(phone_number, phone_number_type)
