from owslib.wms import WebMapService
print("connection...")
wms = WebMapService('http://wms.vsegei.ru/rasters/wms?', version='1.1.1')
print("type:", wms.identification.type)
print("version", wms.identification.version)
print("title", wms.identification.title)
print(list(wms.contents)[:10])
print("title", wms['L94'].title)
print("box", wms['L94'].boundingBoxWGS84)
print("crsOptions", wms['L94'].crsOptions)
print("Styles", wms['L94'].styles)

print("Operations:")
print([op.name for op in wms.operations])

print("GetMap:")
print("Methods get:", wms.getOperationByName('GetMap').methods)
print("Get format:", wms.getOperationByName('GetMap').formatOptions)
print("query:", wms['L94'].queryable)
print("opaq", wms['L94'].opaque)

print("\nGetCapabilities:")
print("Methods get:", wms.getOperationByName('GetCapabilities').methods)
print("Get format:", wms.getOperationByName('GetCapabilities').formatOptions)
print("query:", wms['L94'].queryable)
print("opaq", wms['L94'].opaque)

print("\nGetFeatureInfo:")
print("Methods get:", wms.getOperationByName('GetFeatureInfo').methods)
print("Get format:", wms.getOperationByName('GetFeatureInfo').formatOptions)
print("query:", wms['L94'].queryable)
print("opaq", wms['L94'].opaque)

print("\nDescribeLayer:")
print("Methods get:", wms.getOperationByName('DescribeLayer').methods)
print("Get format:", wms.getOperationByName('DescribeLayer').formatOptions)
print("query:", wms['L94'].queryable)
print("opaq", wms['L94'].opaque)

print("\nGetLegendGraphic:")
print("Methods get:", wms.getOperationByName('GetMap').methods)
print("Get format:", wms.getOperationByName('GetMap').formatOptions)
print("query:", wms['L94'].queryable)
print("opaq", wms['L94'].opaque)

print("\nGetStyles:")
print("Methods get:", wms.getOperationByName('GetStyles').methods)
print("Get format:", wms.getOperationByName('GetStyles').formatOptions)

img = wms.getmap(layers=['L94'],
                 styles=['default'],
                srs='EPSG:4326',
                bbox=(27.0, 45.061, 33.0, 48.0),
                size=(2000, 2000),
                format='image/jpeg',
                transparent=True
                )
out = open('L94.jpg', 'wb')
out.write(img.read())
out.close()

response = wms.getOperationByName()

out = open('L94_legend.jpg', 'wb')
out.write(response.read())
out.close()

"""
GetMap:
Methods get: [{'type': 'Get', 'url': 'http://wms.vsegei.ru/rasters/wms?'}, {'type': 'Post', 'url': 'http://wms.vsegei.ru/rasters/wms?'}]
Get format: ['image/png', 'image/jpeg', 'image/png; mode=8bit', 'application/x-pdf', 'image/svg+xml', 'image/tiff', 'application/vnd.google-earth.kml+xml', 'application/vnd.google-earth.kmz']        
query: 1
opaq 0

GetLegendGraphic:
Methods get: [{'type': 'Get', 'url': 'http://wms.vsegei.ru/rasters/wms?'}, {'type': 'Post', 'url': 'http://wms.vsegei.ru/rasters/wms?'}]
Get format: ['image/png', 'image/jpeg', 'image/png; mode=8bit', 'application/x-pdf', 'image/svg+xml', 'image/tiff', 'application/vnd.google-earth.kml+xml', 'application/vnd.google-earth.kmz']        
query: 1
opaq 0
"""