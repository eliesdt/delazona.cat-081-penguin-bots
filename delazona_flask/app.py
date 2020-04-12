import os
import json
import uuid
import time
import requests

from flask import Flask, request, render_template, redirect, session, Response, jsonify

import unicodedata
from googlesearch import search
from arcgis.gis import GIS
from arcgis.geocoding import geocode
from geopy.distance import geodesic
from bs4 import BeautifulSoup

#from fuzzywuzzy import fuzz, process

# CREDENTIALS NEEDED (IN CASE SORTING BY DISTANCE IS DESIRED)
GIS_USERNAME = ""
GIS_PASSWORD = ""

if GIS_USERNAME and GIS_PASSWORD:
	gis = GIS("http://www.arcgis.com", GIS_USERNAME, GIS_PASSWORD)
	print('inside gis')

from dbhelper import DBHelper

FORM_CATEGORIES_MAPPING = {
	'Cine, TV i Música': '1',
	'Electrònica': '2',
	'Informàtica i Oficina': '3',
	'Videojocs': '4',
	'Joguines i Bebè': '5',
	'Llar, Jardí, Bricolatge i Mascotes': '6',
	'Alimentació i Begudes': '7',
	'Bellesa i Salut': '8',
	'Moda': '9',
	'Esports i Aire Lliure': '10',
	'Cotxe i Moto': '11',
	'Indústria, Empreses i Ciència': '12'
}

AMAZON_CATEGORIES_MAPPING = {
	'1': ['Todo en Cine y TV','Series TV','Blu-ray','CDs y vinilos','Amazon Music Unlimited','Música digital','Instrumentos musicales'],
	'2': ['Fotografía y videocámaras', 'Móviles y telefonía', 'TV, Vídeo y Home Cinema', 'Audio y Hi-Fi', 'GPS', 'Instrumentos musicales', 'Accesorios de electrónica', 'Informática', 'Hogar Digital', 'Amazon Renewed', 'Todo en Electrónica'],
	'3': ['Portátiles', 'Tablets', 'Sobremesas', 'Monitores', 'Componentes', 'Accesorios de informática', 'Impresoras y tinta', 'Software', 'Gaming Store', 'Juegos para PC', 'Todo en Informática', 'Material de oficina', 'Papel', 'Bolígrafos y material de escritura', 'Electrónica de oficina', 'Todo en Oficina y papelería'],
	'4': ['Todo en Videojuegos', 'Consolas y accesorios', 'Juegos para PC', 'Merchandising', 'Infantil'],
	'5': ['Juguetes y juegos', 'Bebé', 'Lista de Nacimiento', 'Amazon Familia', 'Amazon Kids'],
	'6': ['Cocina y comedor', 'Dormitorio y salón', 'Baño', 'Jardín', 'Iluminación', 'Pequeño electrodoméstico', 'Aspiración, limpieza y planchado', 'Almacenamiento y organización', 'Climatización y calefacción', 'Todo en Hogar y cocina', 'Chollos', 'Descubre tu estilo', 'Explorar Showroom', 'Herramientas de bricolaje', 'Hogar Digital', 'Herramientas de jardinería', 'Instalación eléctrica', 'Fontanería de baño y cocina', 'Seguridad y prevención', 'Todo en Bricolaje y herramientas', 'Todo para mascotas', 'Perfiles de mascota'],
	'7': ['Alimentación y bebidas', 'Bebidas alcohólicas', 'Productos eco', 'Alimentación y Vinos de España', 'Pantry'],
	'8': ['Belleza', 'Belleza Luxury', 'Dermocosmética', 'Belleza masculina', 'Cosmética Natural', 'Salud y cuidado personal', 'Limpieza del hogar', 'Pantry'],
	'9': ['Mujer', 'Hombre', 'Niña', 'Niño', 'Bebé', 'The Drop', 'Bolsos', 'Joyería', 'Relojes', 'Equipaje', 'Outlet', 'Chollos'],
	'10': ['Running', 'Fitness y ejercicio', 'Ciclismo', 'Tenis y pádel', 'Golf', 'Deportes de equipo', 'Deportes acuáticos', 'Deportes de invierno', 'Acampada y senderismo', 'Tienda de Yoga', 'Movilidad urbana', 'Todo en Deportes', 'Ropa deportiva', 'Calzado deportivo', 'GPS y electrónica'],
	'11': ['Accesorios y piezas para coche', 'Herramientas y equipos', 'GPS', 'Accesorios y piezas para moto'],
	'12': ['Todo en Industria, empresas y ciencia', 'Laboratorio', 'Limpieza', 'Seguridad']
}

app = Flask(__name__, static_url_path='/static')

db = DBHelper()
db.setup()

DEPLOYED = True

if DEPLOYED:
	BASE_URL = 'https://delazona.herokuapp.com'
else:
	BASE_URL =  'https://5ae6b60b.ngrok.io'

JSON_DATA = {}

def populate_db_with_datasets():
	global JSON_DATA
	with open('data.txt') as json_file:
		print('data.txt opened')
		JSON_DATA = json.load(json_file)
		print('json_data loaded')
		#db.add_dataset('barcelona-shops',json_data)
		#print('dataset added')

populate_db_with_datasets()

URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/62fb990e-4cc3-457a-aea1-497604e15659/resource/495c434e-b005-416e-b760-dc79f56dff3a/download/2019_censcomercialbcn_detall.geojson'

def name_similarity(target,slug):
	ratio = fuzz.ratio(target.lower(),slug.lower())
	partial_ratio = fuzz.partial_ratio(target.lower(),slug.lower())
	if ratio > 90:
		print('ratio: {}'.format(ratio))
		print('partial: {}'.format(partial_ratio))
		return True
	return False

def match_with_targets(targets,slug):
	closest_match = process.extract(slug,targets,scorer=fuzz.ratio,limit=1)
	if closest_match[0][1] > 95:
		print('closest_match for {} is {}'.format(slug, closest_match))
		return closest_match[0][0]
	return False

def get_price(url):
	response = requests.get(url)
	soup = BeautifulSoup(response.content,'lxml')
	#print(soup.get_text())

	prices = []
	old_prices = []
	for EachPart in soup.select('div[class*="price"]'):
		print(EachPart.get_text())
		price = unicodedata.normalize("NFKD",EachPart.get_text()).strip().split(' ')[0]
		if price.isdigit():
			if "old-price" not in str(EachPart):
				print(str(EachPart) + '\n')
				if price not in prices:
					prices.append(price)
			else:
				old_prices.append(price)
	for EachPart in soup.select('span[class*="price"]'):
		print(EachPart.get_text())
		price = unicodedata.normalize("NFKD",EachPart.get_text()).strip().split(' ')[0]
		if price.isdigit():
			if "old-price" not in str(EachPart):
				print(str(EachPart) + '\n')
				if price not in prices:
					prices.append(price)
			else:
				old_prices.append(price)
	prices = [price for price in prices if price not in old_prices]
	print(prices)

	if prices:
		return(prices[0])
	else:
		return("")

def remove_duplicates(result):
	urls = []
	data = []
	for entry in result:
		url = entry['url']
		if url not in urls:
			print('{} not in existing urls'.format(url))
			data.append(entry)
			urls.append(url)
	#print(data)
	return data

def match_amazon_categories(category):
	for key, values in AMAZON_CATEGORIES_MAPPING.items():
		for value in values:
			if category.replace(' ','').lower() in value.replace(' ','').lower():
				print('CATEGORY FOUND! {}'.format(value))
				return key

def get_postcode_coordinates(postcode):
	geocode_fs = geocode(address="{}, Catalunya".format(postcode),
						out_fields="Place_addr",
						max_locations=1,
						as_featureset=False)
	latitude = geocode_fs[0]['location']['y']
	longitude = geocode_fs[0]['location']['x']
	#print(latitude,longitude)
	return latitude,longitude

def sort_by_location(request_id,postcode,result):
	latitude, longitude = get_postcode_coordinates(postcode)
	print('result: {}'.format(result))
	for entry in result:
		entry_latitude = entry['latitude']
		entry_longitude = entry['longitude']
		dist = geodesic((latitude,longitude),(entry_latitude,entry_longitude)).km
		entry['dist'] = dist

	result = sorted(result, key=lambda k: k['dist'])
	#db.update_entry(request_id,'result',result)

	return result

def get_google_results(query):
	pages = []
	urls = []
	domains = []
	BLACKLIST_PAGES = ['amazon','idealo','mediamarkt','elcorteingles','mediamarkt','fnac','']

	for result in search(query,        # The query you want to run
					tld = 'com',  # The top level domain
					lang = 'en',  # The language
					num = 10,     # Number of results per page
					start = 0,    # First result to retrieve
					stop = 10,  # Last result to retrieve
					pause = 2.0,  # Lapse between HTTP requests
				   ):
		print(result)
		domain = result.split('//')[1].split('/')[0]
		if domain not in domains:
			domains.append(domain)
			domain = domain.split('.')
			page = ""
			if len(domain) > 2:
				page = domain[1]
			elif len(domain) == 2:
				page = domain[0]
			else:
				print('Error parsing domain: {}'.format(domain))
			if page not in BLACKLIST_PAGES:
				pages.append(page)
				urls.append(result)

	return pages, urls

def match_database(targets,urls,time_init):
	print('starting to retrieve the data:')

	results = []
	#json_data = db.get_dataset('barcelona-shops')[0]
	json_data = JSON_DATA
	for shop in json_data['features']:
		result = {}
		slug = shop['properties']['Nom_Local'].lower().replace(' ','')
		'''
		if name_similarity(target,slug):
			#print(shop)
			print(shop['properties']['Nom_Local'])
		'''
		'''
		match = match_with_targets(targets,slug)
		if match:
			for url in urls:
				if match in url:
					result['name'] = shop['properties']['Nom_Local'].title()
					result['url'] = url
					if shop['properties']['Nom_Via'].split(' ')[0] in ["RDA","PL","PTGE","PG","VIA","RBLA","AV","G.V."]:
						result['address'] = shop['properties']['Nom_Via'].title() + ', ' + shop['properties']['Num_Policia_Inicial'] + ', Barcelona, Catalunya'
					else:
						result['address'] = "Carrer " + shop['properties']['Nom_Via'].title() + ', ' + shop['properties']['Num_Policia_Inicial'] + ', Barcelona, Catalunya'
					result['address_url'] = ('http://maps.google.com/?q=' + result['name'] + '+' + result["address"]).replace(', Barcelona, Catalunya','').replace(' ','+').replace(',','')
					result['latitude'] = shop['properties']['Latitud']
					result['longitude'] = shop['properties']['Longitud']
					result['price'] = "30€"
					results.append(result)
					time2 = time.time() - time_init
					print("time after result found #{}: {}".format(len(results),time2))
					break
		'''
		for i in range(len(targets)):
			if slug == targets[i]:
				result['name'] = shop['properties']['Nom_Local'].title()
				result['url'] = urls[i]
				if shop['properties']['Nom_Via'].split(' ')[0] in ["RDA","PL","PTGE","PG","VIA","RBLA","AV","G.V."]:
					result['address'] = shop['properties']['Nom_Via'].title() + ', ' + shop['properties']['Num_Policia_Inicial'] + ', Barcelona, Catalunya'
				else:
					result['address'] = "Carrer " + shop['properties']['Nom_Via'].title() + ', ' + shop['properties']['Num_Policia_Inicial'] + ', Barcelona, Catalunya'
				result['address_url'] = ('http://maps.google.com/?q=' + result['name'] + '+' + result["address"]).replace(', Barcelona, Catalunya','').replace(' ','+').replace(',','')
				result['latitude'] = shop['properties']['Latitud']
				result['longitude'] = shop['properties']['Longitud']
				#result['price'] = get_price(urls[i])
				results.append(result)
				time2 = time.time() - time_init
				print("time after result found #{}: {}".format(len(results),time2))
				break

	if results:
		request_id = str(uuid.uuid4())
		return request_id, results

	else:
		return False, False

def get_nearby_stores(category,postcode):
	try:
		results = []
		for store in json.loads(db.get_stores(category)):
			store = store[0]
			print(store)
			if store['postcode'] == postcode:
				print('hey 2')
				result = {}
				result['name'] = store['name'].title()
				result['url'] = store['url']
				result['address'] = store['street'] + ', ' + store['number'] + ', ' + store['city'] + ' (' + store['postcode'] + ')'
				result['address_url'] = ('http://maps.google.com/?q=' + result['name'] + '+' + result["address"]).replace(', Barcelona, Catalunya','').replace(' ','+').replace(',','')
				results.append(result)

		if results:
			return results
		else:
			return []
	except Exception as e:
		print('No nearby stores found')
		print(e)
		return []

@app.route('/result/<id>', methods=['GET'])
def render_result(id):
	result = json.loads(db.get_result(id))
	print(result)
	product_name = result["product_name"]
	if len(product_name.split()) > 5:
		product_name = ' '.join(product_name.split()[0:5]) + '...'
	if result["category"]:
		category = list(FORM_CATEGORIES_MAPPING.keys())[list(FORM_CATEGORIES_MAPPING.values()).index(result["category"])]
	else:
		category = ""
	matches = result["results"]
	nearby = result["nearby"]
	return render_template('response.html', product_name=product_name, category=category, results=matches, nearby=nearby)

@app.route('/request', methods=['GET','POST'])
def process_request():
	time_init = time.time()
	product_name = request.args['product_name'].split(' ')[0:7]
	product_name = ' '.join(product_name)
	print(product_name)
	print(request.args)
	if 'category' in request.args:
		category = request.args['category']
		category = match_amazon_categories(category)
		if not category:
			category = ""	
	else:
		category = ""
	if 'cp' in request.args:
		postcode = request.args['cp']
		print(postcode)
	else:
		postcode = ""

	pages, urls = get_google_results('{} comprar Barcelona'.format(product_name))
	request_id, results = match_database(pages,urls,time_init)
	
	if category and postcode:
		print('inside if')
		print(category)
		nearby_category_stores = get_nearby_stores(category,postcode)
		print('nearby category stores: {}'.format(nearby_category_stores))
	else:
		nearby_category_stores = []

	if postcode.isdigit() and results and gis:
		results = sort_by_location(request_id,postcode,results)

	results = remove_duplicates(results)

	result = {"product_name": product_name,
			  "category": category,
			  "results": results,
			  "nearby": nearby_category_stores}
	print('result')
	print(result)
	db.add_result(request_id,result)

	time2 = time.time() - time_init
	print("time after match_database: {}".format(time2))

	response = {}
	if request_id:
		response['response'] = True
		response['url'] = '{}/result/{}'.format(BASE_URL,request_id)
	else:
		response['response'] = False
	print(response)
	response = jsonify(response)
	print('response is {}:'.format(response))
	response.headers.add('Access-Control-Allow-Origin', '*')
	total_time = time.time() - time_init
	print(total_time)
	print(response)
	return response

@app.route('/register', methods=['GET','POST'])
def shop_registration():
	if request.method == "POST":
		data = {}
		data['name'] = request.form['name']
		data['url'] = request.form['website']
		data['phone'] = request.form['phone']
		data['street'] = request.form['street']
		data['number'] = request.form['number']
		data['postcode'] = request.form['postcode']
		data['city'] = request.form['city']
		data['category'] = request.form['category']
		data['delivery'] = request.form.get('delivery')

		print(data)
		db.add_store(FORM_CATEGORIES_MAPPING[request.form['category']],data)

		return render_template('success.html')
	return render_template('form.html')

@app.route('/', methods=['GET','POST'])
def main():
	return render_template('index.html')

if __name__ == '__main__':
	app.run(host="0.0.0.0", debug=True, port=int(os.environ.get("PORT", 8888)), use_reloader=False)