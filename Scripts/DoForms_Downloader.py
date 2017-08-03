import csv,urllib,os,arcpy
inputCSV = arcpy.GetParameterAsText(0)
outputFolder = arcpy.GetParameterAsText(1)
shpfile = arcpy.GetParameterAsText(2)
imgFd = 'Images'
shpFd = 'Shapefile'
latlng = ['POINT Latitude','POINT Longitude']
msgs = ["Creating Image Directory","Shapefile Process Initiated","Processing Shapefile","Starting Photo Download...","Shapefile Cleaning Up","Images and Shapefile process completed","Problem with Lat/lng fields in csv file","Lat/Lng fields Checked"]
spatialreference = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119522E-09;0.001;0.001;IsHighPrecision"
fields = ["PHOTO1","PHOTO2","SC_PHOTO1","SC_PHOTO2","OF_NM"]
delFields = ['Record_Nam','Status','Point_Alti','Point_Accu']
with open(inputCSV, "rb") as f:
    reader = csv.reader(f)
    i = reader.next()
csvFields = set(i)
for field in latlng:
	if field in csvFields:
		arcpy.AddMessage(msgs[7])
	else:
		arcpy.AddWarning(msgs[6])

fullShpfile = outputFolder+"/"+shpFd+"/"+shpfile
if not os.path.exists(outputFolder+'/'+imgFd):
	arcpy.AddMessage(msgs[0])
	os.makedirs(outputFolder+'/'+imgFd)
upJ = "_UP.jpg"
dnJ = "_DOWN.jpg"
shp = '.shp'
try:
	arcpy.AddMessage(msgs[1])
	temp_path = os.path.join('in_memory', 'tempShpLyr')
	if not os.path.exists(outputFolder+'/'+shpFd):
		os.makedirs(outputFolder+'/'+shpFd)
	arcpy.AddMessage(msgs[2])
	evt_lyr = arcpy.MakeXYEventLayer_management(inputCSV, latlng[1], latlng[0], temp_path, spatialreference)
	arcpy.CopyFeatures_management(evt_lyr, fullShpfile)
except Exception as err:
	print err.args[0]
	print arcpy.GetMessages()
try:
	arcpy.AddMessage(msgs[3])
	totalrecord = int(arcpy.GetCount_management(fullShpfile+shp).getOutput(0))*2
	i = 1
	with arcpy.da.UpdateCursor(fullShpfile+shp, fields) as cursor:
		for row in cursor:
			arcpy.AddMessage("Downloading Photo {0} & {1} / {2}".format(i,i+1, totalrecord))
			i+=2
			if len(row[0]) > 1:
				outputPhotos = "./"+imgFd+"/TPIC_" + row[4] + upJ
				urllib.urlretrieve (row[0], outputFolder + os.sep + outputPhotos)
				row[0] = outputPhotos
			if len(row[1]) > 1:
				outputPhotos =  "./"+imgFd+"/TPIC_" + row[4] + dnJ
				urllib.urlretrieve (row[1], outputFolder + os.sep + outputPhotos)
				row[1] = outputPhotos
			if len(row[2]) > 1:
				outputPhotos =  "./"+imgFd+"/SC_TPIC_" + row[4] + upJ
				urllib.urlretrieve (row[2], outputFolder + os.sep + outputPhotos)
				row[2] = outputPhotos
			if len(row[3]) > 1:
				outputPhotos =  "./"+imgFd+"/SC_TPIC_" + row[4] + dnJ
				urllib.urlretrieve (row[3], outputFolder + os.sep + outputPhotos)
				row[3] = outputPhotos
			cursor.updateRow(row)
except Exception as err:
	print err.args[0]
	print arcpy.GetMessages()
try:
	arcpy.AddMessage(msgs[4])
	arcpy.DeleteField_management (fullShpfile+shp, delFields[0])
	arcpy.DeleteField_management (fullShpfile+shp, delFields[1])
	arcpy.DeleteField_management (fullShpfile+shp, delFields[2])
	arcpy.DeleteField_management (fullShpfile+shp, delFields[3])
except Exception as err:
	print err.args[0]
	print arcpy.GetMessages()
arcpy.AddMessage(msgs[5])
