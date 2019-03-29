from botocore.vendored import requests
import boto3, botocore, json
import logging, traceback, os
import socket, struct

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def getDebug():
	try:
		d = os.environ['debug']
		if d == 'True':
			return True
		else:
			return False
	except:
		return False

def getAWSips(services, regions):
	ip_ranges = requests.get('https://ip-ranges.amazonaws.com/ip-ranges.json').json()['prefixes']
	ips = [item['ip_prefix'] for item in ip_ranges if item["service"] in services and item["region"] in regions]
	if len(ips) > getLimit():
		logger.info('AWSviaNATGW Lambda - Warning - number of entries greater than limit of ' + str(getLimit()) + ' only using first ' + str(getLimit()) + ' routes')
		ips = ips[:getLimit()]
	return ips

def getRegion():
	try:
		r = os.environ['AWS_REGION']
		return r
	except:
		logger.info('AWSviaNATGW Lambda - Error - Could not retreive environment variable AWS_REGION')
		return 'error'


def getLimit():
	try:
		return int(os.environ['AWSRouteLimit'],10)
	except:
		logger.info('AWSviaNATGW Lambda - Error - Could not retreive environment variable AWSRouteLimit. Setting to default of 25.')
		return 25
		
def getIgnore():
	try:
		i = os.environ['IgnoreRoutes']
		ignore = i.split()
		return ignore
	except:
		return []
		
def getServices():
	try:
		s = os.environ['AWSservices']
		services = s.split()
		return services
	except:
		logger.info('AWSviaNATGW Lambda - Error - Could not retreive environment variable AWSservices.')
		return []

def getRegions():
	try:
		region = getRegion()
		r = os.environ['AWSregions']
		regions = r.split()
		if region in regions:
			regions.remove(region)
		return regions
	except:
		logger.info('AWSviaNATGW Lambda - Error - Could not retreive environment variable AWSregions.')
		return []

def getVPCids():
	try:
		v = os.environ['AWSvpcids']
		vpcids = v.split()
		return vpcids
	except:
		logger.info('AWSviaNATGW Lambda - Error - Could not retreive environment variable AWSvpcids.')
		return []

def compare(routes1, routes2):
	routes2 = set(routes2)
	return [item for item in routes1 if item not in routes2]


def lambda_handler(event, context):
	if getDebug(): logger.info('AWSviaNATGW Lambda - Debug - Start with Debugging enabled')
	if getDebug(): logger.info('AWSviaNATGW Lambda - Debug - Event: ' + str(event))
	try:
		if getDebug(): logger.info('AWSviaNATGW Lambda - Debug - Get information')
		region     = getRegion()
		account    = event['account']
		session    = boto3.Session(region_name=region)
		ec2        = session.client('ec2')
		AWSvpcids  = getVPCids()
		regions    = getRegions()
		services   = getServices()
		new_routes = getAWSips(services, regions)
		ignore     = getIgnore()
		limit      = getLimit()
		filters    = [{'Name': 'vpc-id', 'Values': AWSvpcids}]
		routes     = ec2.describe_route_tables(Filters=filters)
		logger.info('AWSviaNATGW Lambda - Info [region, account, AWSvpcids, New Routes, Route Limit]: ' + str(region) + ' ' + str(account) + ' ' + str(AWSvpcids) + ' ' + str(new_routes) + ' ' + str(limit))
		
		if getDebug(): logger.info('AWSviaNATGW Lambda - Debug - Start Loop')
		for i in range(0, len(routes['RouteTables'])):
			routes_dict = routes['RouteTables'][i]['Routes']
			if getDebug(): logger.info('AWSviaNATGW Lambda - Debug - routes dictionary: ' + str(routes_dict))
			route_table_id = routes['RouteTables'][i]['RouteTableId']
			if getDebug(): logger.info('AWSviaNATGW Lambda - Debug - route table ID: ' + str(route_table_id))
			existing_cidrs = []
			nat_gw_id = ''
			for y in range(0, len(routes_dict)):
				if getDebug(): logger.info('AWSviaNATGW Lambda - Debug - routes_dict[' + str(y) + ']: ' + str(routes_dict[y]))
				if 'DestinationPrefixListId' not in routes_dict[y]:
					if routes_dict[y]['Origin'] == "CreateRoute":
						if 'NatGatewayId' in routes_dict[y]:
							nat_gw_id = routes_dict[y]['NatGatewayId']
							if getDebug(): logger.info('AWSviaNATGW Lambda - Debug - NAT Gateway ID: ' + str(nat_gw_id))
							route = routes_dict[y]['DestinationCidrBlock']
							existing_cidrs.append(route)
							if route not in new_routes and route not in ignore:
								if getDebug(): logger.info('AWSviaNATGW Lambda - Debug - routes_dict[' + str(y) + '][DestinationCidrBlock]: ' + str(routes_dict[y]['DestinationCidrBlock']))
								try:
									ec2.delete_route(
										DestinationCidrBlock=route,
										DryRun=False,
										RouteTableId=route_table_id
									)
									logger.info('AWSviaNATGW Lambda - Info Deleted Route ' + str(route) + ' in rotuing table ' + str(route_table_id))
								except:
									logger.info('AWSviaNATGW Lambda - Error Deleting Route ' + str(route) + ' in rotuing table ' + str(route_table_id))
									logger.info('AWSviaNATGW Lambda - Error Deleting Route Detail ' + traceback.format_exc())
			
			new_routes_final = compare(new_routes, existing_cidrs)
			if getDebug(): logger.info('AWSviaNATGW Lambda - Debug - Existing Routes: ' + str(existing_cidrs))
			if getDebug(): logger.info('AWSviaNATGW Lambda - Debug - New Routes to add: ' + str(new_routes_final))

			if nat_gw_id != "":
				for route in new_routes_final:
					try:
						ec2.create_route(
							DestinationCidrBlock=route,
							DryRun=False,
							NatGatewayId=nat_gw_id,
							RouteTableId=route_table_id,
						)
						logger.info('AWSviaNATGW Lambda - Info Added Route ' + str(route) + ' in rotuing table ' + str(route_table_id))
					except:
						logger.info('AWSviaNATGW Lambda - Error Adding Route ' + str(route) + ' in rotuing table ' + str(route_table_id))
						logger.info('AWSviaNATGW Lambda - Error Adding Route Detail ' + traceback.format_exc())
			else:
				if getDebug(): logger.info('AWSviaNATGW Lambda - Debug - No NAT Gateway found for route table ' + str(route_table_id))
		if getDebug(): logger.info('AWSviaNATGW Lambda - Debug - End Loop')
	except:
		logger.info('AWSviaNATGW Lambda - Error ' + traceback.format_exc())