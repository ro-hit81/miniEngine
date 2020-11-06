from django.shortcuts import render

# Create your views here.

from django.views.generic import TemplateView

import folium
from folium import plugins
import ee

ee.Initialize()

class home(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        figure = folium.Figure()

        bands = ['B2', 'B3', 'B4', 'B8', 'B11', 'B12', 'QA60']
        bound = ee.FeatureCollection('users/rhtkhati/Ubon_Boundary')
        def maskS2clouds(image):
            qa = image.select('QA60')
            cloudBitMask = 1 << 10
            cirrusBitMask = 1 << 11
            mask = qa.bitwiseAnd(cloudBitMask).eq(0)
            mask = mask.bitwiseAnd(cirrusBitMask).eq(0)

            return image.updateMask(mask).divide(10000)
        collection = (ee.ImageCollection("COPERNICUS/S2")
                    .select(bands)
                    .filter(ee.Filter.date('2019-01-01', '2019-03-31'))
                    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 1))
                    .map(maskS2clouds)
                    )
        def add_ee_layer(self, eeImageObject, visParams, name):
            mapID = ee.Image(eeImageObject).getMapId(visParams)
            folium.TileLayer(
                tiles = mapID['tile_fetcher'].url_format,
                attr = "Map Data © Google Earth Engine",
                name = name,
                overlay = True,
                control = True
            ).add_to(self)
        folium.Map.add_ee_layer = add_ee_layer
        image = collection.sort('system:index', opt_ascending=False).mosaic()
        image = image.clip(bound)
        visParams1 = {'bands': ["B4","B3","B2"],
                    'max': 0.4,
                    'min': 0
                        }
        visParams2 = {'bands': ["B11","B8","B3"],
                    'max': 0.4,
                    'min': 0
                        }
        visParams3 = {'bands': ["B8","B4","B3"],
                    'max': 0.4,
                    'min': 0,
                        }              

        myMap = folium.Map(location = [15.2448, 105.1], zoom_start = 12)
        myMap.add_ee_layer(image, visParams1, 'True_Color')
        myMap.add_ee_layer(image, visParams3, 'False_Color')
        myMap.add_ee_layer(image, visParams2, 'Natural_Infrared')
        myMap.add_child(folium.LayerControl())
        myMap.add_to(figure)
        figure.render()

        return{"map": figure}