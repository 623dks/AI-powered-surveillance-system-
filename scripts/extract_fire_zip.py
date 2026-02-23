import zipfile
src = r"C:\Users\Lenovo\Downloads\Fire Detection.v1i.yolov8.zip"
dst = r"C:\Users\Lenovo\Documents\surveillance-system\fire_detection_dataset"
print('Extracting', src, '->', dst)
with zipfile.ZipFile(src,'r') as z:
    z.extractall(dst)
print('Done')
