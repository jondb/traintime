try:
  from urllib.request import urlopen
except ImportError:
  from urllib2 import urlopen

import datetime
from lxml import etree

class BartApi():
  def __init__(self, api_key="MW9S-E7SL-26DU-VV8V"):
    self.api_key = api_key

  def parse_response(self,raw_xml):
    if isinstance(raw_xml, bytes):
      parsed_xml = etree.fromstring(raw_xml, parser=etree.XMLParser(encoding='utf-8'))
    else:
      parsed_xml = etree.parse(raw_xml)
    return parsed_xml

  def get_xml(self,url):
    raw_response = urlopen(url)
    xml = self.parse_response(raw_response)
    return xml

  def number_of_trains(self):
    xml = self.get_xml("http://api.bart.gov/api/bsa.aspx?cmd=count&key=%s" % (self.api_key))
    train_count = xml.xpath('traincount')[0].text
    return train_count

  def elevator_status(self):
    xml = self.get_xml("http://api.bart.gov/api/bsa.aspx?cmd=elev&key=%s" % (self.api_key))
    elevator_status = xml.xpath('bsa')[0].xpath('description')[0].text
    return elevator_status

  def system_status(self):
    xml = self.get_xml("http://api.bart.gov/api/bsa.aspx?cmd=bsa&key=%s" % (self.api_key))
    elevator_status = xml.xpath('bsa')[0].xpath('description')[0].text
    return elevator_status

  def get_stations(self):
    xml = self.get_xml("http://api.bart.gov/api/stn.aspx?cmd=stns&key=%s" % (self.api_key))
    stations = xml.find("stations").findall("station")
    station_list = []
    for station in stations:
        station_list.append(dict(((elt.tag,elt.text) for elt in station)))
    return station_list

  def bsa(self, stn="ALL"):
    xml = self.get_xml("http://api.bart.gov/api/stn.aspx?cmd=stninfo&orig=%s&key=%s" % (stn,self.api_key))
    return xml.find(".//description").text

  def station_info(self, station):
    xml = self.get_xml("http://api.bart.gov/api/stn.aspx?cmd=stninfo&orig=%s&key=%s" % (station,self.api_key))
    raw_station = xml.find(".//station")
    return dict(((elt.tag,elt.text) for elt in raw_station))

  def station_access(self, station, legend="1"):
    xml = self.get_xml("http://api.bart.gov/api/stn.aspx?cmd=stnaccess&orig=%s&key=%s&l=%s" % (station,self.api_key,legend))
    return dict(((elt.tag,elt.text) for elt in xml))

  def etd(self, station="ALL", platform=None, direction=None):
    if station == "ALL":
      xml = self.get_xml("http://api.bart.gov/api/etd.aspx?cmd=etd&orig=ALL&key=%s" % (self.api_key))
    elif platform is None:
      xml = self.get_xml("http://api.bart.gov/api/etd.aspx?cmd=etd&orig=%s&direction=%s&key=%s" % (station,direction,self.api_key))
    elif direction is None:
      url = "http://api.bart.gov/api/etd.aspx?cmd=etd&orig=%s&platform=%s&key=%s" % (station,platform,self.api_key)
    else:
      xml = self.get_xml("http://api.bart.gov/api/etd.aspx?cmd=etd&orig=%s&platform=%s&direction=%s&key=%s" % (station,platform,direction,self.api_key))
    raw_etds = xml.findall(".//etd")
    etd_list=[]
    for etd in raw_etds:
        raw_estimates = etd.findall("estimate")
        estimates = []
        for estimate in raw_estimates:
          estimates.append(dict(((elt.tag,elt.text) for elt in estimate)))
        raw_dict = { "destination" : etd.find("destination").text, "abbreviation" : etd.find("abbreviation").text, "estimates" : estimates }
        etd_list.append(raw_dict)
    return etd_list

  def routes(self, sched=None, date="today"):
    if sched is None:
      url = "http://api.bart.gov/api/route.aspx?cmd=routes&date=%s&key=%s" % (date,self.api_key)
    else:
      url = "http://api.bart.gov/api/route.aspx?cmd=routes&sched=%s&key=%s" % (sched,self.api_key)
      
    xml = self.get_xml(url)
    raw_routes = xml.findall(".//route")
    routes = []
    for route in raw_routes:
      routes.append(dict(((elt.tag,elt.text) for elt in route)))
    return routes


  def route_info(self, route="all", sched=None, date="today"):
    if sched is None:
      url = "http://api.bart.gov/api/route.aspx?cmd=routeinfo&route=%s&date=%s&key=%s" % (route,date,self.api_key)
    else:
      url = "http://api.bart.gov/api/route.aspx?cmd=routeinfo&route=%s&sched=%s&date=%s&key=%s" % (route,sched,date,self.api_key)
    print url
    xml = self.get_xml(url)
    raw_route = xml.find(".//route")
    raw_stations = raw_route.findall(".//station")
    route = dict(((elt.tag,elt.text) for elt in raw_route))
    station_list = []
    for station in raw_stations:
        station_list.append(station.text)
    route['config'] = station_list
    return route

  def get_item(self, item_name, xml):
    item_list = xml.findall(".//" + item_name)
    if len(item_list) == 1:
      return [item_list[0].text]
    else:
      list_of_items = []
      for entry in item_list:
          list_of_items.append(entry.text)
      return list_of_items

  def get_holidays(self):
    xml = self.get_xml("http://api.bart.gov/api/route.aspx?cmd=holiday&key=%s" % (self.api_key))
    raw_holidays = xml.findall(".//holiday")
    holiday_list = []
    for holiday in raw_holidays:
      holiday_list.append(dict(((elt.tag,elt.text) for elt in holiday)))
    return holiday_list


  def get_schedules(self):
    xml = self.get_xml("http://api.bart.gov/api/route.aspx?cmd=scheds&key=%s" % (self.api_key))
    raw_schedules = xml.findall(".//schedule")
    schedules = []
    for schedule in raw_schedules:
        id = schedule.get('id')
        effective_date = schedule.get('effectivedate')
        schedules.append({ "id" : id, "effective_date" : effective_date})
    return schedules

  def get_special_schedules(self, legend="1"):
    xml = self.get_xml("http://api.bart.gov/api/stn.aspx?cmd=special&key=%s&l=%s" % (self.api_key,legend))
    schedule_xml = xml.find('.//special_schedule')
    xml_dict = dict(((elt.tag,elt.text) for elt in schedule_xml))
    return xml_dict
  
  def get_station_schedule(self, station):
    xml = self.get_xml("http://api.bart.gov/api/stn.aspx?cmd=stnsched&orig=%s&key=%s" % (station,self.api_key))
    raw_schedules = xml.findall('.//item')
    schedule_list = []
    for item in raw_schedules:
        schedule_dict = { "line" : item.get('line'), "train_head_station" : item.get('trainHeadStation'), "orig_time" : item.get('origTime'), "dest_time" : item.get('destTime'), "train_idx" : item.get('trainIdx'), "bikeflag" : item.get('bikeflag') }
        schedule_list.append(schedule_dict)
    return schedule_list

  def get_route_schedule(self, sched='', date='today', legend="1"):
    if not sched=='':
      xml = self.get_xml("http://api.bart.gov/api/stn.aspx?cmd=special&sched=%s&key=%s&l=%s" % (sched,self.api_key,legend))
    elif sched == '':
      xml = self.get_xml("http://api.bart.gov/api/stn.aspx?cmd=special&date=%s&key=%s&l=%s" % (date,self.api_key,legend))
    raw_routes = xml.findall(".//train")
    trains = {}
    for train in raw_routes:
        stops = {}
        raw_stops = train.findall(".//stop")
        for stop in raw_stops:
            raw_dict = { "orig_time" : stop.get("origTime"), "bikeflags" : stop.get("bikeflag") }
            stops[stop.get("station")] = raw_dict
        trains[train.get("index")] = stops
    return trains

  def get_fare(self, orig, dest):
    xml = self.get_xml("http://api.bart.gov/api/stn.aspx?cmd=fare&orig=%s&dest=%s&key=%s" % (orig,dest,self.api_key))
    raw_fare = xml.find(".//trip")
    fare_dict = { "fare" : raw_fare.find("fare").text, "clipper_fare" : raw_fare.find(".//clipper").text }
    return fare_dict

  def get_departures(self, orig, dest):
    # Use schedule to find all trains that will get you there.
    url = "http://api.bart.gov/api/sched.aspx?cmd=depart&orig=%s&dest=%s&b=0&a=4&key=%s" % (orig,dest,self.api_key)
    xml = self.get_xml(url)
    trips = xml.findall(".//trip")

    first_route = None

    trains = {}
    for trip in trips:
      print trip
      legs = trip.findall(".//leg")
      leg_dest = legs[0].get("trainHeadStation")
      if leg_dest not in trains:
        trains[leg_dest] = {"fare": trip.get("fare"), "arrives": trip.get("destTimeMin")}
        destination, estimates = self.get_estimates_for_train(orig, leg_dest)
        trains[leg_dest]["destination"] = destination
        trains[leg_dest]["departures"] = estimates
        if not first_route:
          first_route = legs[0].get('line').strip("ROUTE ")

    prev_station, next_station = self.get_adjacent_station(route=first_route, orig=orig)

    all_departures = []
    for abbr in trains:
      for departure in trains[abbr]["departures"]:
        departure["fare"] = trains[abbr]["fare"]
        departure["arrives"] = trains[abbr]["arrives"]
        departure["destination"] = trains[abbr]["destination"]
        all_departures.append(departure)

    all_departures = sorted(all_departures, key=lambda x: int(x['minutes']) if x['minutes'].isdigit() else -1)

    # We only know when the first schedule option will arrive at the destination.
    # This removes the ones we don't predict.
    used_arrivals = []
    for departure in all_departures:
      if departure['arrives'] in used_arrivals:
        departure['arrives'] = None
      else:
        used_arrivals.append(departure['arrives'])
    return all_departures, prev_station, next_station

  def get_adjacent_station(self, route, orig):
    """Return the station before and after the current station."""
    stations = self.route_info(route=route)['config']
    for i, stn in enumerate(stations):
      if stn == orig:
        if i == len(stations) -1:
          return stations[i-1], stations[i]
        if i == 0:
          return stations[0], stations[i+1]
        return stations[i-1], stations[i+1]
    return None, None

  def get_estimates_for_train(self, orig, dest):
    est = self.etd(station=orig, direction='ns')
    for direction in est:
        if direction["abbreviation"] == dest:
          return direction["destination"], direction["estimates"]
    return "Not Found"


if __name__ == "__main__":
    bart = BartApi()
    depts = bart.get_departures('WCRK', 'CIVC')
    for dept in depts:
      print "%s mins. %s header" % (dept['minutes'], dept['trainHeadStation'])
